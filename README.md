oertutor
========

Web-based tutor using RL techniques to select best OER. Code is still in development, not a stable release.

Disclaimer
----------
I take no responsibility for any consequences that result from following these instructions. The instructions were made for Fedora 18 on a 64bit machine.

Required packages
-----------------
gcc, git, python, python-pip, python-virtualenv, mysql_server, mysql-devel

Installation
------------
    git clone git@github.com:mslatour/oertutor.git
    cd oertutor #The working directory from now on
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt

Setting up the database
-----------------------
The following commands use 'root' as MySQL administrator user)
For more information and other setups see: http://dev.mysql.com/doc/refman/5.1/en/adding-users.html

    sudo service mysqld start (start webserver)
    mysqladmin -uroot -p create oertutor
    mysql -uroot -p -e "CREATE USER 'django'@'localhost' IDENTIFIED BY 'djngpwd'"
    mysql -uroot -p -e "GRANT ALL PRIVILEGES ON oertutor.* TO 'django'@'localhost'"

Make sure you are in the working directory
    python manage.py syncdb

Running
-------
    sudo service mysqld start

Make sure you are in the working directory
    . venv/bin/activate
    python manage.py runserver # Default: http://127.0.0.1:8000
