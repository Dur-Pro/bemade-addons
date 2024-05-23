from odoo.tests.common import TransactionCase
from unittest.mock import patch, MagicMock
import caldav
from icalendar import Calendar, Event
from datetime import datetime


class TestCaldavSync(TransactionCase):

    def setUp(self):
        super(TestCaldavSync, self).setUp()
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'caldav_server_url': 'http://testserver/caldav',
            'caldav_username': 'testuser',
            'caldav_password': 'password',
        })
        self.env = self.env(context=dict(self.env.context, no_reset_password=True))

    @patch('odoo.addons.caldav_sync.models.calendar_event.CalendarEvent._get_caldav_client')
    def test_create_caldav_event(self, mock_get_caldav_client):
        mock_client = MagicMock()
        mock_principal = MagicMock()
        mock_calendar = MagicMock()
        mock_event = MagicMock()
        mock_event.id = 'test-uid-12345'

        mock_client.principal.return_value = mock_principal
        mock_principal.calendars.return_value = [mock_calendar]
        mock_calendar.add_event.return_value = mock_event
        mock_get_caldav_client.return_value = mock_client

        event = self.env['calendar.event'].with_user(self.user).create({
            'name': 'Test Event',
            'start': '2024-05-22 10:00:00',
            'stop': '2024-05-22 11:00:00',
            'description': 'This is a test event',
            'location': 'Test Location',
            'create_uid': self.user.id,
        })

        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.caldav_uid, 'test-uid-12345')

    @patch('odoo.addons.caldav_sync.models.calendar_event.CalendarEvent._get_caldav_client')
    @patch('odoo.addons.caldav_sync.models.calendar_event.CalendarEvent.sync_to_caldav')
    def test_update_caldav_event(self, mock_sync_to_caldav, mock_get_caldav_client):
        mock_client = MagicMock()
        mock_principal = MagicMock()
        mock_calendar = MagicMock()
        mock_event = MagicMock()
        mock_event.id = 'test-uid-12345'

        mock_client.principal.return_value = mock_principal
        mock_principal.calendars.return_value = [mock_calendar]
        mock_calendar.add_event.return_value = mock_event
        mock_get_caldav_client.return_value = mock_client

        event = self.env['calendar.event'].with_user(self.user).create({
            'name': 'Test Event',
            'start': '2024-05-22 10:00:00',
            'stop': '2024-05-22 11:00:00',
            'description': 'This is a test event',
            'location': 'Test Location',
            'create_uid': self.user.id,
        })

        event.with_user(self.user).write({
            'name': 'Updated Test Event',
            'start': '2024-05-22 12:00:00',
            'stop': '2024-05-22 13:00:00',
        })
        self.assertEqual(mock_sync_to_caldav.call_count, 2)

        self.assertEqual(event.name, 'Updated Test Event')
        self.assertEqual(event.start, datetime.strptime('2024-05-22 12:00:00', '%Y-%m-%d %H:%M:%S'))

    @patch('odoo.addons.caldav_sync.models.calendar_event.CalendarEvent._get_caldav_client')
    @patch('odoo.addons.caldav_sync.models.calendar_event.CalendarEvent.remove_from_caldav')
    def test_delete_caldav_event(self, mock_remove_from_caldav, mock_get_caldav_client):
        mock_client = MagicMock()
        mock_principal = MagicMock()
        mock_calendar = MagicMock()
        mock_event = MagicMock()
        mock_event.id = 'test-uid-12345'

        mock_client.principal.return_value = mock_principal
        mock_principal.calendars.return_value = [mock_calendar]
        mock_calendar.add_event.return_value = mock_event
        mock_get_caldav_client.return_value = mock_client

        event = self.env['calendar.event'].with_user(self.user).create({
            'name': 'Test Event',
            'start': '2024-05-22 10:00:00',
            'stop': '2024-05-22 11:00:00',
            'description': 'This is a test event',
            'location': 'Test Location',
            'create_uid': self.user.id,
        })

        event.with_user(self.user).unlink()
        mock_remove_from_caldav.assert_called()

    @patch('odoo.addons.caldav_sync.models.calendar_event.CalendarEvent.sync_event_from_ical')
    def test_poll_caldav_server(self, mock_sync_event_from_ical):
        mock_sync_event_from_ical.return_value = None
        with patch('caldav.DAVClient') as MockClient:
            mock_client = MockClient.return_value
            mock_principal = mock_client.principal.return_value
            mock_calendar = mock_principal.calendars.return_value[0]
            mock_event = MagicMock()

            # Create a Calendar object and add an Event to it
            cal = Calendar()
            event = Event()
            event.add('uid', 'test-uid-12345')
            event.add('dtstamp', datetime.strptime('20240522T100000Z', '%Y%m%dT%H%M%SZ'))
            event.add('dtstart', datetime.strptime('20240522T100000Z', '%Y%m%dT%H%M%SZ'))
            event.add('dtend', datetime.strptime('20240522T110000Z', '%Y%m%dT%H%M%SZ'))
            event.add('summary', 'Polled Event')
            event.add('description', 'This event was polled from CalDAV')
            event.add('location', 'Polled Location')
            cal.add_component(event)

            # Set the mock event's icalendar_instance to the iCal string
            mock_event.icalendar_instance = Calendar.from_ical(cal.to_ical())
            mock_calendar.events.return_value = [mock_event]

            self.env['calendar.event'].poll_caldav_server()
            mock_sync_event_from_ical.assert_called_once()

    @patch('odoo.addons.caldav_sync.models.calendar_event._logger')
    def test_poll_caldav_server_with_exception(self, mock_logger):
        with patch('caldav.DAVClient') as MockClient:
            mock_client = MockClient.return_value
            mock_client.principal.side_effect = Exception('Invalid credentials')

            self.env['calendar.event'].poll_caldav_server()
            mock_logger.error.assert_any_call('Failed to poll CalDAV server for user Test User: Invalid credentials')
