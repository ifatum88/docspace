from flask import Blueprint, request, render_template

import json

doc_layout_bp = Blueprint("doc_layout", __name__)
url = "/doc/layout"
methods = ["POST"]
endpoint = "doc_load"

@doc_layout_bp.route(url, methods=methods, endpoint=endpoint)
def doc_layout():

    doc = json.loads(request.form.get('doc'))
    layout = request.form.get('layout')
    show = request.form.get('show')
    content_type = "raw" if show == "raw" else doc['type']
    # content = Content(doc['content'], doc_type).content

    return render_template("doc/layout.html", 
                           doc=doc,
                           layout=layout,
                           content=doc.get('content'),
                           content_type=content_type,
                           show=show
                           )

