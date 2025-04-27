# imports
from flask import render_template, abort, url_for, request
from core.build import build_app
from db.models.page import Page
from db.models.doc import Doc
from services import build_hierarchy, build_breadcrumbs_for_doc, find_by_path, Content, ContentType
from bson import ObjectId
from filters import register_filters

# APp
app = build_app()
register_filters(app)

#DB.Models
mongo_client = app.client
pages = Page.use(mongo_client)
docs = Doc.use(mongo_client)

#Services
nav = build_hierarchy(pages.all())

# FRONT: Сделать чтобы сворачивались разворачивались меню айтемы (стрелочка была на тех, где есть дочки и точки там, где нет).
# Поведение - развопачиваем все древо до текущей страницы и дочерные страницы N-1 к текущей странице

# Mongo: Делаем схемы doc / page
# Mongo: Делаем валидацию по схеме doc / page
# написать систему работы с логами (скорее всего у flask она итак есть)

# Вывод N документов на 1 странице по порядоку + тут надо будет выводить все теги со всеми типами данных
# Подключить draw.io
# Подключить PlantUML

@app.context_processor
def inject_globals():
  def url_for_page(item, use_id=False):
      if use_id or not hasattr(item, "path"):
          return url_for("show_doc_by_id", page_id=item.id)
      return "/doc" + item.path

  return {
      "nav": nav,
      "url_for_page": url_for_page,
  }

# СТАТИЧЕСКИЕ РОУТЫ
# Домашняя страница
@app.route('/')
def index():
  breadcrumbs = [{"name": "Главная", "url": None}]
  doc = docs.get_one({"_id": ObjectId("6807e10cc21913e276d40a7a")})
  content = Content(getattr(doc, "content", ""), getattr(doc, "type", "")).content

  return render_template('index.html', content=content, breadcrumbs=breadcrumbs)

# Поиск
@app.route('/search')
def search():
  breadcrumbs = [{"name": "Поиск", "url": None}]
  return render_template('search.html', breadcrumbs=breadcrumbs)

# История
@app.route('/history')
def history():
  breadcrumbs = [{"name": "История", "url": None}]
  return render_template('history.html', breadcrumbs=breadcrumbs)

# ДИНАМИЧЕСКИЕ РОУТЫ
# Страница всех документов
@app.route('/doc')
def doc_root():
  breadcrumbs = [{"name": "Документация", "url": None}]
  return render_template('doc_root.html', breadcrumbs=breadcrumbs)

# Доступ к документам по ID
@app.route('/doc/id/<string:page_id>', endpoint='doc_by_id')
def show_doc_by_id(page_id):
  page = pages.get_one({"_id": ObjectId(page_id)})
  doc = docs.get_one({"_id": getattr(page, "doc")})
  if not page:
    abort(404)

  return render_template('doc.html', page=page, doc=doc)

# Доступ к документам по полному пути из slug
@app.route('/doc/<path:slug_path>', endpoint='doc_by_path')
def show_doc_by_path(slug_path):
    
    page = find_by_path(nav, '/' + slug_path.strip('/'))
    doc = docs.get_one({"_id": getattr(page, "doc")}) if getattr(page, "doc") else None
    breadcrumbs = build_breadcrumbs_for_doc(page, nav)
    is_generated = request.args.get('g')
    content = getattr(doc, "content", "")

    if is_generated != "raw" and doc:
      content = Content(content, getattr(doc,"type")).content

    if not page:
        abort(404)

    return render_template('doc.html', page=page, breadcrumbs=breadcrumbs, doc=doc, content=content, is_generated=is_generated)


# RUN
if __name__ == '__main__':
  app.run(debug=True, use_reloader=False)