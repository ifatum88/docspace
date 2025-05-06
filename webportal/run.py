# core app libraries
from core.build import build_app

# app routes
import routes

# App
app = build_app()

# СТАТИЧЕСКИЕ РОУТЫ
app.register_blueprint(routes.index_bp) # Домашняя страница
app.register_blueprint(routes.search_bp) # Поиск
app.register_blueprint(routes.history_bp) # История изменений
app.register_blueprint(routes.doc.doc_nav_bp) # Страница всех документов

# ДИНАМИЧЕСКИЕ РОУТЫ
app.register_blueprint(routes.page.by_path_bp) # Загрузка страницы по пути
app.register_blueprint(routes.page.by_id_bp) # Загрузка страницы по id

# ASYNC загрузки блоков страниц
app.register_blueprint(routes.doc.doc_layout_bp) # Загрузка layout документов
app.register_blueprint(routes.content.content_generate_bp) # Генерация контента документа

# FEATURE: Сделать красивы темплейт для вывода ошибок на страницы
# FEATURE: Добавть необязательные name в коллекцию doc
# FEATURE: Подключить draw.io
# FEATURE: Подключить DBML
# FEATURE: Подключить OpenAPI
# FEATURE: Сделать чтобы сворачивались разворачивались меню айтемы (стрелочка была на тех, где есть дочки и точки там, где нет). Поведение - развопачиваем все древо до текущей страницы и дочерные страницы N-1 к текущей странице

# FEATURE: ON THIS PAGE - передвижение по якорям h1 по станице

# DESIGN REF - https://cruip.com/demos/docs/?ref=builtatlightspeed
# BOOTSTRAP DevDoc - https://demo.htmlcodex.com/2011/bootstrap-documentation-template/
# 

print (app.url_map)

# RUN
if __name__ == '__main__':
  app.run(debug=True, use_reloader=False, threaded=True)


  # code - e86f
  # generate - e069
  # info - e88e
  # close - e5cd