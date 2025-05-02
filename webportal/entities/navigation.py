from core.mongo import QuerySet
from typing import List, Any
from bson import ObjectId
from datetime import datetime

class Navigation:

    def __init__(self, pages:QuerySet):
        self.pages = pages
        self.nav = self.__build_hierarchy()
    
    def __build_hierarchy(self) -> List[Any]:
        """
        Строит иерархическое представление объектов Page, добавляя атрибут `path`.

        Принимает QuerySet, состоящий из объектов модели Page, и преобразует его
        в список вложенных деревьев, где каждый объект содержит ссылку на своих детей
        и путь `path` от корня до текущего узла.

        Возвращает список корневых узлов.
        """

        children_map = {}      # id -> list of children ids
        first_parent = {}      # child_id -> first parent id
        id_index = {}          # id -> индекс
        id_to_doc = {}         # id -> объект Page
        pages = self.pages

        for index, doc in enumerate(pages):
            doc_id = doc._id
            id_index[doc_id] = index
            id_to_doc[doc_id] = doc
            children = doc.child or []
            children_map[doc_id] = children
            for child_id in children:
                if child_id not in first_parent:
                    first_parent[child_id] = doc_id

        visited = set()
        result_forest = []

        for doc in pages:
            doc_id = doc._id
            if doc_id in visited:
                continue
            if doc_id in first_parent:
                parent_id = first_parent[doc_id]
                if id_index.get(parent_id, float('inf')) < id_index.get(doc_id, -1):
                    continue
                if parent_id not in children_map.get(doc_id, []):
                    continue
            tree = self.__build_tree(id_to_doc, visited, children_map, first_parent,doc_id, set(), "")
            result_forest.append(tree)

        result_forest.sort(key=lambda page: getattr(page, "order", float("inf")))        
        
        return result_forest
    
    def __build_tree(self, id_to_doc, visited, children_map, first_parent, node_id, stack, current_path):
        doc_obj = id_to_doc[node_id]
        visited.add(node_id)
        stack.add(node_id)

        slug = doc_obj.slug or ""
        full_path = f"{current_path}/{slug}".replace("//", "/")
        doc_obj.path = full_path
        doc_obj.child = []

        children = children_map.get(node_id, [])
        sorted_children = sorted(
            children,
            key=lambda cid: val if (val := self.__get_attr_by_object_id(cid, "order")) is not None else float("inf")
        )

        for child_id in sorted_children:
            if child_id in visited or child_id in stack:
                continue
            if child_id in first_parent and first_parent[child_id] != node_id:
                continue
            child_node = self.__build_tree(id_to_doc, visited, children_map, first_parent, child_id, stack, full_path)
            doc_obj.child.append(child_node)

        stack.remove(node_id)
        return doc_obj
    
    def __get_attr_by_object_id(self, id:ObjectId, arrg:str):
        for doc in self.pages:
            if doc._id == id:
                attr_val = getattr(doc, arrg)
                return attr_val
            
    def to_list_of_dics(self):
        def serialize(obj):
            result = {}
            for key, val in vars(obj).items():
                if isinstance(val, list):
                    result[key] = [serialize(v) if hasattr(v, "__dict__") else v for v in val]
                elif isinstance(val, ObjectId):
                    result[key] = str(val)
                elif isinstance(val, datetime):
                    result[key] = val.isoformat()
                elif hasattr(val, "__dict__"):
                    result[key] = serialize(val)
                else:
                    result[key] = val
            return result

        return [serialize(doc) for doc in self.nav]
    
    def __recursive_search(self, hierarchy, field, filter):

        """
        Рекурсивный поиск объекта по полю `filter_field` в иерархии self.nav
        
        """

        for node in hierarchy:
            if getattr(node, field) == filter:
                return node
            children = getattr(node, "child", [])
            result = self.__recursive_search(children, field, filter)
            if result:
                return result
            
        return None
        
    def find_by_path(self, target_path:str):
        """
        Поиск элемента меню в иерархии по полю `path`.
        """

        target_path = "/" + target_path.strip("/")
        hierarchy = self.nav
        field = "path"
        return self.__recursive_search(hierarchy, field, target_path)
    
    def find_by_id(self, id:str):
        """
        Поиск элемента меню в иерархии по полю `id`.
        """

        id = ObjectId(id) if not isinstance(id, ObjectId) else id
        hierarchy = self.nav
        field = "_id"
        return self.__recursive_search(hierarchy, field, id)
