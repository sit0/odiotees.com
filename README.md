# ODIO TEES — strona w Hugo (PL / EN / DE)

Strona zbudowana w [Hugo](https://gohugo.io) (statyczny generator stron).
Treść edytujesz **raz**, w jednym miejscu, po polsku i po angielsku/niemiecku
— wersje `/en/` i `/de/` powstają automatycznie **w momencie kompilacji**
(nie utrzymujesz osobnych plików HTML dla każdego języka).

Push na branch `main` na GitHubie automatycznie:
1. buduje stronę (Hugo generuje `/`, `/en/`, `/de/`),
2. publikuje wynik jako podgląd na GitHub Pages.

Nic więcej nie trzeba robić ręcznie — to jest właśnie sens tego repo.

---

## Spis treści

1. [Wymagania](#1-wymagania)
2. [Pierwsze wdrożenie (zrób to raz)](#2-pierwsze-wdrożenie-zrób-to-raz)
3. [Jak to działa — kompilacja i publikacja](#3-jak-to-działa--kompilacja-i-publikacja)
4. [Praca lokalna (podgląd na własnym komputerze)](#4-praca-lokalna-podgląd-na-własnym-komputerze)
5. [Struktura projektu](#5-struktura-projektu)
6. [Jak działają tłumaczenia](#6-jak-działają-tłumaczenia)
7. [Edycja treści — dla użytkownika nietechnicznego](#7-edycja-treści--dla-użytkownika-nietechnicznego)
8. [Edycja treści — dla programisty](#8-edycja-treści--dla-programisty)
9. [Dodawanie kolejnego języka](#9-dodawanie-kolejnego-języka)
10. [Własna domena zamiast adresu github.io](#10-własna-domena-zamiast-adresu-githubio)
11. [Ważne szczegóły techniczne](#11-ważne-szczegóły-techniczne)
12. [Rozwiązywanie problemów](#12-rozwiązywanie-problemów)

---

## 1. Wymagania

**Do samej publikacji na GitHub Pages przez GitHub Actions: żadne.**
Wszystko dzieje się na serwerach GitHuba — nie musisz nic instalować,
żeby strona się zbudowała i opublikowała po pushu.

Lokalny podgląd (opcjonalnie, przed pushem) wymaga:
- [Hugo, wersja **extended**](https://gohugo.io/installation/) — dokładna
  wersja użyta w CI jest zapisana w `.github/workflows/hugo.yml`
  (`HUGO_VERSION`, obecnie `0.166.0`). Warto mieć tę samą wersję lokalnie,
  żeby to, co widzisz u siebie, wyglądało tak samo jak na GitHub Pages.
  **Minimum to Hugo 0.158** — konfiguracja używa kluczy `locale` i `label`,
  wprowadzonych w tej wersji. Starsze Hugo ich nie rozpozna.
- Python 3 z `PyYAML` (`pip install pyyaml`) — do skryptu walidującego
  tłumaczenia. Nie jest potrzebny do samego builda.
- Konto GitHub i uprawnienia do repozytorium (do wdrożenia).

---

## 2. Pierwsze wdrożenie (zrób to raz)

1. **Załóż repozytorium na GitHubie** (jeśli jeszcze go nie masz) i wgraj do
   niego zawartość tego folderu (cały `hugo-site/`, łącznie z ukrytym
   folderem `.github/`):

   ```bash
   cd hugo-site
   git init
   git add .
   git commit -m "Initial commit: Hugo site (pl/en/de)"
   git branch -M main
   git remote add origin https://github.com/<twoj-uzytkownik>/<nazwa-repo>.git
   git push -u origin main
   ```

2. **Włącz GitHub Pages z trybem "GitHub Actions"** (to jest krok, którego
   nie da się zautomatyzować z poziomu repo — robi się go raz, ręcznie,
   w ustawieniach):
   - Wejdź w repo na GitHubie → **Settings** → **Pages** (menu po lewej).
   - W sekcji **Build and deployment** → **Source** wybierz
     **GitHub Actions** (NIE "Deploy from a branch").
   - Nie musisz nic więcej konfigurować — workflow w
     `.github/workflows/hugo.yml` sam się tym zajmie.

3. **Poczekaj na pierwszy build.** Po pushu z kroku 1 (albo od razu po
   zmianie w kroku 2, jeśli push już był) wejdź w zakładkę **Actions** w
   repo. Powinieneś zobaczyć uruchomiony workflow "Build and deploy Hugo
   site to GitHub Pages" z dwoma krokami: `build` i `deploy`. Gdy oba
   będą zielone (✅), strona jest opublikowana.

4. **Adres podglądu** pojawi się:
   - w zakładce **Settings → Pages** (u góry, "Your site is live at ..."),
   - oraz w podsumowaniu ukończonego joba `deploy` w zakładce Actions.

   Domyślnie będzie to `https://<twoj-uzytkownik>.github.io/<nazwa-repo>/`.

Od teraz **każdy kolejny `git push` na `main` automatycznie przebuduje i
odświeży opublikowaną stronę** — nie trzeba powtarzać kroku 2 ani 3.

---

## 3. Jak to działa — kompilacja i publikacja

Plik `.github/workflows/hugo.yml` (obszernie skomentowany — otwórz go, żeby
zobaczyć szczegóły) robi dokładnie to:

```
push na main
      │
      ▼
┌─────────────┐  1. instaluje Hugo (wersja przypięta w HUGO_VERSION)
│             │  2. pobiera kod repozytorium
│  job: build │  3. WALIDUJE TŁUMACZENIA — brak = build pada tutaj
│             │  4. buduje `hugo --gc --minify --baseURL ...`
└─────────────┘     → public/ z trzema wersjami językowymi
      │               (public/index.html, public/en/…, public/de/…)
      ▼
┌─────────────┐     wgrywa public/ jako "artefakt Pages"
│ job: deploy │ →   i publikuje go pod adresem *.github.io
└─────────────┘
```

Kluczowa rzecz: **`--baseURL` jest ustawiany automatycznie** przez krok
`actions/configure-pages` na faktyczny adres, pod którym GitHub akurat
hostuje tę stronę. Dzięki temu wszystkie linki, przełącznik języka i
`hreflang` działają poprawnie, mimo że strona żyje w podkatalogu
(`/nazwa-repo/`), a nie pod samym `/`.

Krok 3 istnieje, bo Hugo sam z siebie **nie przerywa** builda przy
brakującym tłumaczeniu — patrz [sekcja 8](#8-edycja-treści--dla-programisty).

Możesz też uruchomić build ręcznie, bez robienia pustego commita: zakładka
**Actions** → workflow "Build and deploy Hugo site to GitHub Pages" →
przycisk **Run workflow**.

---

## 4. Praca lokalna (podgląd na własnym komputerze)

Zainstaluj Hugo (extended) — instrukcje dla Twojego systemu:
https://gohugo.io/installation/. Sprawdź wersję:

```bash
hugo version
```

Do codziennej pracy dołączone są trzy skrypty w `scripts/`. Nie robią nic
magicznego — opakowują polecenia Hugo z właściwymi flagami, żeby nie trzeba
było ich pamiętać. Każdy jest opatrzony komentarzami w środku.

**Serwer z podglądem na żywo** (odświeża się automatycznie po zapisaniu
pliku):

```bash
cd hugo-site
./scripts/dev.sh
```

Otwórz `http://localhost:1313/`. Przełącznik języka w prawym górnym rogu
przełącza między `http://localhost:1313/`, `/en/` i `/de/`.

> Skrypt dodaje flagę `--disableFastRender`. Bez niej Hugo przy zmianach
> w `i18n/` i `data/` potrafi pokazywać starą treść — szybkie renderowanie
> nie śledzi dobrze tych plików. Jeśli uruchamiasz `hugo server` ręcznie,
> dodaj tę flagę sam.

**Walidacja tłumaczeń** (uruchom przed commitem):

```bash
python3 scripts/check-translations.py
```

Sprawdza, czy wszystkie pliki `i18n/*.yaml` mają ten sam zestaw kluczy,
czy żadna wartość nie jest pusta i czy każde pole tłumaczone w `data/*.yaml`
ma komplet języków. Szczegóły i uzasadnienie w [sekcji 8](#8-edycja-treści--dla-programisty).

**Pełny build produkcyjny** (to samo, co robi GitHub Actions):

```bash
./scripts/build.sh                       # baseURL = "/" (test lokalny)
./scripts/build.sh https://odiotees.com/ # baseURL pod docelową domenę
```

Skrypt waliduje tłumaczenia, czyści poprzedni build i uruchamia
`hugo --gc --minify`. Jeśli przechodzi lokalnie, przejdzie też w CI.

Wynik wyląduje w folderze `public/` (ignorowanym przez git — patrz
`.gitignore`). Możesz go otworzyć lokalnie albo wrzucić na dowolny
hosting, w tym na hosting Apache razem z dołączonym `static/.htaccess`
(patrz [sekcja 10](#10-własna-domena-zamiast-adresu-githubio)).

> Podając własny `baseURL`, **zawsze kończ go ukośnikiem**. Bez niego Hugo
> skleja adresy błędnie (`.../repoen/` zamiast `.../repo/en/`).

---

## 5. Struktura projektu

```
hugo-site/
├── hugo.toml                  # konfiguracja: języki, parametry globalne
├── content/
│   ├── _index.md              # PL (domyślny język) — front matter, BEZ treści
│   ├── _index.en.md           # EN — jw.
│   └── _index.de.md           # DE — jw.
├── i18n/                      # ⭐ proste teksty (nagłówki, akapity, etykiety)
│   ├── pl.yaml
│   ├── en.yaml
│   └── de.yaml
├── data/                      # ⭐ powtarzalne elementy (karty, linki, listy)
│   ├── collabs.yaml           # sekcja "Współprace"
│   ├── techniques.yaml        # sekcja "Techniki"
│   ├── archive.yaml           # sekcja "Archiwa"
│   └── places.yaml            # sekcja "Miejsca" (KIOSQ / TOWER)
├── layouts/
│   ├── _default/baseof.html   # szkielet HTML (head + header + stopka)
│   ├── _default/sitemap.xml   # sitemapa z alternatywami hreflang
│   ├── index.html             # strona główna — składa partiale w kolejności
│   ├── partials/               # jedna sekcja strony = jeden plik
│   │   ├── head.html          # <head>: meta, CSS, hreflang
│   │   ├── header.html        # logo, nawigacja, przełącznik języka
│   │   ├── hero.html
│   │   ├── manifest.html
│   │   ├── collabs.html
│   │   ├── techniques.html
│   │   ├── shop-banner.html
│   │   ├── places.html
│   │   ├── archive.html
│   │   ├── contact.html
│   │   ├── footer.html
│   │   └── scripts.html
│   └── robots.txt              # szablon /robots.txt (Hugo wstawia baseURL)
├── static/
│   └── .htaccess               # opcjonalne, tylko pod własny hosting Apache
├── scripts/                    # ⭐ skrypty pomocnicze (patrz sekcja 8)
│   ├── dev.sh                  # lokalny podgląd z auto-odświeżaniem
│   ├── build.sh                # lokalny build produkcyjny (to co robi CI)
│   └── check-translations.py   # walidator kompletności tłumaczeń
├── archetypes/default.md       # szablon dla `hugo new` (nieużywany na co dzień)
├── .github/workflows/hugo.yml  # ⭐ workflow build + deploy
└── README.md                   # ten plik
```

⭐ = pliki, które **edytujesz najczęściej** (treść strony).
Reszta to warstwa "jak to wygląda i jak się buduje" — zmieniana rzadziej.

---

## 6. Jak działają tłumaczenia

To jest sedno tego, o co prosiłeś: **tłumaczenia nie są osobnymi plikami
HTML**, tylko danymi, które Hugo łączy z szablonami *w trakcie kompilacji*.

Są dwa miejsca, w których mieszka tekst:

### a) `i18n/{pl,en,de}.yaml` — proste, pojedyncze teksty

Każdy klucz (np. `hero-h1-1`) ma swój odpowiednik w **każdym** z trzech
plików. W szablonie wygląda to tak:

```go-html-template
<h2>{{ i18n "manifest-h2" }}</h2>
```

Hugo, budując wersję angielską, sam sięgnie po `manifest-h2` z
`i18n/en.yaml`; budując polską — po `i18n/pl.yaml`. Ty w kodzie szablonu
nic nie zmieniasz — jeden szablon, trzy języki.

**Jeśli zapomnisz dodać klucz w jednym z języków**, Hugo dla tej strony po
prostu użyje tekstu z języka domyślnego (polskiego) jako zapasowego —
strona się zbuduje, ale będzie zawierać polski tekst tam, gdzie miał być
np. angielski. To jedyny "błąd", jaki może się zdarzyć — nic się nie
wywali, ale warto to zauważyć podczas przeglądu (patrz
[sekcja 8](#8-edycja-treści--dla-programisty), skrypt sprawdzający spójność).

### b) `data/*.yaml` — powtarzalne listy (karty, linki)

Rzeczy takie jak 4 karty w sekcji "Techniki" czy 6 linków w "Archiwach" nie
pasują do prostego `i18n` (to nie jest jeden tekst, tylko lista obiektów).
Dla nich każdy element listy ma pole tekstowe zagnieżdżone per-język,
np. w `data/techniques.yaml`:

```yaml
- title:
    pl: "Folia hologramowa"
    en: "Holographic foil"
    de: "Hologrammfolie"
  desc:
    pl: "Nakładam ją ręcznie…"
    en: "I apply it by hand…"
    de: "Ich trage sie von Hand auf…"
```

a szablon (`layouts/partials/techniques.html`) w pętli wybiera właściwy
język:

```go-html-template
{{ range hugo.Data.techniques }}
  <h3>{{ index .title $lang }}</h3>
  <p>{{ index .desc $lang }}</p>
{{ end }}
```

Dodanie piątej techniki = dopisanie jednego bloku `- title: ... desc: ...`
w pliku danych. Szablon automatycznie pokaże nową kartę we wszystkich
trzech językach, bez zmiany kodu HTML.

### c) Adresy, uchwyty social media, nazwiska — bez tłumaczenia

Rzeczy, które są takie same we wszystkich językach (np. `name:
"Jakub Pieczarkowski"`, adres `ul. 1 Maja 64, Jelenia Góra`, adres URL do
Instagrama) są zapisane jako zwykły, płaski tekst — bez zagnieżdżania
`pl/en/de` — dokładnie po to, żeby nie trzeba było ich niepotrzebnie
powielać.

---

## 7. Edycja treści — dla użytkownika nietechnicznego

Nie musisz instalować niczego na komputerze. Wszystko robi się w
przeglądarce, na stronie GitHub.com.

### Zmiana istniejącego tekstu (np. opisu w sekcji "Manifest")

1. Wejdź na stronę repozytorium na GitHub.com.
2. Wejdź w folder `i18n`, a potem w plik odpowiedniego języka, np.
   `pl.yaml` (dla tekstu polskiego).
3. Kliknij ikonę ołówka (**Edit this file**) w prawym górnym rogu
   podglądu pliku.
4. Znajdź linijkę z tekstem, który chcesz zmienić — tekst jest zawsze w
   cudzysłowie, po `other:`, np.:
   ```yaml
   manifest-h2:
     other: "Recykling jako punkt wyjścia"
   ```
   Zmień tekst **wewnątrz cudzysłowów**. Nie ruszaj nazwy klucza
   (`manifest-h2:`) ani słowa `other:` — to są "etykiety", po których Hugo
   rozpoznaje, gdzie wstawić dany tekst w szablonie.
5. Jeśli Twój nowy tekst sam zawiera znak cudzysłowu `"`, poprzedź go
   ukośnikiem: `\"` (np. `"To jest \"ważne\" zdanie"`).
6. Jeśli chcesz zmienić ten sam fragment w innym języku, powtórz kroki
   2–5 dla `en.yaml` / `de.yaml`.
7. Na dole strony kliknij **Commit changes...** → zostaw zaznaczoną opcję
   **Commit directly to the `main` branch** → **Commit changes**.
8. Gotowe. W ciągu 1–2 minut GitHub sam przebuduje i opublikuje stronę z
   Twoją zmianą — możesz to obserwować w zakładce **Actions** (zielony
   ✅ = opublikowane). Nie musisz nic dodatkowo klikać ani odświeżać.

### Zmiana opisu jednej z kart (np. jednej z technik albo jednej ze
współprac)

To samo, tylko plik jest w folderze `data/`, np. `data/techniques.yaml`.
Struktura jest trochę inna — każdy blok zaczyna się myślnikiem `-` i ma
osobny tekst dla każdego języka w tym samym pliku:

```yaml
- title:
    pl: "Farba UV"
    en: "UV paint"
    de: "UV-Farbe"
  desc:
    pl: "Grafiki, które świecą w ultrafiolecie…"
    en: "Graphics that glow under ultraviolet light…"
    de: "Grafiken, die unter Schwarzlicht leuchten…"
```

Zmieniasz tekst po `pl:`, `en:` lub `de:` — analogicznie jak w `i18n/`.
Zwróć uwagę na **wcięcia** (spacje na początku linii) — muszą zostać
dokładnie takie same, jak w reszcie pliku (YAML jest wrażliwy na
wcięcia). Najbezpieczniej: kopiuj istniejącą linijkę i zmieniaj w niej
tylko tekst, nie strukturę.

### Czego NIE zmieniać samodzielnie (bez pomocy programisty)

- Plików w `layouts/` (kod szablonów — zmiana układu strony, dodawanie
  nowych sekcji).
- `hugo.toml` (konfiguracja języków, adresy globalne).
- `.github/workflows/hugo.yml` (proces publikacji).

Zmiana tekstu w `i18n/` i `data/` jest w pełni bezpieczna — najgorsze, co
może się zdarzyć przy literówce w YAML, to że build w zakładce Actions
zakończy się na czerwono (❌) zamiast zielono — wtedy **stara wersja
strony zostaje online**, nic się nie psuje "na żywo". Wystarczy poprawić
plik i zacommitować ponownie.

---

## 8. Edycja treści — dla programisty

### Workflow dnia codziennego

1. `git pull`, ewentualnie nowy branch.
2. Edytuj `i18n/*.yaml`, `data/*.yaml` (treść) albo `layouts/**/*.html`
   (układ/HTML/CSS).
3. Podejrzyj lokalnie: `hugo server -D` → `http://localhost:1313/`.
4. Commit + push na `main` (albo PR → merge do `main`) → CI robi resztę.

### Dodanie nowego, prostego tekstu (klucz i18n)

1. Dodaj klucz do **wszystkich trzech** plików `i18n/pl.yaml`,
   `i18n/en.yaml`, `i18n/de.yaml` w tym samym formacie:
   ```yaml
   moj-nowy-klucz:
     other: "Tekst po polsku"
   ```
2. Użyj go w odpowiednim partialu: `{{ i18n "moj-nowy-klucz" }}`.

### Dodanie nowej karty do listy (np. piątej technologii)

Dopisz kolejny blok na końcu np. `data/techniques.yaml`, zachowując
strukturę (`title.pl/en/de`, `desc.pl/en/de`). Nic w `layouts/` nie trzeba
zmieniać — pętla `range` w `techniques.html` obejmie nowy element
automatycznie. **Uwaga:** CSS siatki kart (`.card-grid`) i kolorowanie
kropek (`.patch:nth-child(n) .dot`) w `layouts/partials/head.html` są
napisane pod 4 elementy — przy 5. karcie pokoloruj piątą kropkę ręcznie
albo zaakceptuj, że powtórzy kolor pierwszej.

### Dodanie nowej sekcji na stronie

1. Utwórz nowy plik `layouts/partials/moja-sekcja.html` z markupem
   (wzoruj się na istniejących partiach, np. `manifest.html`).
2. Dodaj potrzebne klucze do `i18n/*.yaml` (albo nowy plik w `data/`,
   jeśli sekcja ma powtarzalną listę).
3. Dodaj `{{ partial "moja-sekcja.html" . }}` w `layouts/index.html`, w
   odpowiednim miejscu kolejności.
4. Jeśli sekcja potrzebuje własnego CSS, dopisz go w `<style>` w
   `layouts/partials/head.html` (cały CSS strony celowo siedzi w jednym
   miejscu, tak jak w oryginalnym pojedynczym pliku HTML, żeby było go
   łatwo przeglądać).

### Sprawdzenie spójności tłumaczeń przed commitem

```bash
python3 scripts/check-translations.py
```

Wymaga Pythona z `PyYAML` (`pip install pyyaml`). Skrypt sprawdza trzy rzeczy:

1. **Parzystość kluczy w `i18n/*.yaml`** — czy każdy język ma dokładnie ten
   sam zestaw kluczy. Klucz obecny tylko w części plików to błąd niezależnie
   od tego, w którą stronę.
2. **Puste wartości** — klucz istnieje, ale tekst jest pusty.
3. **Kompletność pól w `data/*.yaml`** — każde pole tłumaczone (rozpoznawane
   po tym, że jest słownikiem z kodami języków) musi mieć komplet języków.

Skrypt **sam wykrywa listę języków** z nazw plików w `i18n/`, więc po dodaniu
kolejnego języka nie trzeba go edytować.

Przykładowe wyjście przy błędzie:

```
Wykryte języki: de, en, pl

ZNALEZIONE PROBLEMY:

  - i18n/de.yaml: BRAKUJE klucza 'nav-places'
  - techniques.yaml[0].title: brakuje tłumaczenia 'de'

Razem: 2. Build przerwany.
```

**Ten skrypt jest wpięty w CI** jako krok poprzedzający `hugo`
(patrz `.github/workflows/hugo.yml`, krok „Sprawdź kompletność tłumaczeń").
Przy brakującym tłumaczeniu build na GitHubie kończy się błędem z czytelnym
komunikatem, zamiast opublikować niekompletną stronę.

**Dlaczego to jest w ogóle potrzebne:** Hugo przy brakującym tłumaczeniu
**nie przerywa builda**. Po cichu wstawia tekst z języka domyślnego
(polskiego) albo pusty ciąg — patrz [sekcja 6](#6-jak-działają-tłumaczenia).
To rozsądne zachowanie dla dużych serwisów (lepiej pokazać cokolwiek niż
pustą stronę), ale przy trzech językach i jednym landing page'u oznacza, że
literówka przechodzi niezauważona aż na produkcję. Skrypt zamienia cichą
awarię w głośną.

---

## 9. Dodawanie kolejnego języka

Przykład: dodanie francuskiego (`fr`).

1. **`hugo.toml`** — dopisz blok języka:
   ```toml
   [languages.fr]
     label = "Français"
     locale = "fr-FR"
     weight = 4
     title = "ODIO TEES — pièces uniques imprimées à la main"
     [languages.fr.params]
       description = "…"
   ```
2. **`content/_index.fr.md`** — skopiuj `content/_index.en.md` i zmień
   komentarz/`title` w front matter.
3. **`i18n/fr.yaml`** — skopiuj `i18n/en.yaml` i przetłumacz wszystkie
   wartości po `other:` (zachowaj identyczne klucze).
4. **`data/*.yaml`** — w każdym pliku dopisz `fr:` obok istniejących
   `pl:/en:/de:` w każdym polu tekstowym.
5. Gotowe — przełącznik języka w nagłówku (`header.html`) **nie wymaga
   zmian**, bo generuje się automatycznie z `.AllTranslations`; podobnie
   `hreflang` w `head.html` i sitemapy (Hugo robi to samo dla każdego
   zdefiniowanego języka).
6. `hugo server -D` lokalnie → sprawdź `/fr/` → commit + push.

---

## 10. Własna domena zamiast adresu github.io

Gdy będziesz gotów zastąpić `*.github.io` własną domeną (np.
`odiotees.com`):

1. W repo: **Settings → Pages → Custom domain** → wpisz domenę → Save.
   GitHub sam utworzy plik `CNAME` w publikowanej wersji (dopisze go
   automatycznie do brancha Pages — **nie musisz** ręcznie tworzyć
   `static/CNAME`, chyba że wolisz mieć to w repo na stałe, wtedy dodaj
   plik `static/CNAME` z samą nazwą domeny w środku).
2. U rejestratora domeny ustaw rekordy DNS zgodnie z instrukcją GitHuba
   (zwykle `ALIAS`/`ANAME` albo 4 rekordy `A` na adresy GitHub Pages +
   rekord `CNAME` dla `www`).
3. Poczekaj na propagację DNS i na to, aż GitHub wystawi certyfikat HTTPS
   (dzieje się automatycznie, bywa, że trwa do kilkudziesięciu minut).
4. **`static/.htaccess`** w tym repo dotyczy TYLKO hostingu na własnym
   serwerze Apache (np. gdybyś kiedyś przeniósł stronę poza GitHub
   Pages) — GitHub Pages go nie odczytuje i nie musisz się nim
   przejmować przy hostowaniu na GitHub Pages, nawet z własną domeną.

---

## 11. Ważne szczegóły techniczne

- **Wersja Hugo jest przypięta** w `.github/workflows/hugo.yml`
  (`HUGO_VERSION`). To celowe — gwarantuje, że build w CI zawsze wygląda
  tak samo, niezależnie od tego, kiedy go uruchomisz. Aby zaktualizować
  Hugo: sprawdź najnowszą wersję na
  https://github.com/gohugoio/hugo/releases, zainstaluj ją lokalnie,
  odpal `hugo server -D` i sprawdź, czy nic się nie posypało, dopiero
  potem podbij `HUGO_VERSION` w workflow.
- **`--baseURL` na produkcji** pochodzi z `actions/configure-pages`, NIE
  z `hugo.toml` (tam jest tylko wartość domyślna `"/"` do pracy
  lokalnej). Nie edytuj `baseURL` w `hugo.toml`, żeby "naprawić" adres
  na GitHub Pages — to nic nie da, bo flaga z CLI go nadpisuje.
- **Obrazy i wideo w hero** są linkowane z zewnętrznego adresu
  `https://odiotees.com/static/...` (parametry `logoImage`, `heroVideo`
  w `hugo.toml`) — tak samo jak w oryginalnej stronie. Nie są
  kopiowane do repozytorium. Jeśli kiedyś zechcesz hostować je razem ze
  stroną, wrzuć pliki do `static/img/...` i zmień wartości w
  `hugo.toml` na `/img/...` (Hugo skopiuje wszystko z `static/` do
  `public/` bez zmian).
- **Sitemap i `robots.txt` generują się przy buildzie.** `robots.txt`
  powstaje z szablonu `layouts/robots.txt` — Hugo wstawia do niego
  prawdziwy, aktualny `baseURL`, więc adres sitemapy jest poprawny
  zarówno na podglądzie GitHub Pages, jak i na docelowej domenie.
  Sitemapa używa **własnego szablonu** `layouts/_default/sitemap.xml`,
  a nie domyślnego. Powód: domyślna sitemapa Hugo nie zawiera znaczników
  `<xhtml:link rel="alternate" hreflang="...">`, a Google zaleca je
  właśnie w sitemapie przy serwisach wielojęzycznych. Szablon buduje tę
  listę z `.AllTranslations`, więc przy dodaniu języka aktualizuje się sam.
- **`hreflang` w `<head>`** generuje się automatycznie z
  `.AllTranslations`, więc zawsze jest zgodny z faktycznie zbudowanymi
  językami — nie trzeba go ręcznie aktualizować przy dodaniu/usunięciu
  języka (poza samym dodaniem języka wg [sekcji 9](#9-dodawanie-kolejnego-języka)).
- **Minifikacja HTML/CSS/JS** dzieje się przez flagę `--minify` w
  workflow — build lokalny bez tej flagi (`hugo server`) daje
  nieminifikowany, czytelny HTML, przydatny do debugowania.
- **`concurrency`** w `hugo.yml` pilnuje, żeby dwa buildy nie publikowały
  się jednocześnie, gdyby ktoś zrobił dwa pushe pod rząd — drugi poczeka,
  aż pierwszy się skończy.
- **`disableKinds`** w `hugo.toml` wyłącza generowanie nieużywanych typów
  stron (RSS, taxonomie, 404) — to jednostronicowa witryna typu
  "one-pager", więc te typy tylko zaśmiecałyby build.
- **Brak motywu (theme) Hugo** — cały layout jest napisany od zera w
  `layouts/`, celowo, żeby zachować dokładnie oryginalny wygląd strony
  bez narzucania cudzej struktury CSS.

---

## 12. Rozwiązywanie problemów

**`WARN deprecated: .Site.Data was deprecated ... Use hugo.Data instead.`**

Hugo 0.156 przeniósł dostęp do plików z `data/` z `.Site.Data` na globalną
funkcję `hugo.Data`. To tylko ostrzeżenie — build przechodzi — ale aktualne
szablony w tym projekcie już używają `hugo.Data` (w `collabs.html`,
`techniques.html`, `archive.html`, `places.html`). Jeśli widzisz to
ostrzeżenie, masz starszą wersję tych plików — podmień je na te z paczki.

```go-html-template
{{ range hugo.Data.techniques }}   {{/* aktualnie */}}
{{ range .Site.Data.techniques }}  {{/* przestarzałe */}}
```

**`can't evaluate field DefaultContentLanguage in type interface {}`**

Hugo **nie udostępnia** w szablonach pola z wartością
`defaultContentLanguage` z konfiguracji. Szablony biorą ją z parametru
`defaultLang` w `hugo.toml`, sekcja `[params]`:

```toml
[params]
  defaultLang = "pl"
```

Jest on potrzebny do wygenerowania znacznika `hreflang="x-default"`
(w `layouts/partials/head.html` i w sitemapie). **Ta wartość musi być
zgodna z `defaultContentLanguage`** — przy zmianie języka domyślnego
zmieniasz w obu miejscach. `scripts/check-translations.py` sprawdza tę
zgodność i przerwie build, jeśli się rozjadą.

Jeśli widzisz ten błąd, masz starą wersję `hugo.toml` lub szablonów —
podmień je na te z paczki.

**`failed to acquire a build lock: ... function not implemented`**

Hugo tworzy plik `.hugo_build.lock` i blokuje go wywołaniem systemowym
`flock()`. Część systemów plików tego nie obsługuje — wtedy build pada,
niezależnie od tego, czy plik blokady skasujesz (Hugo utworzy go od nowa).

Dotyczy to najczęściej:
- **Androida / Termuksa**, gdy projekt leży w pamięci współdzielonej
  (`~/storage/downloads/...`, `/sdcard/...`) — to warstwa FUSE bez `flock()`
- dysków sieciowych (SMB, NFS)
- niektórych woluminów Dockera na macOS/Windows

Rozwiązania, od najlepszego:

1. **Użyj dołączonych skryptów** — mają już flagę `--noBuildLock`:
   ```bash
   ./scripts/dev.sh
   ./scripts/build.sh
   ```
2. **Dodaj flagę ręcznie**, jeśli wołasz Hugo bezpośrednio:
   ```bash
   hugo --noBuildLock
   hugo server --noBuildLock
   ```
3. **Przenieś projekt poza pamięć współdzieloną** (zalecane na Termuksie).
   Katalog domowy Termuksa to zwykły system plików i obsługuje `flock()`:
   ```bash
   cp -r ~/storage/downloads/ODIO/odio-tees ~/odio-tees
   cd ~/odio-tees
   hugo    # już bez dodatkowych flag
   ```
   Przy okazji rozwiązuje to inne problemy pamięci współdzielonej na
   Androidzie — brak uprawnień wykonywania (`chmod +x` na skryptach nie
   działa) i gubione uprawnienia plików przy operacjach gitowych.

Sama blokada chroni wyłącznie przed dwoma równoległymi buildami w tym samym
katalogu. Przy pracy jednoosobowej jej wyłączenie nic nie kosztuje.

**`WARN deprecated: project config key languageCode / languageName ...`**

To ostrzeżenia, nie błędy — build przechodzi. Hugo 0.158 zmienił nazwy
dwóch kluczy konfiguracji. Aktualna wersja `hugo.toml` używa już nowych:

| Stary klucz (przestarzały) | Nowy klucz |
|---|---|
| `languageCode` | `locale` |
| `languageName` | `label` |

Jeśli widzisz te ostrzeżenia, masz starszą wersję `hugo.toml` — podmień ją
na tę z paczki. Nowe nazwy wymagają Hugo **0.158 lub nowszego**.

**Build w zakładce Actions kończy się na czerwono (❌).**
Kliknij w niego → rozwiń krok `Zbuduj stronę` → w logu Hugo zwykle
dokładnie mówi, w którym pliku i linii jest błąd (najczęściej: brakujący
cudzysłów albo złe wcięcie w pliku YAML w `i18n/` lub `data/`). Poprzednia,
działająca wersja strony **zostaje opublikowana** — błąd nie zdejmuje
strony z powietrza.

**Strona w GitHub Pages pokazuje 404 mimo zielonego builda.**
Sprawdź w **Settings → Pages**, czy "Source" to na pewno **GitHub
Actions** (nie "Deploy from a branch") — patrz [sekcja 2](#2-pierwsze-wdrożenie-zrób-to-raz),
krok 2. To najczęstsza przyczyna.

**Jeden z języków pokazuje polski tekst zamiast tłumaczenia.**
Brakuje odpowiedniego klucza w `i18n/en.yaml` lub `i18n/de.yaml` (albo pola
`en`/`de` w pliku z `data/`). Zobacz skrypt sprawdzający w
[sekcji 8](#8-edycja-treści--dla-programisty).

**Zmiana w `i18n/`/`data/` nie widoczna na stronie.**
Sprawdź zakładkę Actions — może build jeszcze trwa (zwykle ok. minuty) albo
zakończył się błędem. Odśwież przeglądarkę z pominięciem cache
(Ctrl/Cmd+Shift+R), bo GitHub Pages i przeglądarki potrafią chwilę
trzymać starą wersję w cache.

**Chcę cofnąć błędną zmianę.**
Na GitHub.com: zakładka **Commits** → znajdź poprzedni, dobry commit →
"..." → **Revert** (utworzy nowy commit cofający zmianę, automatycznie
odpali nowy build). Lokalnie: `git revert <hash>` + `git push`.
