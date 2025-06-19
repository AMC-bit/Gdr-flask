from . import inventory_bp
from flask import render_template

@inventory_bp.route('/inventory')
def inventory():
    return render_template('inventory.html')