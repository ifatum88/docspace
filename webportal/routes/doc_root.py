from flask import Blueprint, render_template

doc_root_bp = Blueprint("doc_root", __name__)
url = "/doc"

@doc_root_bp.route(url)
def doc_root():
    breadcrumbs = [{"name": "Документация", "url": None}]
    return render_template('doc_root.html', breadcrumbs=breadcrumbs)