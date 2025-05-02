from flask import Blueprint, render_template

history_bp = Blueprint("history", __name__)
url = "/history"

@history_bp.route(url)
def history():
    breadcrumbs = [{"name": "История", "url": None}]
    return render_template('history.html', breadcrumbs=breadcrumbs)
