Setup Instructions
==================

Development Environment
-----------------------

To install the project in a development environment, only Python and some Python packages are required. It is also recommended to use a proper database such as PostgreSQL in the development environment already. The installation with PostgreSQL is described below. Alternatively, SQLite can also be used, which gets installed with Python 3.

Prerequisites
^^^^^^^^^^^^^

- **Python 3.11.6 or higher**: https://www.python.org/downloads/
- Recommended: **PostgreSQL**: https://www.postgresql.org/download/
- **Python Packages**:
    - **Django**: 5.0.6
    - **dotenv**: 1.0.1
    - **qrcode**: 7.4.2
    - **reportlab**: 4.2.2
    - **requests**: 2.32.3
    - **psycopg** (for usage with PostgreSQL): 3.2.1
    - **django-sslserver** (for usage with SSL/HTTPS): 22.0.0

Getting started
^^^^^^^^^^^^^^^

Before getting started you need to install all prerequisites. Once successfully installed, you need to make a few configurations, before you can start your development server.

If want to use another database besides PostgreSQL you can edit `DATABASES` in `settings.py` following `Django's guide <https://docs.djangoproject.com/en/5.0/ref/databases/>`__.

If you want to use PostgreSQL, please continue reading.

Setup DB (PostgreSQL)
"""""""""""""""""""""

First, we need to create a database and a database user and grant the user access to the database, by
replacing >DB-User<, >DB-User-Password< and >DB-Name< with the username, password and database name you wish to use in the following commands:

.. code-block:: bash

    sudo -i -u postgres
    psql
    CREATE ROLE >DB-User< WITH LOGIN SUPERUSER PASSWORD '>DB-User-Password<';
    CREATE DATABASE >DB-Name<;
    GRANT ALL PRIVILEGES ON DATABASE >DB-Name< TO >DB-User<;
    \q
    exit

Edit .env File
""""""""""""""

Next, we need to add a `.env`-file which holds various sensitive information, including the database access, by executing:

.. code-block:: bash

    nano .env

Replace placeholder values `>...<` with your actual configuration details. A **secret** SumUp-API-Key can be created `here <https://developer.sumup.com/api-keys>`__.

.. code-block:: none

    DJANGO_SECRET_KEY=django-insecure-e(lhi9t328)pm_rl=@refzhpmw1soj-9_j$@zaba4gle24#1xq

    EMAIL_HOST=>Email-Host<
    EMAIL_HOST_USER=>E-Mail-Address<
    EMAIL_HOST_PASSWORD=>Password<

    DB_USER=>DB-User<
    DB_PASSWORD=>DB-User-Password<
    DB_HOST=>DB-Host<
    DB_NAME=>DB-Name<

    MEMBER_API_USER=>API-Username<
    MEMBER_API_REFRESH_TOKEN=>API-Refresh-Token<

    SUMUP_API_KEY=>SumUp-API-Key<

After saving the file, you should now be ready to connect Django to your PostgreSQL database.

Initializing DB Tables
""""""""""""""""""""""

Before you can start your development server, you need to create Django migrations and apply them, by running:

.. code-block:: bash

    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic
    python manage.py createcachetable
    python manage.py createsuperuser

Optionally, you can also run those lines, to create guest and event users and a predefined menu:

.. code-block:: bash

    python manage.py create_menu
    python manage.py create_guest_user
    python manage.py create_event_user

Prepare settings.py and start server
""""""""""""""""""""""""""""""""""""

Now you are almost ready to start your development server. Depending on whether you want to use a SSL-certificate or not, you need to adjust `settings.py`.

Using an SSL-certificate is necessary to use the QR-Code feature.

