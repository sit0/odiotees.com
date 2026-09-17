#!/usr/bin/env bash
# ============================================================================
# scripts/dev.sh — lokalny podgląd strony z automatycznym odświeżaniem.
#
# Uruchamia serwer deweloperski Hugo pod http://localhost:1313/
# Każda zmiana w i18n/*.yaml, data/*.yaml lub layouts/* jest od razu
# widoczna w przeglądarce (bez ręcznego odświeżania).
#
# Użycie:
#   ./scripts/dev.sh
#
# Przydatne adresy po starcie:
#   http://localhost:1313/      -> wersja polska
#   http://localhost:1313/en/   -> wersja angielska
#   http://localhost:1313/de/   -> wersja niemiecka
# ============================================================================

set -euo pipefail

# Przejdź do katalogu głównego projektu, niezależnie skąd skrypt odpalono
cd "$(dirname "$0")/.."

# Sprawdź, czy Hugo jest w ogóle zainstalowane — czytelny komunikat
# zamiast "command not found"
if ! command -v hugo >/dev/null 2>&1; then
  echo "BŁĄD: nie znaleziono Hugo. Instrukcja instalacji: README.md, sekcja 'Wymagania'."
  exit 1
fi

echo "Uruchamiam serwer deweloperski Hugo..."
echo "PL: http://localhost:1313/   EN: http://localhost:1313/en/   DE: http://localhost:1313/de/"
echo

# --noBuildLock : Hugo domyślnie tworzy plik .hugo_build.lock i blokuje go
#   wywołaniem flock(). Część systemów plików tego nie obsługuje i build
#   pada z "failed to acquire a build lock: function not implemented".
#   Dotyczy to m.in. współdzielonej pamięci Androida (Termux,
#   /storage/... lub /sdcard/...), dysków sieciowych SMB/NFS i niektórych
#   woluminów Dockera. Blokada chroni tylko przed dwoma równoległymi
#   buildami w tym samym katalogu — przy pracy jednoosobowej nic nie tracimy.
# --buildDrafts : pokazuje też wpisy oznaczone jako draft: true
# --disableFastRender : pełne przebudowanie przy każdej zmianie; wolniejsze,
#   ale eliminuje "duchy" starej treści przy pracy z plikami i18n/data
hugo server \
  --noBuildLock \
  --buildDrafts \
  --disableFastRender
