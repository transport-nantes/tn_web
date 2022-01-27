This repository contains the Transport Nantes website code.

This program is distributed under the GNU GPL v3 licence.  See the file LICENCE for its text.

# Project description

(to come)

# Table of contents
- [1. How to install](#how-to-install)
  - [1.1 Requirements](#requirements)
  - [1.2 Setting the local environment](#setting-the-local-environment)
    - [1.2.1 Setting Django and Vagrant environment](#setting-django-and-vagrant-environment)
    - [1.2.2 Setting Django environment on Mac](#setting-django-environment-on-mac)
    - [1.2.3 Setting up a database](#setting-up-a-database)
- [2. Contribution guidelines](#contribution-guidelines)
  - [2.1 Style guide](#style-guide)
    - [2.1.1 Code Style](#code-style)
    - [2.1.2 Git Commit messages](#git-commit-messages)
  - [2.2 I want to contribute](#i-want-to-contribute)
  - [2.3 You have a question ?](#you-have-a-question)
# How to install
## Requirements
You will need the following softwares:

* [Python 3](https://www.python.org/downloads/)
* [Vagrant](https://www.vagrantup.com/downloads/)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Git](https://git-scm.com/downloads)

Vagrant and VirtualBox are optional (but recommended) if you use Linux.
Those two software will be used to create a virtual machine on which you will run the website. This machine is will be running Ubuntu 20.04, and Vagrant is used to script the installation of requirements on it.
The following instructions assume you have installed all the softwares listed above.
For Mac users, VirtualBox won't run on the new M1 chips(i.e. M1, M1 Pro, M1 Max) so follow the instructions below for Mac users.

## Setting the local environment

### Setting Django and Vagrant environment
At the end of those instructions, you should be able to run a local version of the website.

1. Fork the repository on GitHub.
Let's assume you have created a new repository called `mobilitains` in `/Documents/mobilitains`.

2. Use the `cd` command to change the current directory to the repository. 
E.g. :  `cd /Documents/mobilitains/`

3. Use `vagrant up --provision` to create the virtual machine. This can take some times depending on your internet connection.
It creates an Ubuntu environnement with all requirements to run the website (Django etc.).

4. Use `vagrant ssh` to connect to the virtual machine. You can check that if your terminal displays `vagrant@ubuntu-focal:~$ `.

5. Use `cd /vagrant/` to move to the website directory. You can find the website's code in this folder.

6. Enter the vagrant's virtual environnement by using `source venv.vagrant/bin/activate`. You can confirm it works by seeing the `(venv.vagrant) vagrant@ubuntu-focal:/vagrant$` in your terminal.

7. Enter the website's directory by using `cd transport_nantes/transport_nantes`. Your current directory should now be `(venv.vagrant) vagrant@ubuntu-focal:/vagrant/transport_nantes/transport_nantes$ `

8. Create a file called `settings_local.py` and fill it with the content of `settings_local.py.DEV.template`. This file isn't tracked on GitHub, so you can edit it without affecting the repository. It's mandatory to create this file in order to run the website. The content of `settings_local.py.DEV.template` is a base that defines the settings for the development environment.

9. Go one folder up using `cd ..` , you're current directory should now be `(venv.vagrant) vagrant@ubuntu-focal:/vagrant/transport_nantes$ `

10. You're ready to run the website, you can use `python manage.py runserver 0.0.0.0:8000` to run the server.
If you open your browser at `http://localhost:8000/` or `0.0.0.0:8000`, you should see the website.
However at this point, you should see a message saying you have X unapplied migrations in your console, and a 404 error.


Indeed, even though your configuration is fine, you don't have the database created yet.

### Setting Django environment on Mac
1. Fork the repository on GitHub.
Let's assume you have created a new repository called `mobilitains` in `/Documents/mobilitains`.

2. Use the `cd` command to change the current directory to the repository. 
E.g. :  `cd /Documents/mobilitains/`.

3. Create a python virtual environment in the `mobilitains` folder with `python -m venv venv`.
Activate the environment with `source venv/bin/activate` and clone your forked repo to `mobilitains`.

4. Use `cd` to change directory to `tn_web`. E.g. : `cd /Documents/mobilitains/tn_web`.
Install project dependencies with `pip install -r requirements.txt`. If this doesn't work install dependencies manually.
E.g. : `pip install django, pip install requests, etc`.

5. Create a folder for yor logs in your root folder. Let's assume you created a new folder `mbt_logs` in `/mobilitains/mbt_logs`.
Next, create a `tn_web.log` file inside the `mbt_logs` folder. E.g. : `/mobilitains/mbt_logs/tn_web.log`.

6. Enter the website's directory by using `cd transport_nantes/transport_nantes`. Your current directory should now be `mobilitains/tn_web/transport_nantes/transport_nantes`.

7. Create a file called `settings_local.py` and fill it with the content of `settings_local.py.DEV.template`. This file isn't tracked on GitHub, so you can edit it without affecting the repository. It's mandatory to create this file in order to run the website. The content of `settings_local.py.DEV.template` is a base that defines the settings for the development environment.

8. In `settings_local.py`, above the `LOG_DIR` variable, create a `path` variable and add your file path to the `mobilitains` directory.
I.e. `path = "/Users/name/Documents/mobilitains"`. Next, replace the path in the `LOG_DIR` variable with `os.path.join(path, "mbt_logs/")`.

9. Go one folder up using `cd ..` , you're current directory should now be `/mobilitains/tn_web/transport_nantes`.

10. You're ready to run the website, you can use `python manage.py runserver` to run the server.
If you open your browser at `http://127.0.0.1:8000/`, you should see the website.
However at this point, you should see a message saying you have X unapplied migrations in your console, or some kind of database error on the live site.


Indeed, even though your configuration is fine, you don't have the database created yet.

### Setting up a database

1. Start by running the `python manage.py migrate` command. You should now see a new file named `db.sqlite3` in your current directory.

2. Run `python manage.py createsuperuser` to create a superuser, you will use this to connect to Django's admin interface.

The database is set but still empty. Let's display a "Hello, world!" message in the landing page of your local version of the website !

3. Run `python manage.py runserver 0.0.0.0:8000` to run the server.

4. Open your browser at `http://localhost:8000/admin` or `0.0.0.0:8000/admin`. You're facing Django Admin's interface. Use the credentials you created to connect to it.

The landing page is an instance of an app named "topicblog", however because your database is empty, you will also need to create 1 item before you can see the landing page : 

5. Edition of the landing page 
  [todo]  
Congratulations, you customized your first page on the website ! You can now see it at `http://localhost:8000/` or `0.0.0.0:8000/` ! 

# Contribution Guidelines

## Style Guide

### Code Style

Make sure your code is well formatted.
This means : Complies to PEP8 (https://www.python.org/dev/peps/pep-0008/) and PEP257 (https://www.python.org/dev/peps/pep-0257/).
You can use linters such as `flake8` and `pylint` to check your code.

It must be written in English.

### Git Commit messages

* Your commits should be short and concise.
* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Reference issues and pull requests liberally after the first line


## I want to contribute

Thank you for your interest in contributing to this project.
The simplest way for you to contribute is to fork the repository and start a pull request.

If you want to report a bug, please open an issue on GitHub.

## You have a question ?

You can send your questions to [this address.](mailto:jevousaide@mobilitains.fr)

