def get_last_slug_part(slug_path: str) -> str:
    """
    Извлекает последний slug из пути, игнорируя query-параметры и завершающие слеши.

    Примеры:
        "arch"                           → "arch"
        "arch/c4-d"                      → "c4-d"
        "arch/c4-d/ppp/ffff"            → "ffff"
        "arch/c4-d/ppp/ffff/"           → "ffff"
        "arch/c4-d/ppp/ffff/?var=val1"  → "ffff"
        "arch/c4-d/ppp/ffff/?a=1&b=2"   → "ffff"
    """
    if not slug_path:
        return ""

    # Убираем query-параметры, оставляя только путь
    path = slug_path.split("?")[0].strip("/")

    # Получаем последний сегмент
    return path.split("/")[-1] if path else ""