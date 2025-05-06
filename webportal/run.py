# core app libraries
from core.build import build_app

# app routes
import routes
import routes.partials

# App
app = build_app()

# СТАТИЧЕСКИЕ РОУТЫ
app.register_blueprint(routes.index_bp) # Домашняя страница
app.register_blueprint(routes.search_bp) # Поиск
app.register_blueprint(routes.history_bp) # История изменений
app.register_blueprint(routes.doc_root_bp) # Страница всех документов

# ДИНАМИЧЕСКИЕ РОУТЫ
app.register_blueprint(routes.show_doc_by_path_bp) # Загрузка страницы по пути
app.register_blueprint(routes.show_doc_by_id_bp) # Загрузка страницы по id

# ASYNC загрузки блоков страниц
app.register_blueprint(routes.partials.doc_content_bp) # Загрузка контнета для страниц

# FRONT: Сделать чтобы сворачивались разворачивались меню айтемы (стрелочка была на тех, где есть дочки и точки там, где нет).
#        Поведение - развопачиваем все древо до текущей страницы и дочерные страницы N-1 к текущей странице

# FEATURE: Сделать спинер на загрузку контента
# FEATURE: Сделать красивы темплейт для вывода ошибок на страницы
# FEATURE: Подключить draw.io
# FEATURE: Подключить DBML
# FEATURE: Подключить OpenAPI

# FEATURE: ON THIS PAGE - передвижение по якорям h1 по станице

# DESIGN REF - https://cruip.com/demos/docs/?ref=builtatlightspeed
# BOOTSTRAP DevDoc - https://demo.htmlcodex.com/2011/bootstrap-documentation-template/
# 

# RUN
if __name__ == '__main__':
  app.run(debug=True, use_reloader=False, threaded=True)


  # code - e86f
  # generate - e069
  # info - e88e
  # close - e5cd