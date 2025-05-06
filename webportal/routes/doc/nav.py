from flask import Blueprint, render_template

doc_nav_bp = Blueprint("doc_nav", __name__)
url = "/doc"

@doc_nav_bp.route(url)
def doc_nav():
    breadcrumbs = [{"name": "Документация", "url": None}]
    return render_template('doc/nav.html', breadcrumbs=breadcrumbs)