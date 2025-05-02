from flask import Blueprint, render_template, current_app, request, abort
from use_cases import build_breadcrumbs_for_doc
from entities import Content

show_doc_by_id_bp = Blueprint("show_doc_by_id", __name__)
url = "/doc/id/<string:page_id>"
endpoint = "doc_by_id"

@show_doc_by_id_bp.route(url, endpoint=endpoint)
def show_doc_by_id(page_id):
 
    page = current_app.nav.find_by_id(page_id) or abort(404)
    doc = current_app.docs.find_one({"_id": page.doc})
    breadcrumbs = build_breadcrumbs_for_doc(page, current_app.nav.nav)
    is_generated = request.args.get('g')
    content = doc.content if doc else None
    
    if is_generated != "raw" and doc:
        content = Content(content, getattr(doc,"type")).content

    return render_template('doc.html', page=page, breadcrumbs=breadcrumbs, doc=doc, content=content, is_generated=is_generated)