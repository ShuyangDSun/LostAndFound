Create backup
$ mysqldump -u root -p --databases lost_and_found > lost_and_found.sql

Restore:
$ mysql -u root -p < lost_and_found.sql

