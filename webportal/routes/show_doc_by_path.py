from flask import Blueprint, render_template, current_app, request, abort
from use_cases import build_breadcrumbs_for_doc
from entities import Content
from bson import ObjectId

show_doc_by_path_bp = Blueprint("show_doc_by_path", __name__)
url = "/doc/<path:slug_path>"
endpoint = "doc_by_path"

@show_doc_by_path_bp.route(url, endpoint=endpoint)
def show_doc_by_path(slug_path):
 
    page = current_app.nav.find_by_path(slug_path) or abort(404)
    breadcrumbs = build_breadcrumbs_for_doc(page, current_app.nav.nav)
    layout = request.args.get('layout')
    docs =  current_app.docs.find_many({"_id": {"$in": [ObjectId(doc_id) for doc_id in page.docs]}}) 
    
    return render_template('doc.html', page=page, breadcrumbs=breadcrumbs, docs_ids=page.docs, layout=layout, docs=docs)