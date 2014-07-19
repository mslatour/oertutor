oertutor
========

Web-based tutor using genetic algorithm techniques to select best OER. Code is still in development, not a stable release. There are known issues with multiple student groups per lesson. If you are interested, it is best to send me a message.

Disclaimer
----------
I take no responsibility for any consequences that result from following these instructions. The instructions were made for Fedora 18 on a 64bit machine.

Required packages
-----------------
Install the required packages using the package manager yum.

    sudo yum install gcc git python python-pip python-virtualenv mysql-server mysql-devel

Installation
------------
Fetch the code and install the required python modules in a virtual environment.
    
    git clone git@github.com:mslatour/oertutor.git
    cd oertutor #The working directory from now on
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt

Setting up the database
-----------------------
The following commands use 'root' as MySQL administrator user. You can use different account details for the django user, just make the same adjustments in the settings.py file. For more information and other setups see: http://dev.mysql.com/doc/refman/5.1/en/adding-users.html

    sudo service mysqld start
    mysqladmin -uroot -p create oertutor
    mysql -uroot -p -e "CREATE USER 'django'@'localhost' IDENTIFIED BY 'djngpwd'"
    mysql -uroot -p -e "GRANT ALL PRIVILEGES ON oertutor.* TO 'django'@'localhost'"

Make sure you are in the working directory and then run the following command to create the tables.
    
    python manage.py syncdb

Running
-------
Start the mysql server.

    sudo service mysqld start

Make sure you are in the working directory, activate the virtual environment and run the django server.
    
    . venv/bin/activate
    python manage.py runserver # Default: http://127.0.0.1:8000