If you want to use the development server **with** a SSL-certificate, you need to add `sslserver` to `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = [
        # other installed apps ...
        'sslserver',
    ]

After that, you can start the development server using:

.. code-block:: bash

    python manage.py runsslserver


If you want to use the development server **without** a SSL-certificate, you need to either remove `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` or change them all to `False`.

.. code-block:: python

    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

After that, you can start the development server using:

.. code-block:: bash

    python manage.py runserver






Production Environment
----------------------

To install the project in a production environment, you will need to install the following software. You do not need to install the software beforehand. Following the step-by-step guide, you will install all required software along the way.

Below the installation on a Linux system (Ubuntu 23.10 was tested) with PostgreSQL database and NGINX webserver is described. Alternatively, other databases and webservers could be used. In addition various Python packages are required and will be installed in a Python venv.

After completing the step-by-step guide, your server should be running on localhost (127.0.0.1).

Software
^^^^^^^^

- **Python**: https://www.python.org/downloads/
- **PostgreSQL**: https://www.postgresql.org/download/
- **NGINX Server**: https://nginx.org/en/download.html
- **Python Packages**:
    - **Django**: 5.0.6
    - **dotenv**: 1.0.1
    - **qrcode**: 7.4.2
    - **reportlab**: 4.2.2
    - **requests**: 2.32.3
    - **psycopg (for usage with PostgreSQL)**: 3.2.1
    - **gunicorn (for usage with NGINX)**: 22.0.0

Installation (Deployment)
^^^^^^^^^^^^^^^^^^^^^^^^^

This installation guide is made for Linux systems only. Installation on Windows should be possible, but was not testet.

Clone Repository
""""""""""""""""

Replace >Your-Path< with the path where you want to save the source code.

.. code-block:: bash

    git clone xxxxx >Your-Path<

System Update
"""""""""""""

.. code-block:: bash

    sudo apt update
    sudo apt upgrade -y

Install and Enable Database
"""""""""""""""""""""""""""

.. code-block:: bash

    sudo apt install postgresql-contrib
    sudo systemctl enable postgresql

Setup Database
""""""""""""""

Replace >DB-User<, >DB-User-Password< and >DB-Name< with the username, password and database name you wish to use.

.. code-block:: bash

    sudo -i -u postgres
    psql
    CREATE ROLE >DB-User< WITH LOGIN SUPERUSER PASSWORD '>DB-User-Password<';
    CREATE DATABASE >DB-Name<;
    GRANT ALL PRIVILEGES ON DATABASE >DB-Name< TO >DB-User<;
    \q
    exit

Create Locale
"""""""""""""

.. code-block:: bash

    sudo locale-gen de_DE de_DE.UTF-8

Install Python and Required Packages
""""""""""""""""""""""""""""""""""""

Replace >Your-Path< with the location you cloned the repository to.

.. code-block:: bash

    sudo apt install python3 python3-pip python3-venv -y

    cd >Your-Path</mysite
    pip install --upgrade pip setuptools
    python3 -m venv venv
    source venv/bin/activate
    cd ..
    pip install -r requirements.txt
    cd mysite

Create Required Directories
"""""""""""""""""""""""""""

.. code-block:: bash

    mkdir -p logs media invoices qr_codes/{login,password}

Create .env File
""""""""""""""""

.. code-block:: bash

    nano .env

Replace placeholder values `>...<` with your actual configuration details. A **secret** SumUp-API-Key can be created `here <https://developer.sumup.com/api-keys>`__.

.. code-block:: none

    DJANGO_SECRET_KEY=django-insecure-e(lhi9t328)pm_rl=@refzhpmw1soj-9_j$@zaba4gle24#1xq

    EMAIL_HOST=>Email-Host<
    EMAIL_HOST_USER=>E-Mail-Address<
    EMAIL_HOST_PASSWORD=>Password<

    DB_USER=>DB-User<
    DB_PASSWORD=>DB-User-Password<
    DB_HOST=>DB-Host<
    DB_NAME=>DB-Name<

    MEMBER_API_USER=>API-Username<
    MEMBER_API_REFRESH_TOKEN=>API-Refresh-Token<

    SUMUP_API_KEY=>SumUp-API-Key<

Test Gunicorn
"""""""""""""

.. code-block:: bash

    gunicorn --workers 3 mysite.wsgi:application

End with Strg + C.

Initialize Django Project
"""""""""""""""""""""""""

.. code-block:: bash

    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic
    python manage.py createsuperuser
    python manage.py create_menu
    python manage.py create_guest_user
    python manage.py create_event_user
    python manage.py createcachetable
    deactivate

Install NGINX
"""""""""""""

.. code-block:: bash

    sudo apt install nginx -y

Create NGINX Configuration File
"""""""""""""""""""""""""""""""

Replace >NGINX-Config-Name< with a name for your NGINX Configuration e.g.: 'self_service_kiosk'

.. code-block:: bash

    sudo nano /etc/nginx/sites-available/>NGINX-Config-Name<

Replace >Your-Path< placeholders with the location you cloned this repository to.

