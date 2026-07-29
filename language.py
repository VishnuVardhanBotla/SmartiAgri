import json
from pathlib import Path

from flask import request, session

BASE_DIR = Path(__file__).resolve().parent
TRANSLATIONS_DIR = BASE_DIR / "translations"
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "flag": "🇬🇧"},
    "te": {"name": "తెలుగు", "flag": "🇮🇳"},
    "hi": {"name": "हिन्दी", "flag": "🇮🇳"},
    "ta": {"name": "தமிழ்", "flag": "🇮🇳"},
    "kn": {"name": "ಕನ್ನಡ", "flag": "🇮🇳"},
    "ml": {"name": "മലയാളം", "flag": "🇮🇳"},
    "mr": {"name": "मराठी", "flag": "🇮🇳"},
    "bn": {"name": "বাংলা", "flag": "🇮🇳"},
    "gu": {"name": "ગુજરાતી", "flag": "🇮🇳"},
    "pa": {"name": "ਪੰਜਾਬੀ", "flag": "🇮🇳"},
    "or": {"name": "ଓଡ଼ିଆ", "flag": "🇮🇳"},
}


def _get_translation_file(language):
    return TRANSLATIONS_DIR / f"{language}.json"


def _load_translations(language):
    path = _get_translation_file(language)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def set_language(language):
    language = language or "en"
    if language not in SUPPORTED_LANGUAGES:
        language = "en"
    session["language"] = language
    return language


def get_language():
    if "language" in session:
        return session["language"]
    cookie_language = request.cookies.get("language")
    if cookie_language and cookie_language in SUPPORTED_LANGUAGES:
        session["language"] = cookie_language
        return cookie_language
    requested = request.args.get("lang") or request.form.get("language")
    if requested and requested in SUPPORTED_LANGUAGES:
        session["language"] = requested
        return requested
    session["language"] = "en"
    return "en"


def translate(key, default=None, language=None, **kwargs):
    if language is None:
        language = get_language()
    translations = _load_translations(language)
    if key in translations:
        text = translations[key]
    elif language != "en":
        english = _load_translations("en")
        if key in english:
            text = english[key]
        else:
            text = default or key
    else:
        text = default or key
    if kwargs:
        return text.format(**kwargs)
    return text


def get_language_info(language=None):
    language = language or get_language()
    details = SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES["en"])
    return {"code": language, "name": details["name"], "flag": details["flag"]}


def get_language_options():
    return [
        {"code": code, "name": data["name"], "flag": data["flag"]}
        for code, data in SUPPORTED_LANGUAGES.items()
    ]
