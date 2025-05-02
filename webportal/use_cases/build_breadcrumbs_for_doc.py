from typing import List, Any

def build_breadcrumbs_for_doc(page: Any, nav: List[Any]) -> List[dict]:
    """
    Строит список хлебных крошек (breadcrumbs) для страницы Page на основе path и nav.

    Args:
        page: текущий объект Page
        nav: иерархия объектов Page (nav)

    Returns:
        Список словарей с ключами 'name' и 'url'
    """
    parts = page.path.strip("/").split("/")
    breadcrumbs = [{"name": "Документация", "url": "/doc"}]

    current_path = ""
    current_level = nav

    for slug in parts:
        current_path += "/" + slug
        match = next((p for p in current_level if getattr(p, "slug", None) == slug), None)
        if not match:
            break
        breadcrumbs.append({
            "name": getattr(match, "name", "Untitled"),
            "url": "/doc" + getattr(match, "path", "")
        })
        current_level = getattr(match, "child", [])

    if breadcrumbs:
        breadcrumbs[-1]["url"] = None

    return breadcrumbs