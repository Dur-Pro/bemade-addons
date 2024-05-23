CalDAV Synchronization
======================

Bemade Inc.

Copyright (C) 2023-June Bemade Inc. (<https://www.bemade.org>).
Author: Marc Durepos (Contact : marc@bemade.org)

This program is under the terms of the GNU Lesser General Public License (LGPL-3)
For details, visit https://www.gnu.org/licenses/lgpl-3.0.en.html

Overview
--------

The CalDAV Synchronization module for Odoo allows users to synchronize their
calendar events with CalDAV servers. This enables seamless integration of Odoo
calendar with external applications like Apple Calendar or Thunderbird.

Features
--------

- Synchronize Odoo calendar events with CalDAV servers.
- Create, update, and delete events in Odoo and reflect changes on the CalDAV
  server.
- Poll CalDAV server for changes and update Odoo calendar accordingly.

Configuration
-------------

1. Install the module in Odoo.
2. Go to the User settings in Odoo.
3. Enter the CalDAV calendar URL, username, and password on the user settings.

Usage
-----

1. Create a calendar event in Odoo and it will be synchronized with the CalDAV
   calendar.
2. Update the event in Odoo and the changes will reflect on the CalDAV server.
3. Delete the event in Odoo and it will be removed from the CalDAV server.
4. Changes made to the calendar on the CalDAV server (other email apps) will be
   polled and updated in Odoo.

Technical Details
-----------------

- The module extends the `calendar.event` model to add CalDAV synchronization
  functionality.
- It uses the `icalendar` library to format events and the `caldav` library to
  interact with CalDAV servers.
- Polling for changes on the CalDAV server can be triggered manually by
  triggering the scheduled action in Odoo.

License
-------

This program is under the terms of the GNU Lesser General Public License (LGPL-3)
For details, visit https://www.gnu.org/licenses/lgpl-3.0.en.html
