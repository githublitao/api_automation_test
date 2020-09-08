CREATE USER 'root'@'%' IDENTIFIED BY '123456';
GRANT All privileges ON *.* TO 'root'@'%';
update mysql.user set authentication_string=password('123456') where user='root';