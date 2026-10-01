"""
Compatibility layer for Python 3.14+ / Pydantic v1 / ChromaDB in cloud environments.
Fixes pydantic.v1.errors.ConfigError during CrewAI imports on Python 3.14+.
"""
from typing import Any

try:
    import pydantic.v1.fields
    _orig_set_default_and_type = pydantic.v1.fields.ModelField._set_default_and_type

    def _safe_set_default_and_type(self):
        try:
            _orig_set_default_and_type(self)
        except Exception:
            self.type_ = Any
            self.outer_type_ = Any

    pydantic.v1.fields.ModelField._set_default_and_type = _safe_set_default_and_type
except Exception:
    pass
