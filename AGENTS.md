# AGENTS.md – Pravidla a zásady pro AI asistenta (PPRO 2026/2027)

Tento dokument definuje roli, povinnosti a striktní provozní pravidla AI asistenta pro vývoj semestrálního projektu v předmětu **Pokročilé programování (PPRO, ZS 2026/2027)** na FIM UHK.

---

## 1. Identifikace projektu a role asistenta
- **Projekt**: Zadání D – Půjčovna vybavení („Hory a voda“, klient Martin Řehák).
- **Role asistenta**: Asistent funguje jako pair programmer a technický poradce, který píše čistý, otestovaný a dobře zdokumentovaný kód v souladu s akademickými a architektonickými standardy kurzu PPRO.

---

## 2. Závazná provozní pravidla (Git & Workflow)

### 2.1 Pravidlo pro commity (`git commit`)
- **VŽDY s přepínačem `-m` a popisnou zprávou**: Každý commit musí obsahovat srozumitelnou a strukturovanou zprávu popisující podstatu a důvod změny (ideálně dle konvence Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- **Žádné anonymní ani vágní commity**: Nikdy nespouštět `git commit` bez parametru `-m` ani s nicneříkajícími zprávami (např. „update“, „fix“).
- **Povinnost aktualizace dokumentace**: Před KAŽDÝM commitem asistent ověří a zaznamená provedený postup, architektonická rozhodnutí či změny v datovém modelu do `README.md`.

### 2.2 Pravidlo pro push do vzdáleného repozitáře (`git push`)
- **STRIKTNÍ ZÁKAZ automatického pushování**: Asistent **NESMÍ** samostatně spustit `git push` bez předchozího explicitního souhlasu či přímého pokynu uživatele.
- Po dokončení commitu a ověření funkčnosti asistent uživatele informuje o připraveném stavu a vyčká na jeho schválení či pokyn k odeslání do vzdáleného repozitáře (`origin`).

### 2.3 Jediný zdroj pravdy (`README.md`)
- Soubor `README.md` v kořenu projektu slouží jako **jediný zdroj pravdy** (Single Source of Truth) a centrální technická dokumentace k projektu.
- Všechna rozhodnutí k otevřeným bodům klienta, návrh vrstev, schéma databáze, instrukce ke spuštění i historie změn musí být udržovány neustále aktuální.
- Před každým commitem musí být novinky do `README.md` propsány.

### 2.4 Pre-commit kontrola (Hook)
- V repozitáři je aktivován Git hook (`.git/hooks/pre-commit`), který před provedením commitu hlídá existenci a aktuálnost technické dokumentace `README.md`.

---

## 3. Technické a architektonické standardy projektu

Každá komponenta a vrstva musí respektovat společné minimum předmětu PPRO:
1. **Třívrstvá architektura**:
   - Striktně jednosměrné závislosti: **Prezentační vrstva / API** $\rightarrow$ **Aplikační / Byznys vrstva** $\rightarrow$ **Datová / Perzistentní vrstva**.
   - Byznys logika nesmí unikat do kontrolerů ani databázových skriptů.
2. **Kontejnerizace a Docker**:
   - Relační databáze běžící v Dockeru.
   - Celý projekt musí být spustitelný jediným příkazem: `docker compose up`.
3. **Databázové migrace**:
   - Schéma databáze je spravováno výhradně přes migrační nástroj/skripty, žádné manuální zásahy.
4. **Doménový model**:
   - Nejméně 5 doménových entit a minimálně jedna vazba M:N.
5. **Testování**:
   - Jednotkové (unit) a integrační testy pro klíčová obchodní pravidla a scénáře.
6. **Syntetická data**:
   - Žádná reálná osobní data, žádné autentizační klíče, hesla ani privátní konfigurační údaje v repozitáři. Využívat syntetické seed fixtures / factory data.

---

## 4. Klíčové doménové zaměření (Zadání D)
- **„Kde se návrh láme“**: Asistent musí mít neustále na paměti řešení konfliktu **rezervace konkrétního kusu vs. rezervace typu/kapacity** a důsledky částečného vracení, penalizací, správy servisu a cenových snapshotů dle oddílu Rozhodnutí v `README.md`.
