#!/bin/bash
make clean
make
echo 'begin running server...'
# service postgresql start
# #psql -h 0.0.0.0 --username=postgres postgres
# su - postgres
# PGPASSWORD=postgres psql -h 0.0.0.0 --username=postgres
# #psql
# #ALTER USER postgres with password 'passw0rd';
# # CREATE DATABASE "EXCHANGE";
# #\q
# #exit
# # service postgresql restart
# #psql -c "ALTER USER SUPERUSER WITH postgres;"
# psql -U postgres -c "ALTER USER postgres with password 'passw0rd';"
# #psql -U postgres -c "CREATE DATABASE \"EXCHANGE\";"
# service postgresql restart
echo 'begin running server...'
./serv
while true
do
    sleep 1
done
