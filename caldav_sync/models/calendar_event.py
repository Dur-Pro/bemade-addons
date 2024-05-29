import uuid
from odoo import models, api, fields
import caldav
import logging
from datetime import datetime, timezone
from icalendar import Calendar, Event, vCalAddress, vText, vWeekday
from bs4 import BeautifulSoup
from datetime import timedelta
import re
from pytz import timezone, utc

_logger = logging.getLogger(__name__)

WEEKDAY_MAP = {
    0: "MO",
    1: "TU",
    2: "WE",
    3: "TH",
    4: "FR",
    5: "SA",
    6: "SU",
}


def _parse_rrule_string(rrule_str):
    def try_to_int(part):
        try:
            return int(part)
        except Exception:
            return part

    regex_str = "RRULE:(.*)$"
    regex = re.compile(regex_str)
    params_match = regex.search(rrule_str)
    params_part = params_match.groups()[0]
    params = params_part.split(';')
    params_dict = {}
    for param in params:
        parts = param.split('=')
        params_dict.update({parts[0]: try_to_int(parts[1])})
    return params_dict


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    caldav_uid = fields.Char(string='CalDAV UID', readonly=True)
    caldav_recurrence_id = fields.Char(string='CalDAV Recurrence ID', readonly=True)

    @api.model
    def create(self, vals):
        if not vals.get('caldav_uid'):
            vals['caldav_uid'] = str(uuid.uuid4())
        event = super(CalendarEvent, self).create(vals)
        if not self.env.context.get('caldav_no_sync'):
            try:
                _logger.debug(f"Creating event {event.name} in CalDAV")
                event.sync_create_to_caldav()
            except Exception as e:
                _logger.error(f"Failed to create event in CalDAV server: {e}")
        return event

    def write(self, vals):
        res = super(CalendarEvent, self).write(vals)
        if not self.env.context.get('caldav_no_sync') and self.ids:
            for rec in self:
                try:
                    _logger.debug(f"Updating event {self.name} in CalDAV")
                    rec.sync_update_to_caldav()
                except Exception as e:
                    _logger.error(f"Failed to update event in CalDAV server: {e}")
        return res

    def unlink(self):
        if not self.env.context.get('caldav_no_sync'):
            for event in self:
                try:
                    _logger.debug(f"Removing event {event.name} from CalDAV")
                    event.sync_remove_from_caldav()
                except Exception as e:
                    _logger.error(f"Failed to delete event from CalDAV server: {e}")
        return super(CalendarEvent, self).unlink()

    def _is_caldav_enabled(self):
        return self.env.user.is_caldav_enabled()

    def _get_caldav_client(self):
        user = self.env.user
        return caldav.DAVClient(
            url=user.caldav_calendar_url,
            username=user.caldav_username,
            password=user.caldav_password
        )

    def sync_create_to_caldav(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(url=self.env.user.caldav_calendar_url)
        for event in self:
            ical_event = event._get_icalendar()
            try:
                _logger.debug(f"Creating new CalDAV event for {event.name}")
                caldav_event = calendar.add_event(ical_event)
                caldav_uid = caldav_event.vobject_instance.vevent.uid.value
                _logger.debug(f"New CalDAV UID: {caldav_uid}")
                event.with_context(caldav_no_sync=True).write({'caldav_uid': caldav_uid})
            except Exception as e:
                _logger.error(f"Failed to sync event to CalDAV server: {e}")

    def sync_update_to_caldav(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(url=self.env.user.caldav_calendar_url)
        for event in self:
            ical_event = event._get_icalendar()
            try:
                _logger.debug(f"Updating existing CalDAV event {event.caldav_uid}")
                calendar.save_event(ical=ical_event)
            except Exception as e:
                _logger.error(f"Failed to sync event to CalDAV server: {e}")

    def sync_remove_from_caldav(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(url=self.env.user.caldav_calendar_url)
        for event in self:
            if event.caldav_uid:
                try:
                    _logger.debug(f"Removing CalDAV event {event.caldav_uid}")
                    caldav_event = calendar.object_by_uid(event.caldav_uid)
                    caldav_event.delete()
                except caldav.error.NotFoundError:
                    _logger.warning(f"CalDAV event {event.caldav_uid} not found on server.")
                except Exception as e:
                    _logger.error(f"Failed to remove event from CalDAV server: {e}")

    def _get_icalendar(self):
        calendar = Calendar()
        calendar.add('prodid', '-//Odoo//mxm.dk//')
        calendar.add('version', '2.0')

        for event in self:
            user_tz = timezone('UTC')
            if event.user_id.tz:
                user_tz = timezone(event.user_id.tz)
            ical_event = Event()
            ical_event.add('uid', event.caldav_uid)
            ical_event.add('dtstamp', utc.localize(event.write_date).astimezone(user_tz))
            if event.name:
                ical_event.add('summary', event.name)
            if event.description and self._html_to_text(event.description):
                ical_event.add('description', self._html_to_text(event.description))
            if event.location:
                ical_event.add('location', event.location)
            if event.videocall_location:
                ical_event.add('CONFERENCE', event.videocall_location)
            for partner in event.partner_ids:
                if partner == event.user_id.partner_id:
                    continue
                attendee = vCalAddress(f'MAILTO:{partner.email}')
                attendee.params['cn'] = vText(partner.name)
                attendee_record = self.env['calendar.attendee'].search([('event_id', '=', event.id), ('partner_id', '=', partner.id)], limit=1)
                if attendee_record:
                    attendee.params['partstat'] = vText(self._map_attendee_status(attendee_record.state))
                ical_event.add('attendee', attendee, encode=0)
            organizer = vCalAddress(f"MAILTO:{event.user_id.email}")
            organizer.params['cn'] = event.user_id.name
            ical_event.add('organizer', organizer)
            # Add RRULE if the event is recurrent
            if event.recurrency and event.recurrence_id:
                rrule = event.recurrence_id._get_rrule()
                rrule_dict = _parse_rrule_string(str(rrule))
                ical_event.add('rrule', rrule_dict)

            # Add DTSTART and DTEND
            ical_event.add('dtstart', utc.localize(event.start).astimezone(user_tz))
            ical_event.add('dtend', utc.localize(event.stop).astimezone(user_tz))

            calendar.add_component(ical_event)

        return calendar.to_ical()

    @api.model
    def poll_caldav_server(self):
        all_users = self.env['res.users'].search([]).filtered(lambda u: u.is_caldav_enabled())
        for user in all_users:
            self.with_user(user).poll_user_caldav_server()

    @api.model
    def poll_user_caldav_server(self):
        if not self._is_caldav_enabled():
            return
        client = self._get_caldav_client()
        calendar = client.calendar(url=self.env.user.caldav_calendar_url)
        events = calendar.events()
        caldav_uids = set()
        now = datetime.now()
        one_year_later = now + timedelta(days=365)

        _logger.info(f"Polling CalDAV server for user {self.env.user.name}")

        for caldav_event in events:
            ical_event = caldav_event.icalendar_instance
            self.sync_event_from_ical(ical_event)
            for component in ical_event.subcomponents:
                if isinstance(component, Event):
                    uid = str(component.get('uid'))
                    recurrence_id = str(component.get('recurrence-id'))
                    if recurrence_id == 'None':
                        recurrence_id = ''
                    caldav_uids.add(f"{uid}{recurrence_id}")

        _logger.info(f"CalDAV UIDs fetched: {caldav_uids}")

        # Remove Odoo events that no longer exist on the CalDAV server
        odoo_events = self.search([('caldav_uid', '!=', False)])
        for event in odoo_events:
            recurrence_id = event.caldav_recurrence_id or ''
            event_uid = f"{event.caldav_uid}{event.caldav_recurrence_id or ''}"
            if event_uid not in caldav_uids:
                _logger.info(f"Deleting orphan event {event.name} with UID {event.caldav_uid} "
                             f"and Recurrence ID {event.caldav_recurrence_id or ''}")
                event.with_context(caldav_no_sync=True).unlink()

    @api.model
    def _get_existing_instance(self, uid, recurrence_id):
        instance = self.env['calendar.event'].search([
            ('caldav_uid', '=', uid),
            ('recurrence_id', '=', recurrence_id)
        ])
        return instance or self.env['calendar.event'].search([
            ('caldav_uid', '=', 'uid'),
            ('recurrence_id', '=', False),
        ])

    def _get_recurrency_values_from_ical_event(self, component):
        """ Match the fields from calendar.event (recurring fields) to the fields specified in RRULE at
         https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html """

        rrule = component.get('rrule')
        if not rrule:
            if not self.recurrency:
                # No change, this was already not a recurring event
                return {}
            else:
                # This was a recurring event and has been made non-recurring
                if self.recurrence_id.base_event_id != self:
                    # This is not the base event, so change its recurrency only
                    return {'recurrence_update': 'self_only', 'recurrency': False, 'follow_recurrence': False}
                else:
                    # This is the base event, so change all events in the list
                    return {'recurrence_update': 'all_events', 'recurrency': False}
        rrule_str = rrule.to_ical().decode('utf-8')
        sequence = component.get('sequence')
        if sequence and sequence != 0:
            # This is not the base event so we can't change recurrence properties
            return {}

        caldav_recurrence_id = component.get('recurrence-id')
        rrule_params = self.env['calendar.recurrence']._rrule_parse(rrule_str, component.decoded('dtstart'))
        vals = {
            'recurrency': True,
            'follow_recurrence': True,
            'caldav_recurrence_id': caldav_recurrence_id,
            'recurrence_update': 'all_events',
            'rrule_type': rrule_params.get('rrule_type'),
            'end_type': rrule_params.get('end_type'),
            'interval': rrule_params.get('interval'),
            'count': rrule_params.get('count'),
            'month_by': rrule_params.get('monty_by'),
            'day': rrule_params.get('day'),
            'byday': rrule_params.get('byday'),
            'until': rrule_params.get('until'),
        }

        if rrule_params.get('weekday'):
            vals.update(rrule_params.get('weekday'))
        day_list = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        vals.update({day: rrule_params.get(day) for day in day_list if day in rrule_params})

        return vals

    def sync_event_from_ical(self, ical_event):
        email_regex = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
        current_user_email = self.env.user.email.lower()

        for component in ical_event.subcomponents:
            if isinstance(component, Event):
                uid = component.get('uid')
                recurrence_id = component.get(
                    'recurrence_id')  # Unique identifier for a single event in a recurrence set
                attendees = component.get('attendee', [])

                if isinstance(attendees, vCalAddress):
                    attendees = [attendees]
                elif isinstance(attendees, str):
                    attendees = [vCalAddress(attendees)]

                attendees_emails = [
                    email_regex.search(str(attendee)).group(0).lower().strip()
                    for attendee in attendees if email_regex.search(str(attendee))
                ]

                _logger.info(f"Attendees emails: {attendees_emails}")

                # Add current user email to attendees if not already present
                if current_user_email not in attendees_emails:
                    attendees_emails.append(current_user_email)

                attendee_ids = self.env['res.partner'].search([('email', 'in', attendees_emails)])

                existing_instance = self._get_existing_instance(uid, recurrence_id)
                start = component.decoded('dtstart')
                if isinstance(start, datetime):
                    start = start.astimezone(utc).replace(tzinfo=None)
                end = component.decoded('dtend')
                if isinstance(end, datetime):
                    end = end.astimezone(utc).replace(tzinfo=None)
                values = {
                    'name': str(component.get('summary')),
                    'start': start,
                    'stop': end,
                    'description': self._extract_component_text(component, 'description'),
                    'location': self._extract_component_text(component, 'location'),
                    'videocall_location': self._extract_component_text(component, 'conference'),
                    'caldav_uid': uid,
                    'partner_ids': [(6, 0, attendee_ids.ids)],
                }
                recurrency_vals = self._get_recurrency_values_from_ical_event(component)
                if recurrency_vals:
                    values.update(recurrency_vals)
                if not existing_instance:
                    _logger.info(f"Creating with vals: {values}")
                    self.with_context({'caldav_no_sync': True}).create(values)
                else:
                    _logger.info(f"Updating with vals: {values}")
                    changed_vals = {}
                    # Don't update partner_ids if no change
                    if attendee_ids - existing_instance.partner_ids:
                        changed_vals.update({
                            'partner_ids',values.pop('partner_ids'),
                        })

                    # Don't write values that haven't changed
                    for key, val in values.items():
                        if getattr(existing_instance, key) != val:
                            changed_vals.update({key: values.pop(key)})
                    if (recurrency_vals and recurrency_vals.get('recurrency')
                            and (not existing_instance.recurrency or not
                            existing_instance.follow_recurrence)):
                        existing_instance.write({
                            'recurrency': True,
                            'follow_recurrence': True,
                        })
                    existing_instance.with_context({
                        'caldav_no_sync': True,
                    }).write(changed_vals)

    @staticmethod
    def _extract_component_text(component, subcomponent_name):
        text = str(component.get(subcomponent_name))
        text = text if text != 'None' else ''

    @staticmethod
    def _html_to_text(html):
        return BeautifulSoup(html, "html.parser").getText()

    @staticmethod
    def _map_attendee_status(state):
        mapping = {
            'needsAction': 'NEEDS-ACTION',
            'accepted': 'ACCEPTED',
            'declined': 'DECLINED',
            'tentative': 'TENTATIVE',
        }
        return mapping.get(state, 'NEEDS-ACTION')

    @staticmethod
    def _map_ical_status(ical_status):
        mapping = {
            'NEEDS-ACTION': 'needsAction',
            'ACCEPTED': 'accepted',
            'DECLINED': 'declined',
            'TENTATIVE': 'tentative',
        }
        return mapping.get(ical_status, 'needsAction')
