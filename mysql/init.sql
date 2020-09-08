CREATE DATABASE IF NOT EXISTS api_test DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
GRANT All privileges ON *.* TO 'root'@'%';
update mysql.user set authentication_string=password('123456') where user='root';