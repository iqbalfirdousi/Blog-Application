Blog Application | Flask, MySQL
A user-friendly blogging web app built using Flask and SQLAlchemy ORM for efficient CRUD operations and a seamless user experience.

Features
User authentication system (secure login, user management)
SQLAlchemy integration for managing blog posts and user data
SMTP configuration for email notifications (contact form)
Dynamic web pages using Jinja2 templating
Installation & Setup
Clone the repository:
bash git clone <repository-url>
Create a virtual environment and activate it:
bash python -m venv venv source venv/bin/activate # On Windows use `venv\Scripts\activate`
Install the requirements:
bash pip install -r requirements.txt
Configure the database in config.py and initialize it.
Run the application:
bash flask run
