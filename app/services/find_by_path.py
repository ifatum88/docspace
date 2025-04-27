def find_by_path(tree, path):
    for node in tree:
        if getattr(node, "path", "") == path:
            return node
        result = find_by_path(getattr(node, "child", []), path)
        if result:
            return result
    return None