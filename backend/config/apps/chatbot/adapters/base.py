from typing import Any, Optional, List
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError, transaction


class BaseAdapterError(Exception):
    def __init__(self, message: str, missing_fields: List[str] = None):
        super().__init__(message)
        self.message = message
        self.missing_fields = missing_fields or []


class BaseAdapter:
    def _validate_params(self, params: dict, required: list[str]) -> list[str]:
        errors = []
        for field in required:
            if field not in params or params[field] is None:
                errors.append(f"Missing required field: {field}")
        return errors

    def _safe_get(self, model, pk: int, model_name: str) -> Any:
        try:
            return model.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise BaseAdapterError(f"{model_name} with id {pk} not found")
        except (ValueError, TypeError):
            raise BaseAdapterError(f"Invalid id for {model_name}: {pk}")

    def _safe_delete(self, obj: Any, model_name: str) -> dict:
        try:
            with transaction.atomic():
                obj.delete()
            return {"deleted": True, "model": model_name, "id": getattr(obj, 'pk', None)}
        except IntegrityError as e:
            raise BaseAdapterError(f"Cannot delete {model_name}: related objects exist")

    def _to_dict(self, obj: Any) -> dict:
        if obj is None:
            return None
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    if hasattr(value, '__dict__'):
                        result[key] = self._to_dict(value)
                    elif hasattr(value, 'all'):
                        result[key] = [self._to_dict(item) for item in value.all()]
                    else:
                        result[key] = value
            return result
        return obj

    def _parse_date(self, date_str: Optional[str]) -> Any:
        from datetime import datetime
        if not date_str:
            return None
        if isinstance(date_str, str):
            for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y'):
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            raise BaseAdapterError(f"Invalid date format: {date_str}")
        return date_str

    def _parse_int(self, value: Any, field_name: str) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            raise BaseAdapterError(f"Invalid integer for {field_name}: {value}")