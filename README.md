# Django Thermal Printer Project

This project demonstrates how to connect and use a thermal printer with a Django web application on Windows OS. It includes setting up a virtual environment, creating a Django project, and building an interface for dynamic printing using `win32print`. Additionally, it covers connecting devices like passport scanners and barcode readers to Python.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Setting Up the Virtual Environment](#setting-up-the-virtual-environment)
  - [Installing Required Packages](#installing-required-packages)
- [Setting Up the Django Project](#setting-up-the-django-project)
- [Creating Models](#creating-models)
- [Setting Up the Admin Interface](#setting-up-the-admin-interface)
- [Creating Views and Templates](#creating-views-and-templates)
- [Connecting Devices to Python](#connecting-devices-to-python)
- [Running the Project](#running-the-project)
- [Docker Installation](#docker-installation)
  - [Dockerfile](#dockerfile)
  - [docker-compose.yml](#docker-composeyml)
- [Conclusion](#conclusion)

## Prerequisites

Before starting, ensure you have the following:
- Python installed on your system
- Django installed in your Python environment
- A thermal printer with the necessary drivers installed on your Windows OS

## Installation

### Setting Up the Virtual Environment

1. Install `virtualenv` if you haven't already:

    ```sh
    pip install virtualenv
    ```

2. Create a virtual environment named `printer_env`:

    ```sh
    virtualenv printer_env
    ```

3. Activate the virtual environment:

    - On Windows:

      ```sh
      printer_env\Scripts\activate
      ```

    - On macOS/Linux:

      ```sh
      source printer_env/bin/activate
      ```

### Installing Required Packages

Within the virtual environment, install Django and other required packages:

```sh
pip install django pywin32
```

### Installing Required Packages

Now Migrating the data to the database:

```sh
python manage.py makemigrations pos
python manage.py migrate
```

or smiple 
### Install the project using Docker image

```sh
docker-compose build -d
```
