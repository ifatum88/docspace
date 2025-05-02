from flask import Blueprint, render_template

search_bp = Blueprint("search", __name__)
url = "/search"

@search_bp.route(url)
def search():
    breadcrumbs = [{"name": "Поиск", "url": None}]
    return render_template('search.html', breadcrumbs=breadcrumbs)