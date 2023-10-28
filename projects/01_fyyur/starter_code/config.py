import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
# declaring environment variables to use on the db URI below
DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
DB_USER = os.getenv('DB_USER', 'evemwangi')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Nima900##')
DB_NAME = os.getenv('DB_NAME', 'fire')

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
print(SQLALCHEMY_DATABASE_URI)
