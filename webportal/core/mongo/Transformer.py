from bson import ObjectId
from datetime import datetime
from jsonschema import validate, ValidationError

from .Fields import ModelFieldTypes

class ModelFieldValueTransformer:

    @staticmethod
    def __handle_special_types(val, t):
        """
        Обрабатывает специфические типы данных, которые требуют приведения или десериализации
        вручную, перед валидацией по jsonschema.

        Используется как предварительная стадия трансформации до основного кастинга типов.

        Args:
            val: Значение поля, которое нужно обработать.
            t (ModelFieldTypes): Целевой тип из перечисления ModelFieldTypes.

        Returns:
            Приведенное значение, если удалось выполнить конвертацию.
            None — если тип не требует спец. обработки или приведение не выполнено.

        Обрабатываемые типы:
        - OBJECTID: Преобразует строку или уже готовый ObjectId в ObjectId
        - DATE: Преобразует ISO-строку в datetime.datetime (aware)
        """

        # Обработка ObjectId: либо возвращаем как есть, либо преобразуем из строки
        if t == ModelFieldTypes.OBJECTID:
            return val if isinstance(val, ObjectId) else ObjectId(val)
        
        # Обработка даты: если уже datetime, вернуть как есть, иначе распарсить ISO 8601 строку
        if t == ModelFieldTypes.DATE:
            return val if isinstance(val, datetime) else datetime.fromisoformat(val.replace("Z", "+00:00"))
        
        # Для остальных типов ничего не делаем
        return None

    @staticmethod
    def transform(model, field_name, val, field_type, validation_rules=None, logger=None):
        """
        Преобразует и валидирует значение поля на основе допустимых типов и правил валидации.

        Эта функция обрабатывает случаи, когда поле может иметь один или несколько допустимых типов 
        (например, через `anyOf` в jsonschema), и пытается привести значение к первому подходящему типу.

        Аргументы:
            val: Значение, которое нужно привести.
            field_type: Один или список типов из ModelFieldTypes.
            validation_rules (dict): Правила валидации JSON Schema (pattern, minLength и т.д.)
            logger (logging.Logger): Логгер для фиксации ошибок, если передан.

        Возвращает:
            Приведённое значение, если один из типов прошёл валидацию и преобразование,
            иначе — оригинальное значение.
        """
        if val is None:
            return None

         # Приведение к списку (если один тип — оборачиваем в список)
        types = field_type if isinstance(field_type, list) else [field_type]

         # Пробуем по очереди все возможные типы
        for t in types:
            try:
                # Если требуется специальная обработка (DATE, OBJECTID)
                val = ModelFieldValueTransformer.__handle_special_types(val, t) or val
                
                if t in (ModelFieldTypes.OBJECTID, ModelFieldTypes.DATE):
                    return val

                # Формируем схему и добавляем валидаторы
                schema = {"type": t.value}

                # if validation_rules:
                #     schema.update(validation_rules)

                # Валидация по jsonschema
                validate(instance=val, schema=schema)

                # Если прошло валидацию — возвращаем приведённое значение
                return ModelFieldValueTransformer.__cast(val, t)

            except Exception as e: 
                continue

         # Если не удалось привести ни к одному типу — логируем и возвращаем оригинал
        if logger:
            logger.warning(f"[Transform] Model = {model}, Field = {field_name}. Не удалось преобразовать '{val}' в один из типов {types}")

        return val

    @staticmethod
    def __cast(val, t: ModelFieldTypes):
        if t == ModelFieldTypes.STRING:
            return str(val)
        if t == ModelFieldTypes.INT:
            return int(val)
        if t == ModelFieldTypes.NUMBER:
            return float(val)
        if t == ModelFieldTypes.BOOLEAN:
            return bool(val)
        if t == ModelFieldTypes.ARRAY:
            return list(val)
        if t == ModelFieldTypes.OBJECT:
            return dict(val)
        return val  