"""Persistencia simple de casos en un único fichero JSON local.

No es una BD de verdad: serializa el dict de casos completo a disco cada vez
que se escribe. Suficiente para la demo del hackathon — todo el estado vive en
`apps/api/db/casos.json` y se carga al arrancar el servidor.

reload: 1
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from threading import RLock
from typing import Iterator

from models import Caso

def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


class JsonCasoStore:
    """Dict-like store de Caso → fichero JSON en disco.

    Implementa la interfaz mínima de `dict[str, Caso]` que ya usan los routers
    (`__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `values`,
    `keys`, `items`, `get`), así que sustituir el `casos_db` por una instancia
    de esta clase no requiere tocar el resto del código.
    """

    def __init__(self, path: Path):
        _log(f"[JsonCasoStore] Loading from {path}")
        self._path = path
        self._lock = RLock()
        self._data: dict[str, Caso] = {}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        _log(f"[JsonCasoStore] Checking path: {self._path}")
        if not self._path.exists():
            _log(f"[JsonCasoStore] Path does not exist!")
            return
        _log(f"[JsonCasoStore] Path exists, reading...")
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            _log(f"[JsonCasoStore] Loaded {len(raw)} raw entries")
        except (json.JSONDecodeError, OSError) as e:
            _log(f"[JsonCasoStore] Error reading JSON: {e}")
            return
        for caso_id, blob in raw.items():
            try:
                self._data[caso_id] = Caso.model_validate(blob)
                _log(f"[JsonCasoStore] OK: {caso_id}")
            except Exception as e:
                _log(f"[JsonCasoStore] FAIL {caso_id}: {e}")
                continue
        _log(f"[JsonCasoStore] Total loaded: {len(self._data)}")

    def _flush(self) -> None:
        payload = {cid: json.loads(c.model_dump_json()) for cid, c in self._data.items()}
        tmp_fd, tmp_path = tempfile.mkstemp(
            prefix="casos_", suffix=".json.tmp", dir=str(self._path.parent)
        )
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
            os.replace(tmp_path, self._path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    # ── dict-like API ────────────────────────────────────────────────────────

    def __getitem__(self, key: str) -> Caso:
        with self._lock:
            return self._data[key]

    def __setitem__(self, key: str, value: Caso) -> None:
        with self._lock:
            self._data[key] = value
            self._flush()

    def __delitem__(self, key: str) -> None:
        with self._lock:
            del self._data[key]
            self._flush()

    def __contains__(self, key: object) -> bool:
        with self._lock:
            return key in self._data

    def __iter__(self) -> Iterator[str]:
        with self._lock:
            return iter(list(self._data.keys()))

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)

    def get(self, key: str, default=None):
        with self._lock:
            return self._data.get(key, default)

    def keys(self):
        with self._lock:
            return list(self._data.keys())

    def values(self):
        with self._lock:
            return list(self._data.values())

    def items(self):
        with self._lock:
            return list(self._data.items())
