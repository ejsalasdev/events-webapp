# Event Management System :tada:

![GitHub License](https://img.shields.io/github/license/ejsalasdev/events-webapp)

## Description :clipboard:

A simple web application developed using FastAPI, designed to manage registrations and user information databases for events or parties. 🎉


## Installation :wrench:

To install this project, follow these steps:

```bash
git clone https://github.com/ejsalasdev/events-webapp
cd events-webapp
```

Create and activate a virtual environment (optional, but recommended)

```python -m venv venv
source venv/bin/activate  # on Windows use `venv\Scripts\activate`
```

To install the necessary dependencies for this project, ensure you have Python and pip installed on your system, and then run the following command:

```bash
pip install -r requirements.txt
```

Database Configuration with SQLite

By default, the application uses SQLite. You do not need to configure additional database settings.

Initial Migrations with Alembic

To set up your database with the necessary migrations, use Alembic:

```
# Generate the initial migration (this will create a migration script in the 'migrations/versions' folder)
alembic revision --autogenerate -m "Initial migration"

# Apply the migrations to the database
alembic upgrade head
```

## Usage :computer:

Updating the roles Table

Before you start using the application, it's necessary to populate the roles table with specific role names that the application will use for authorization purposes. Here's how to manually insert the required roles into the database:

```
# Access your SQLite database
sqlite3 path_to_database.db

# Insert roles into the 'roles' table
INSERT INTO roles (role_name) VALUES ('user');
INSERT INTO roles (role_name) VALUES ('admin');
INSERT INTO roles (role_name) VALUES ('super');

# Verify that the roles have been inserted
SELECT * FROM roles;
```


Here's how you can use the application:

```bash
uvicorn main:app --reload
```

## License :scroll:

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