.. code-block:: none

    server {
        listen 80;
        server_name 127.0.0.1;
        return 301 https://$host$request_uri;  # Redirects all HTTP requests to HTTPS
    }

    server {
        listen 443 ssl;
        server_name 127.0.0.1;

        ssl_certificate >Your-Path</mysite/mysite.crt;
        ssl_certificate_key >Your-Path</mysite/mysite.key;

        location /static/ {
            alias >Your-Path</mysite/static/;
            expires 30d;
            access_log off;
        }

        location /media/ {
            alias >Your-Path</mysite/media/;
            expires 30d;
            access_log off;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:>Your-Path</mysite/mysite.sock;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

Enable NGINX Configuration and Start NGINX on Boot
""""""""""""""""""""""""""""""""""""""""""""""""""

Replace >NGINX-Config-Name< with the NGINX configuration name you selected.

.. code-block:: bash

    sudo ln -s /etc/nginx/sites-available/>NGINX-Config-Name< /etc/nginx/sites-enabled
    sudo systemctl enable nginx

Check and Restart NGINX
"""""""""""""""""""""""

.. code-block:: bash

    sudo nginx -t
    sudo systemctl restart nginx

Set Permissions for Static Files
""""""""""""""""""""""""""""""""

Replace >Your-Username< with the username you are using and >Your-Path< placeholders with the location you cloned this repository to.

.. code-block:: bash

    sudo chown -R >Your-Username<:www-data >Your-Path</mysite
    sudo chmod -R 755 >Your-Path</mysite

Set Permissions for Home Directory
""""""""""""""""""""""""""""""""""

Replace >Your-Path< with the location you cloned this repository to.

.. code-block:: bash

    sudo chmod 755 >Your-Path</

Setup Gunicorn as a System Service
""""""""""""""""""""""""""""""""""

Replace >Your-Path< placeholders with the location you cloned this repository to.

.. code-block:: bash

    sudo nano /etc/systemd/system/gunicorn.service

.. code-block:: none

    [Unit]
    Description=gunicorn daemon
    After=network.target

    [Service]
    User=ctraut
    Group=www-data
    WorkingDirectory=>Your-Path</mysite/
    ExecStart=>Your-Path</mysite/venv/bin/gunicorn --workers 3 --bind unix:>Your-Path</mysite/mysite.sock mysite.wsgi:application

    [Install]
    WantedBy=multi-user.target

Start and Enable Gunicorn Service
"""""""""""""""""""""""""""""""""

.. code-block:: bash

    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn

Configure Firewall
""""""""""""""""""

.. code-block:: bash

    sudo ufw allow 'Nginx Full'

Configurations
^^^^^^^^^^^^^^

Host-Settings (IP-Configuration)
""""""""""""""""""""""""""""""""

To use another host/ip than localhost (127.0.0.1) you need to modify Djangos `settings.py` and your NGINX configuration.

Add your desired host/ip `>Your-Host<` to `ALLOWED_HOSTS`:

.. code-block:: python

    ALLOWED_HOSTS = [
        "127.0.0.1",  # You can remove this line if you want
        ">Your-Host<"
    ]

And modify your NGINX configuration by replacing >NGINX-Config-Name< with a name of your NGINX Configuration e.g.: 'self_service_kiosk' in the following command:

.. code-block:: bash

    sudo nano /etc/nginx/sites-available/>NGINX-Config-Name<

Now you can need to replace >Your-Host< with your desired host/ip address.

.. code-block:: none

    server {
        listen 80;
        server_name >Your-Host<;
        return 301 https://$host$request_uri;  # Redirects all HTTP requests to HTTPS
    }

    server {
        listen 443 ssl;
        server_name >Your-Host<;

        ssl_certificate >Your-Path</mysite/mysite.crt;
        ssl_certificate_key >Your-Path</mysite/mysite.key;

        location /static/ {
            alias >Your-Path</mysite/static/;
            expires 30d;
            access_log off;
        }

        location /media/ {
            alias >Your-Path</mysite/media/;
            expires 30d;
            access_log off;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:>Your-Path</mysite/mysite.sock;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

After saving your changes, you can apply the changes by reloading system services and restarting Gunicorn and NGINX service.

SSL-Certificate
"""""""""""""""

This repository comes with a self-singed certificate for simple installation. In a production scenario you might want to use your own ssl-certificate.

The simplest way to achieve that is by placing your certificate and key as 'mysite.key' and 'mysite.crt' in the 'mysite' folder.

Alternatively you can modify those filenames and paths by editing the according lines in the NGINX configuration like shown in the previous chapter.

Django Debug Mode
"""""""""""""""""

For production environments Django suggests disabling the `DEBUG` mode by setting `DEBUG=False` in `settings.py`.

After changing the file you should restart your Gunicorn service to apply changes.

Useful Commands
^^^^^^^^^^^^^^^

Reload System Services:
"""""""""""""""""""""""

.. code-block:: bash

    sudo systemctl daemon-reload

Restart Gunicorn Service
""""""""""""""""""""""""

.. code-block:: bash

    sudo systemctl restart gunicorn

Show Gunicorn Service Status
""""""""""""""""""""""""""""

.. code-block:: bash

    systemctl status gunicorn

Restart NGINX Service
"""""""""""""""""""""

.. code-block:: bash

    sudo systemctl restart nginx

Show NGINX Service Status
"""""""""""""""""""""""""

.. code-block:: bash

    systemctl status nginx
