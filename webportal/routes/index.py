from flask import Blueprint, render_template, current_app
from bson import ObjectId

from entities import Content

index_bp = Blueprint("index", __name__)
url = "/"

@index_bp.route(url)
def index():
  breadcrumbs = [{"name": "Главная", "url": None}]
  doc = current_app.docs.find_many({"_id": ObjectId("6807e10cc21913e276d40a7a")}).first()
  content = Content(doc.content, doc.type).content

  return render_template('index.html', content=content, breadcrumbs=breadcrumbs)