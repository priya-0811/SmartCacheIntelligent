-- MySQL Initialization Script for Docker Container Entrypoint
GRANT ALL PRIVILEGES ON smartcache_db.* TO 'root'@'%';
FLUSH PRIVILEGES;

USE smartcache_db;

-- Initial configuration verification comment
SELECT 'SmartCache Database Initialized Successfully' AS message;
