mysql -uroot -p 123456 <<EOF

source /docker-entrypoint-initdb.d/init.sql;
