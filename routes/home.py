# routes/home.py
from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__)

@home_bp.route('/', methods=['GET', 'POST'])
def home():
    """
    Home page that displays the main navigation.
    """
    return render_template('home.html')
