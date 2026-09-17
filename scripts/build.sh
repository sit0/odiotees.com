#!/usr/bin/env bash
# ============================================================================
# scripts/build.sh — lokalny build produkcyjny.
#
# Robi DOKŁADNIE to samo co GitHub Actions (poza samą publikacją), więc
# jeśli ten skrypt przechodzi lokalnie, build na GitHubie też przejdzie.
# Wynik ląduje w katalogu public/.
#
# Użycie:
#   ./scripts/build.sh                      # baseURL = "/" (do testów lokalnych)
#   ./scripts/build.sh https://odiotees.com/   # baseURL pod docelową domenę
#
# UWAGA: podając własny baseURL, ZAWSZE kończ go ukośnikiem (/).
# Bez niego Hugo skleja adresy błędnie (np. ".../repoen/" zamiast ".../repo/en/").
# ============================================================================

set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v hugo >/dev/null 2>&1; then
  echo "BŁĄD: nie znaleziono Hugo. Instrukcja instalacji: README.md, sekcja 'Wymagania'."
  exit 1
fi

# Pierwszy argument to baseURL; jeśli go nie podano, użyj "/"
BASE_URL="${1:-/}"

echo "==> Krok 1/3: walidacja tłumaczeń"
python3 scripts/check-translations.py

echo
echo "==> Krok 2/3: czyszczenie poprzedniego builda"
rm -rf public/

echo
echo "==> Krok 3/3: build Hugo (baseURL: ${BASE_URL})"
# --noBuildLock : patrz komentarz w scripts/dev.sh — niezbędne na systemach
#   plików bez obsługi flock() (Android/Termux na pamięci współdzielonej,
#   dyski sieciowe, część woluminów Dockera). Bez tej flagi build kończy się
#   błędem "failed to acquire a build lock: function not implemented".
hugo --gc --minify --noBuildLock --baseURL "${BASE_URL}"

echo
echo "Gotowe. Wynik w katalogu public/:"
# Pokaż, co faktycznie powstało — szybka kontrola, czy są wszystkie języki
find public -maxdepth 2 -name "index.html" | sort
