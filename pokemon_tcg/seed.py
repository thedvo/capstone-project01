from models import *
from app import app

# Clear any old tables
db.drop_all()

# Create all tables
db.create_all()