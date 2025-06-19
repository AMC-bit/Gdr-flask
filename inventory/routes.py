from . import inventory_bp
from flask import render_template

@inventory_bp.route('/view_inventory')
def view_inventory():
    return render_template('view_inventory.html')