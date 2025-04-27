from typing import List, Any


def build_hierarchy(doc_list: List[Any]) -> List[Any]:
    """
    Строит иерархическое представление объектов Page,
    добавляя атрибуты `path` и `child` прямо в экземпляры модели.

    Args:
        doc_list: список объектов модели Page

    Returns:
        Иерархия объектов Page с полями `path` и `child`
    """
    children_map = {}      # id -> list of children ids
    first_parent = {}      # child_id -> first parent id
    id_index = {}          # id -> индекс
    id_to_doc = {}         # id -> объект Page

    for index, doc in enumerate(doc_list):
        doc_id = doc.id
        id_index[doc_id] = index
        id_to_doc[doc_id] = doc
        children = doc.child or []
        children_map[doc_id] = children
        for child_id in children:
            if child_id not in first_parent:
                first_parent[child_id] = doc_id

    visited = set()
    result_forest = []

    def build_tree(node_id, stack, slug_path_list):
        doc_obj = id_to_doc[node_id]
        visited.add(node_id)
        stack.add(node_id)

        slug = getattr(doc_obj, "slug", "")
        full_path = "/" + "/".join(slug_path_list + [slug])
        doc_obj.path = full_path
        doc_obj.child = []

        children = children_map.get(node_id, [])
        sorted_children = sorted(
            children,
            key=lambda cid: getattr(id_to_doc.get(cid), "order", float("inf"))
        )

        for child_id in sorted_children:
            if child_id in visited or child_id in stack:
                continue
            if child_id in first_parent and first_parent[child_id] != node_id:
                continue
            child_node = build_tree(child_id, stack, slug_path_list + [slug])
            doc_obj.child.append(child_node)

        stack.remove(node_id)
        return doc_obj

    for doc in doc_list:
        doc_id = doc.id
        if doc_id in visited:
            continue
        if doc_id in first_parent:
            parent_id = first_parent[doc_id]
            if id_index.get(parent_id, float('inf')) < id_index.get(doc_id, -1):
                continue
            if parent_id not in children_map.get(doc_id, []):
                continue
        tree = build_tree(doc_id, set(), [])
        result_forest.append(tree)

    return result_forest