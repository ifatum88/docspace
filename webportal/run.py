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
app.register_blueprint(routes.doc_root_bp) # Страница всех документов

# ДИНАМИЧЕСКИЕ РОУТЫ
app.register_blueprint(routes.show_doc_by_path_bp)
app.register_blueprint(routes.show_doc_by_id_bp)

# FRONT: Сделать чтобы сворачивались разворачивались меню айтемы (стрелочка была на тех, где есть дочки и точки там, где нет).
#        Поведение - развопачиваем все древо до текущей страницы и дочерные страницы N-1 к текущей странице
# FRONT: Сделать несколько типов документ на одной странице и всю мета информацию спарятать под (i)
# FRONT: Подключить draw.io
# FRONT: Подключить PlantUML

# RUN
if __name__ == '__main__':
  app.run(debug=True, use_reloader=False)