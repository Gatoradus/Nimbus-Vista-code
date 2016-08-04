TODO

* mysql and system root passwords need to be different
===============================================

mysql_secure_installation answers:

Normally, root should only be allowed to connect from
'localhost'. This ensures that someone cannot guess at
the root password from the network.

Disallow root login remotely? (Press y|Y for Yes, any other key for No) : N

By default, MySQL comes with a database named 'test' that
anyone can access. This is also intended only for testing,
and should be removed before moving into a production
environment.


Remove test database and access to it? (Press y|Y for Yes, any other key for No) : N


Did the following:=============================================
mysql> CREATE DATABASE test;
Query OK, 1 row affected (0.00 sec)

mysql> GRANT ALL ON test.* TO 'example_user' IDENTIFIED BY 'password';
ERROR 1819 (HY000): Your password does not satisfy the current policy requirements
mysql> GRANT ALL ON test.* TO 'example_user' IDENTIFIED BY '#jJ68-11-1968'
    -> ;
Query OK, 0 rows affected, 1 warning (0.00 sec)

# PHP
==========================================================

apt-get install php
apt-get install php-pear
apt-get install php-mysql

These are the settings Linode is recommending. Need to return to this later:

max_execution_time = 30
memory_limit = 128M
error_reporting = E_COMPILE_ERROR|E_RECOVERABLE_ERROR|E_ERROR|E_CORE_ERROR
display_errors = Off
log_errors = On
error_log = /var/log/php/error.log
register_globals = Off



#DNS
==================================================
administrator is the email for all zones







