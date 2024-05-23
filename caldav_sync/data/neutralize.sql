-- Neutralize CalDAV synchronization by setting credentials to NULL
UPDATE res_users
SET caldav_server_url = NULL,
    caldav_username = NULL,
    caldav_password = NULL
WHERE caldav_server_url IS NOT NULL
   OR caldav_username IS NOT NULL
   OR caldav_password IS NOT NULL;
