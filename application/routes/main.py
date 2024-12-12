from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def home():
    """
    Home page that displays the main navigation.
    """
    return render_template('home.html')
