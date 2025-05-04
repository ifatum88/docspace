from flask import Blueprint, request, render_template
from entities import Content

import json

doc_content_bp = Blueprint("doc_content", __name__)
url = "/content/"
methods = ["POST"]
endpoint = "generate_content"

@doc_content_bp.route(url, methods=methods, endpoint=endpoint)
def doc_content():

    doc = json.loads(request.form.get('doc'))
    layout = request.form.get('layout')
    show = request.form.get('show')
    content = doc['content'] if show == "raw" else Content(doc['content'], doc['type']).content

    print (f"Генерирую документ {doc['_id']}, Layout={layout}, Show={show}", end="\n")
    
    return render_template("doc_block.html", 
                           doc=doc,
                           layout=layout,
                           content=content,
                           show=show
                           )

