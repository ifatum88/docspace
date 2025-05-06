from flask import Blueprint, request, render_template
from entities import Content


content_generate_bp = Blueprint("content_generate", __name__)
url = "/content/generate"
methods = ["POST"]

@content_generate_bp.route(url, methods=methods)
def content_generate():

    content = request.form.get('content')
    content_type = request.form.get('content_type')

    return render_template(
        "content/main.html",
        content=Content(content, content_type).content
    )
