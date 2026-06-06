# -*- coding: utf-8 -*-
"""AppConfig — cau hinh co ban cua ung dung.

Dung singleton de dam bao chi co mot nguon cau hinh duy nhat.
Doc tu config/settings.json hoac hardcoded defaults.

Cong thuc:
    1. Doc tu config/settings.json (uu tien cao nhat)
    2. Doc tu config/app_settings.json (backup)
    3. Dung hardcoded defaults (chi khi ca 1 va 2 that bai)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional


class _AppConfigMeta(type):
    """Metaclass de dam bao chi co mot instance."""

    _instance: Optional["AppConfig"] = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class AppConfig(metaclass=_AppConfigMeta):
    """
    Cau hinh co ban ung dung — Singleton.

    Cac thuoc tinh deu la class-level (khong can instance).
    Doc tu file JSON hoac hardcoded defaults.
    """

    # ── Version ─────────────────────────────────────────────────────────────
    VERSION = "2.2.1"
    VERSION_MAJOR = 2
    VERSION_MINOR = 2
    VERSION_PATCH = 1

    # ── Update server ────────────────────────────────────────────────────────
    # URL GitHub Raw chua file update.json (dung de kiem tra va tai cap nhat)
    UPDATE_CHECK_URL = "https://raw.githubusercontent.com/ntuan8x/mkatool/refs/heads/main/update.json"
    # URL GitHub Releases (fallback)
    FALLBACK_GITHUB_URL = "https://api.github.com/repos/ntuan8x/mkatool/releases/latest"

    # ── Default settings ─────────────────────────────────────────────────────
    DEFAULT_BATCH_SIZE = 20
    DEFAULT_MAX_WORKERS = 8
    DEFAULT_PAID_MULTIPLIER = 10
    DEFAULT_TARGET_LANGUAGE = "vi"
    DEFAULT_THEME = "Light"

    # ── Checkpoint ──────────────────────────────────────────────────────────
    CHECKPOINT_DIR = "checkpoints"
    CHECKPOINT_MAX_AGE_DAYS = 30

    # ── Cache ───────────────────────────────────────────────────────────────
    TTS_CACHE_DIR = "cache/tts"
    TTS_CACHE_MAX_AGE_DAYS = 30

    # ── Private ─────────────────────────────────────────────────────────────
    _loaded: bool = False
    _config_data: dict = {}

    def __init__(self):
        if self._loaded:
            return
        self._loaded = True
        self._load()

    def _load(self):
        """Doc cau hinh tu file JSON."""
        # Tim root
        root = self._resolve_root()
        # Thu tu uu tien doc config
        candidates = [
            os.path.join(root, "config", "settings.json"),
            os.path.join(root, "app_settings.json"),
            os.path.join(root, "src", "app_settings.json"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self._config_data = json.load(f)
                    return
                except Exception:
                    pass
        # Khong tim thay -> dung defaults
        self._config_data = {}

    def _resolve_root(self) -> str:
        """Tim root cua ung dung."""
        if getattr(os.sys, "frozen", False):
            return getattr(os.sys, "_MEIPASS", os.path.dirname(os.path.abspath(os.sys.executable)))
        if os.environ.get("APP_ROOT"):
            return os.environ["APP_ROOT"]
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get(self, key: str, default: Any = None) -> Any:
        """Doc mot gia tri cau hinh."""
        return self._config_data.get(key, default)

    def get_version(self) -> str:
        return self._config_data.get("version", self.VERSION)

    def get_update_url(self) -> str:
        return self._config_data.get("update_url", self.UPDATE_CHECK_URL)

    def get_github_url(self) -> str:
        return self._config_data.get("github_url", self.FALLBACK_GITHUB_URL)
