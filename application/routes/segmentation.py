from flask import Blueprint, render_template

segmentation_bp = Blueprint('segmentation', __name__)

@segmentation_bp.route('/segmentation')
def segmentation():
    """
    Placeholder page for Segmentation.
    """
    return render_template('segmentation.html')
