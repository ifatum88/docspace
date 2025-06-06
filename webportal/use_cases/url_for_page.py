from flask import url_for

def url_for_page(item, use_id=False):
    if use_id or not hasattr(item, "path"):
        return url_for("page_by_id.load_by_id", page_id=item._id)
    return "/doc" + item.path