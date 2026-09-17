#!/usr/bin/env python3
# ============================================================================
# scripts/check-translations.py
#
# Po co to jest:
#   Hugo NIE przerywa builda, gdy brakuje tłumaczenia. Zamiast tego po cichu
#   wstawia tekst z języka domyślnego (pl) albo pusty ciąg — i taka literówka
#   potrafi wylecieć na produkcję niezauważona. Ten skrypt wyłapuje to
#   ZANIM Hugo w ogóle wystartuje.
#
# Co dokładnie sprawdza:
#   1. i18n/*.yaml — czy każdy język ma DOKŁADNIE ten sam zestaw kluczy.
#   2. i18n/*.yaml — czy żadna wartość nie jest pusta.
#   3. data/*.yaml — czy każde pole tłumaczone (czyli takie, które jest
#      słownikiem z kluczami językowymi) ma komplet języków.
#
# Jak uruchomić lokalnie:
#   python3 scripts/check-translations.py
#
# Kody wyjścia:
#   0 — wszystko OK
#   1 — znaleziono problemy (szczegóły wypisane na stdout)
#
# W CI: ten skrypt jest wywoływany w .github/workflows/hugo.yml PRZED
# `hugo`, więc build na GitHubie wywali się z czytelnym komunikatem
# zamiast opublikować stronę z brakującym tłumaczeniem.
# ============================================================================

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("BŁĄD: brak modułu PyYAML. Zainstaluj go: pip install pyyaml")
    sys.exit(1)

# Katalog główny projektu = katalog nadrzędny wobec scripts/
ROOT = Path(__file__).resolve().parent.parent

# Lista obsługiwanych języków. Wyciągana z nazw plików w i18n/, żeby
# dodanie nowego języka nie wymagało edycji tego skryptu.
I18N_DIR = ROOT / "i18n"
DATA_DIR = ROOT / "data"

# Zbieramy tu wszystkie wykryte problemy; na końcu decydują o kodzie wyjścia.
problems = []


def load_yaml(path):
    """Wczytuje plik YAML i zwraca sparsowaną strukturę."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# KROK 1: i18n/*.yaml — parzystość kluczy między językami
# ---------------------------------------------------------------------------
i18n_files = sorted(I18N_DIR.glob("*.yaml"))
if not i18n_files:
    problems.append(f"Nie znaleziono żadnych plików w {I18N_DIR}")
    languages = []
else:
    # np. i18n/pl.yaml -> "pl"
    languages = [p.stem for p in i18n_files]
    print(f"Wykryte języki: {', '.join(languages)}")

bundles = {}
for path in i18n_files:
    data = load_yaml(path) or {}
    bundles[path.stem] = data

    # Sprawdzenie pustych wartości. Format Hugo to: klucz -> {"other": "tekst"}
    for key, value in data.items():
        if not isinstance(value, dict) or "other" not in value:
            problems.append(
                f"{path.name}: klucz '{key}' nie ma pod-klucza 'other' "
                f"(wymagany format Hugo)"
            )
        elif not str(value["other"]).strip():
            problems.append(f"{path.name}: klucz '{key}' ma pustą wartość")

# Porównujemy każdy język z językiem pierwszym na liście (alfabetycznie).
# Nie chodzi o to, który jest "wzorcem" — różnica w którąkolwiek stronę
# jest błędem, bo oznacza klucz obecny tylko w części plików.
if len(bundles) > 1:
    all_keys = set()
    for keys in bundles.values():
        all_keys |= set(keys.keys())

    for lang, data in bundles.items():
        missing = all_keys - set(data.keys())
        for key in sorted(missing):
            problems.append(f"i18n/{lang}.yaml: BRAKUJE klucza '{key}'")


# ---------------------------------------------------------------------------
# KROK 2: data/*.yaml — kompletność pól tłumaczonych
# ---------------------------------------------------------------------------
def check_translatable(value, where):
    """
    Rekurencyjnie przechodzi strukturę z data/*.yaml.

    Zasada rozpoznawania pola tłumaczonego: jeśli natrafimy na słownik,
    którego klucze pokrywają się z kodami języków (np. {'pl':..., 'en':...}),
    traktujemy go jako pole tłumaczone i wymagamy kompletu języków.
    Pola takie jak "name" czy "url" są zwykłymi napisami i są pomijane
    (celowo — to nazwy własne i adresy, wspólne dla wszystkich języków).
    """
    if isinstance(value, dict):
        keys = set(value.keys())
        # Czy to wygląda na pole tłumaczone? (część kluczy to kody języków)
        if keys & set(languages):
            missing = set(languages) - keys
            for lang in sorted(missing):
                problems.append(f"{where}: brakuje tłumaczenia '{lang}'")
            # Puste wartości w polu tłumaczonym
            for lang, text in value.items():
                if lang in languages and not str(text).strip():
                    problems.append(f"{where}.{lang}: pusta wartość")
        else:
            # Zwykły słownik — schodzimy głębiej
            for k, v in value.items():
                check_translatable(v, f"{where}.{k}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            check_translatable(item, f"{where}[{i}]")
    # Napisy/liczby — nic do sprawdzenia


for path in sorted(DATA_DIR.glob("*.yaml")):
    data = load_yaml(path)
    check_translatable(data, path.name)


# ---------------------------------------------------------------------------
# KROK 3: hugo.toml — zgodność języka domyślnego
# ---------------------------------------------------------------------------
# `defaultContentLanguage` (używane przez Hugo) i `params.defaultLang`
# (używane przez szablony do hreflang="x-default") to ta sama informacja
# zapisana w dwóch miejscach. Jeśli się rozjadą, x-default wskaże złą wersję
# językową — błąd całkowicie niewidoczny na stronie, wyłapywalny tylko tak.
try:
    import tomllib  # Python 3.11+

    with open(ROOT / "hugo.toml", "rb") as f:
        cfg = tomllib.load(f)

    default_content_lang = cfg.get("defaultContentLanguage")
    default_param_lang = cfg.get("params", {}).get("defaultLang")

    if default_param_lang is None:
        problems.append(
            "hugo.toml: brakuje [params] defaultLang — wymagany przez "
            "szablony do wygenerowania hreflang=\"x-default\""
        )
    elif default_content_lang != default_param_lang:
        problems.append(
            f"hugo.toml: defaultContentLanguage = '{default_content_lang}' "
            f"ale params.defaultLang = '{default_param_lang}' — muszą być zgodne"
        )
    elif default_param_lang not in languages:
        problems.append(
            f"hugo.toml: defaultLang = '{default_param_lang}', ale nie ma "
            f"pliku i18n/{default_param_lang}.yaml"
        )
except ImportError:
    # Python starszy niż 3.11 nie ma tomllib — pomijamy ten krok,
    # reszta walidacji działa normalnie.
    print("(pominięto sprawdzenie hugo.toml — wymaga Pythona 3.11+)")


# ---------------------------------------------------------------------------
# PODSUMOWANIE
# ---------------------------------------------------------------------------
if problems:
    print("\nZNALEZIONE PROBLEMY:\n")
    for p in problems:
        print(f"  - {p}")
    print(f"\nRazem: {len(problems)}. Build przerwany.")
    sys.exit(1)

print("\nOK — wszystkie tłumaczenia kompletne, brak pustych wartości.")
sys.exit(0)
