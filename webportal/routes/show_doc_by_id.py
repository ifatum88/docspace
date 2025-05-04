from flask import Blueprint, render_template, current_app, request, abort
from use_cases import build_breadcrumbs_for_doc
from entities import Content
from bson import ObjectId

show_doc_by_id_bp = Blueprint("show_doc_by_id", __name__)
url = "/doc/id/<string:page_id>"
endpoint = "doc_by_id"

@show_doc_by_id_bp.route(url, endpoint=endpoint)
def show_doc_by_id(page_id):

    page = current_app.nav.find_by_id(page_id) or abort(404)
    breadcrumbs = build_breadcrumbs_for_doc(page, current_app.nav.nav)
    layout = request.args.get('layout')
    docs =  current_app.docs.find_many({"_id": {"$in": [ObjectId(doc_id) for doc_id in page.docs]}}) 
    
    return render_template('doc.html', page=page, breadcrumbs=breadcrumbs, docs_ids=page.docs, layout=layout, docs=docs)
