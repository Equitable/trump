/* sudo -u postgres 
   psql -f pgtrump.sql -v ua:$usrA -v uap:'$usrApass'
                       -v ub:$usrB -v ubp:'$usrBpass'*/

CREATE ROLE :ua WITH LOGIN PASSWORD :uap SUPERUSER CREATEDB CREATEROLE REPLICATION;
CREATE DATABASE trump OWNER :ua;
CREATE ROLE :ub WITH LOGIN PASSWORD :ubp;
GRANT ALL PRIVILEGES ON DATABASE trump TO :ua, :ub;