
from odoo.tests.common import TransactionCase
from unittest.mock import patch, MagicMock
import caldav

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

    def test_create_caldav_event(self):
        with patch('caldav.DAVClient') as MockClient:
            mock_client = MockClient.return_value
            mock_principal = mock_client.principal.return_value
            mock_calendar = mock_principal.calendars.return_value[0]
            mock_event = MagicMock()
            mock_event.vobject_instance.vevent.uid.value = 'test-uid-12345'
            mock_calendar.add_event.return_value = mock_event

            event = self.env['calendar.event'].create({
                'name': 'Test Event',
                'start': '2024-05-22 10:00:00',
                'stop': '2024-05-22 11:00:00',
                'description': 'This is a test event',
                'location': 'Test Location',
                'create_uid': self.user.id,
            })

            self.assertEqual(event.name, 'Test Event')
            self.assertEqual(event.caldav_uid, 'test-uid-12345')

    def test_update_caldav_event(self):
        with patch('caldav.DAVClient') as MockClient:
            mock_client = MockClient.return_value
            mock_principal = mock_client.principal.return_value
            mock_calendar = mock_principal.calendars.return_value[0]
            mock_event = MagicMock()
            mock_event.vobject_instance.vevent.uid.value = 'test-uid-12345'
            mock_calendar.add_event.return_value = mock_event

            event = self.env['calendar.event'].create({
                'name': 'Test Event',
                'start': '2024-05-22 10:00:00',
                'stop': '2024-05-22 11:00:00',
                'description': 'This is a test event',
                'location': 'Test Location',
                'create_uid': self.user.id,
            })

            with patch.object(event, 'sync_to_caldav') as mock_sync_to_caldav:
                event.write({
                    'name': 'Updated Test Event',
                    'start': '2024-05-22 12:00:00',
                    'stop': '2024-05-22 13:00:00',
                })
                mock_sync_to_caldav.assert_called_once()

            self.assertEqual(event.name, 'Updated Test Event')
            self.assertEqual(event.start, '2024-05-22 12:00:00')

    def test_delete_caldav_event(self):
        with patch('caldav.DAVClient') as MockClient:
            mock_client = MockClient.return_value
            mock_principal = mock_client.principal.return_value
            mock_calendar = mock_principal.calendars.return_value[0]
            mock_event = MagicMock()
            mock_event.vobject_instance.vevent.uid.value = 'test-uid-12345'
            mock_calendar.add_event.return_value = mock_event

            event = self.env['calendar.event'].create({
                'name': 'Test Event',
                'start': '2024-05-22 10:00:00',
                'stop': '2024-05-22 11:00:00',
                'description': 'This is a test event',
                'location': 'Test Location',
                'create_uid': self.user.id,
            })

            with patch.object(event, 'remove_from_caldav') as mock_remove_from_caldav:
                event.unlink()
                mock_remove_from_caldav.assert_called_once()

    def test_poll_caldav_server(self):
        with patch('caldav.DAVClient') as MockClient:
            mock_client = MockClient.return_value
            mock_principal = mock_client.principal.return_value
            mock_calendar = mock_principal.calendars.return_value[0]
            mock_event = MagicMock()
            mock_event.icalendar.return_value = """
            BEGIN:VCALENDAR
            VERSION:2.0
            BEGIN:VEVENT
            UID:test-uid-12345
            DTSTAMP:20240522T100000Z
            DTSTART:20240522T100000Z
            DTEND:20240522T110000Z
            SUMMARY:Polled Event
            DESCRIPTION:This event was polled from CalDAV
            LOCATION:Polled Location
            END:VEVENT
            END:VCALENDAR
            """
            mock_calendar.events.return_value = [mock_event]

            with patch.object(self.env['calendar.event'], 'sync_event_from_ical') as mock_sync_event_from_ical:
                self.env['calendar.event'].poll_caldav_server()
                mock_sync_event_from_ical.assert_called_once()

    def test_poll_caldav_server_with_exception(self):
        with patch('caldav.DAVClient') as MockClient:
            mock_client = MockClient.return_value
            mock_principal = mock_client.principal.return_value
            mock_calendar = mock_principal.calendars.return_value[0]
            mock_event = MagicMock()
            mock_event.icalendar.return_value = """
            BEGIN:VCALENDAR
            VERSION:2.0
            BEGIN:VEVENT
            UID:test-uid-12345
            DTSTAMP:20240522T100000Z
            DTSTART:20240522T100000Z
            DTEND:20240522T110000Z
            SUMMARY:Polled Event
            DESCRIPTION:This event was polled from CalDAV
            LOCATION:Polled Location
            END:VEVENT
            END:VCALENDAR
            """
            mock_calendar.events.return_value = [mock_event]
            mock_client.principal.side_effect = Exception('Invalid credentials')

            with patch.object(self.env['calendar.event'], '_logger') as mock_logger:
                self.env['calendar.event'].poll_caldav_server()
                mock_logger.error.assert_any_call('Failed to poll CalDAV server for user Test User: Invalid credentials')
