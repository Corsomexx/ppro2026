# Půjčovna vybavení „Hory a voda“ (PPRO 2026/2027)

> **Semestrální projekt předmětu Pokročilé programování (PPRO)**  
> Fakulta informatiky a managementu, Univerzita Hradec Králové (ZS 2026/2027)  
> **Vybrané zadání**: Zadání D – Půjčovna vybavení  
> **Jediný zdroj pravdy (Single Source of Truth) a technická dokumentace projektu**

---

## 1. Kontext a zadání klienta

- **Klient**: Martin Řehák, půjčovna *Hory a voda*.
- **Činnost**: Půjčování zimního (lyže, snowboardy, boty, hole) a letního vybavení (lodě, pádla, vesty). Sezóna je krátká, nárazová a o víkendech se tvoří dlouhé fronty.
- **Původní stav**: Papírový sešit, inventární čísla napsaná lihovkou přímo na vybavení, telefonické rezervace zaznamenávané na lístečky nad pultem. Dochází k chybám (dvojitá rezervace stejného kusu lyží), v ranní špičce vzniká chaos a klient situaci řeší improvizovanými slevami.

---

## 2. Přehled požadavků

### 2.1 Funkční požadavky (Co klient chce)
1. **Jednotlivé kusy vybavení**: Každý kus má inventární číslo, kategorii, velikost, rok pořízení a aktuální stav opotřebení. Dva totožné páry lyží tvoří dva samostatné záznamy.
2. **Kategorie vybavení**: Lyže, snowboardy, boty, hole, lodě, vesty apod. Cenotvorba se odvíjí od kategorie.
3. **Zákazníci**: Evidence zákazníků (jméno, příjmení, telefon, číslo dokladu totožnosti, výše a složení kauce).
4. **Výpůjčky**: Výpůjčka obsahuje více kusů vybavení, eviduje sjednané období (od – do) a tentýž inventární kus se v čase půjčuje opakovaně.
5. **Rezervace předem**: Rezervace termínu dopředu (např. telefonát v úterý na víkend).
6. **Vrácení po částech**: Možnost vrátit část výpůjčky dříve (např. lyže vráceny v poledne, boty až večer).
7. **Servisní evidence**: Vyřazení kusu z oběhu po dobu servisu. Přehled o tom, které kusy jsou v servisu a jak dlouho.
8. **Ceník podle kategorie a počtu dní**: Flexibilní ceník; víkend se počítá jako dva dny s vyzvednutím již v pátek odpoledne.
9. **Manažerské přehledy**:
   - Co je aktuálně vypůjčeno („venku“).
   - Co mělo být vráceno a nebylo (prodlení).
   - Frekvence výpůjček jednotlivých kusů (podklad pro nákup a obnovu fondu).
   - Ranní přehled volného vybavení na pultu.

### 2.2 Obchodní pravidla (Na čem klient trvá)
- **Zákaz kolize termínů**: Jeden kus nesmí být přiřazen ve dvou překrývajících se výpůjčkách či rezervacích.
- **Blokace servisu**: Kus nacházející se ve stavu servisu nelze půjčit ani pro něj potvrdit rezervaci.
- **Penalizace za prodlení**: Za pozdní vrácení je automaticky účtováno penále za každý započatý den prodlení.
- **Nenávratnost historie**: Historie výpůjček a servisních úkonů se fyzicky nemaže (slouží pro reklamace a analýzu životnosti).

### 2.3 Přání a nálady klienta (Co klient prohodil mimochodem)
- *„Nejvíc mi pomůže, když v sobotu ráno uvidím na jedné obrazovce, co je volné.“* $\rightarrow$ Dashboard dostupnosti na hlavní obrazovce.
- *„Kauci beru v hotovosti, to do počítače dávat nemusíme.“* $\rightarrow$ Systém eviduje stav složené/vrácené kauce pro případné započtení škody, ale nefunguje jako pokladní terminál.
- *„Někdy dám slevu, to je moje věc.“* $\rightarrow$ Možnost zadat manuální slevu na celou výpůjčku či položku.
- *„Kdyby to šlo tisknout, tak bych tiskl smlouvu.“* $\rightarrow$ Generování tiskového protokolu/smlouvy o výpůjčce.

---

## 3. Rozhodnutí k otevřeným bodům zadání (Architecture Decision Records)

Tento oddíl formalizuje rozhodnutí pro 5 klíčových neujasněných bodů zadání vyžadovaných specifikací PPRO.

### Rozhodnutí 1: Rezervace – konkrétní kus vs. typ vybavení („Kde se návrh láme“)
- **Kontext**: Zákazník při telefonátu požaduje např. „lyže 170 cm“, nikoliv inventární číslo 412. Přímé vázání rezervace na jeden konkrétní kus vytváří rigidní systém náchylný k selhání (např. při neplánovaném servisu daného kusu).
- **Rozhodnutí**: Systém implementuje **dvoufázový model alokace kapacity**:
  1. *Fáze rezervace*: Zákazník rezervuje **typ a velikostní kategorii** (např. Kategorie: Sjezdové lyže, Velikost: 170 cm). Systém ověří dostupnou kapacitu v daném termínu a vytvoří rezervaci (`ReservationItem`), která sníží volnou kapacitu pro daný slot.
  2. *Fáze výdeje*: Při fyzickém převzetí zákazníkem na přepážce systém nabídne volné kusy odpovídající specifikaci a obsluha naskenuje/přiřadí konkrétní inventární kus (`EquipmentItem`), čímž se vytvoří aktivní položka výpůjčky (`RentalItem`). Pro specifické požadavky (VIP zákazník trvá na konkrétním modelu) systém volitelně umožňuje i před-přiřazení konkrétního kusu.
- **Důvod**: Odstraňuje zmatky při ranním odbavování, umožňuje flexibilní záměnu kusů stejné specifikace a zabraňuje neoprávněnému blokování celého provozu.

### Rozhodnutí 2: Platnost rezervace a expirace („do desíti“)
- **Kontext**: Rezervace na víkend jsou obvykle drženy do určité hodiny (např. 10:00), po které hrozí, že nevyzvednuté kusy zablokují odbavení čekajících zájemců ve frontě.
- **Rozhodnutí**: Rezervace má explicitní atribut `validUntil` (datum a čas). Po uplynutí termínu (s konfigurovatelnou tolerancí 15 minut) je rezervace v přehledu označena jako **prošlá** a systém umožní její automatické i manuální stornování (`EXPIRED`), čímž se kapacita okamžitě uvolní do volného fondu pro zákazníky na prodejně. Obsluha má možnost u rezervace zaznamenat telefonické prodloužení platnosti jedním kliknutím.
- **Důvod**: Chrání půjčovnu před ušlým ziskem v ranní špičce, kdy před obchodem stojí fronta.

### Rozhodnutí 3: Evidence poškození a vazba na kauci
- **Kontext**: Poškození je dosud evidováno neformálně. Je nutné určit, zda se váže ke kusu, k výpůjčce, nebo ke kauci.
- **Rozhodnutí**: Zavádí se samostatná entita `DamageRecord`. Poškození se primárně váže ke konkrétnímu inventárnímu kusu (`EquipmentItem`) a konkrétní položce výpůjčky (`RentalItem`). Záznam obsahuje popis vady, fotodokumentaci/poznámku a finanční vyčíslení škody. Tato škoda je při vyrovnání automaticky odečtena z vratné kauce zákazníka. Zároveň se stav opotřebení daného kusu přehodnotí, a pokud je poškození vážné, je kus automaticky přesunut do stavu `IN_SERVICE`.
- **Důvod**: Zajišťuje právní i finanční dohledatelnost (kdo škodu způsobil a jak byla uhrazena) a zároveň udržuje reálný technický stav vybavení.

### Rozhodnutí 4: Částečné vrácení a penalizace
- **Kontext**: Zákazník může vrátit část vypůjčených položek dříve než zbytek (např. lyže v poledne, boty až večer nebo další den).
- **Rozhodnutí**: Každá položka výpůjčky (`RentalItem`) vystupuje jako samostatně stavový prvek s vlastním časem vrácení (`returnedAt`) a stavem (`BORROWED`, `RETURNED`, `LATE_RETURNED`). Výpůjčka (`Rental`) zůstává ve stavu `ACTIVE` až do vrácení poslední položky. Penále za pozdní vrácení se počítá **odděleně za každý nevrácený kus** podle denní sazby jeho kategorie za každý započatý den prodlení.
- **Důvod**: Férový a transparentní výpočet pro zákazníka (neplatí penále za kusy, které vrátil včas) a přesná evidence, co se ještě nachází u zákazníka.

### Rozhodnutí 5: Změna ceníku během sezóny a fixace cen
- **Kontext**: Ceník se v průběhu roku mění, avšak dříve sjednané smlouvy a rezervace musí zachovat původní cenu.
- **Rozhodnutí**: Ceník (`PriceList` / `PriceCategoryRate`) funguje jako katalog. V momentě vytvoření rezervace či výpůjčky systém provede **cenový snapshot** – sjednané částky (denní sazba, záloha, sleva) se uloží přímo do záznamu `ReservationItem` a `RentalItem`. Pozdější editace globálního ceníku nijak neovlivní již vystavené záznamy.
- **Důvod**: Právní jistota, neměnnost uzavřených obchodních smluv a čistá auditní stopa pro účetnictví.

---

## 4. Doménový a datový model

Systém splňuje povinné minimum: obsahuje více než 5 provázaných entit a několik vazeb M:N.

### 4.1 Klíčové entity
1. **EquipmentCategory**: Kategorie vybavení (např. Sjezdové lyže, Běžky, Snowboardy, Kanoe, Vesty). Definuje standardní sazby a parametry.
2. **EquipmentItem**: Konkrétní fyzický inventární kus (unikátní inventární číslo, kategorie, model/specifikace, velikost, rok pořízení, stav opotřebení, aktuální status: `AVAILABLE`, `RESERVED`, `RENTED`, `IN_SERVICE`, `RETIRED`).
3. **Customer**: Zákazník půjčovny (jméno, příjmení, telefon, e-mail, číslo dokladu totožnosti, poznámka o spolehlivosti).
4. **Rental**: Smlouva o výpůjčce (zákazník, datum a čas zahájení, plánované datum vrácení, celková složená kauce, celková sleva, finální status).
5. **RentalItem**: Vazební M:N entita mezi `Rental` a `EquipmentItem`. Nese sjednanou denní sazbu, skutečný čas vrácení, stav položky a případné vypočtené penále.
6. **Reservation**: Rezervace termínu dopředu (zákazník, datum od, datum do, čas expirace `validUntil`, stav: `PENDING`, `CONFIRMED`, `FULFILLED`, `CANCELLED`, `EXPIRED`).
7. **ReservationItem**: Požadavek v rezervaci (kategorie vybavení, požadovaná velikost, volitelná alokace konkrétního kusu).
8. **ServiceRecord**: Servisní záznam pro inventární kus (datum zahájení, datum ukončení, popis provedených oprav, náklady, provádějící technik).
9. **DamageRecord**: Protokol o poškození inventárního kusu při výpůjčce (vazba na položku výpůjčky, popis škody, stržená částka z kauce).
10. **PriceCategoryRate**: Matice cen pro kategorii a délku výpůjčky (např. sazba na 1 den, víkendový tarif, týdenní tarif).

### 4.2 Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    EquipmentCategory ||--o{ EquipmentItem : "obsahuje kusy"
    EquipmentCategory ||--o{ PriceCategoryRate : "má tarify"
    EquipmentCategory ||--o{ ReservationItem : "specifikuje"
    
    Customer ||--o{ Rental : "uzavírá výpůjčky"
    Customer ||--o{ Reservation : "vytváří rezervace"
    
    Reservation ||--|{ ReservationItem : "obsahuje položky"
    ReservationItem }o--o| EquipmentItem : "volitelně alokuje"
    
    Rental ||--|{ RentalItem : "obsahuje položky"
    EquipmentItem ||--o{ RentalItem : "je půjčován v"
    
    RentalItem ||--o{ DamageRecord : "může způsobit"
    EquipmentItem ||--o{ DamageRecord : "utrpěl poškození"
    EquipmentItem ||--o{ ServiceRecord : "podstupuje servis"
```

---

## 5. Architektura systému

Projekt je navržen v souladu s principy **třívrstvé architektury** se striktně jednosměrnými závislostmi:

```
[ Prezentační vrstva / Web API ]
               │
               ▼
[ Aplikační a doménová vrstva (Business Logic) ]
               │
               ▼
[ Datová a perzistentní vrstva (ORM / Migrace / DB) ]
```

1. **Prezentační vrstva (Presentation / Web API)**:
   - Zodpovídá za komunikaci s uživatelem, validaci vstupních DTO požadavků, zobrazení pultového přehledu a generování protokolů smluv.
   - Neobsahuje žádnou byznys logiku.
2. **Aplikační a doménová vrstva (Application & Domain Layer)**:
   - Čistá doménová logika a orchestration služeb.
   - Vynucuje obchodní pravidla: ověření nepřekrývání termínů, kalkulace penále, přechody stavových automatů rezervací a výpůjček, validace servisu.
3. **Datová / Perzistentní vrstva (Data Access / Infrastructure Layer)**:
   - Relační databáze běžící v Dockeru.
   - Správa schématu pomocí verzovaných migrací.
   - Repositáře a mapování entit.

---

## 6. Společné minimum předmětu PPRO

| Požadavek PPRO | Splnění v projektu |
|---|---|
| **Třívrstvá architektura** | Implementována s jednosměrnými závislostmi (API $\rightarrow$ Service/Domain $\rightarrow$ Repository/DB). |
| **Relační databáze v Dockeru** | PostgreSQL běžící v kontejneru v rámci `docker compose`. |
| **Databázové migrace** | Správa verzí databázového schématu pomocí migračních skriptů. |
| **Nejméně 5 entit** | Model obsahuje 10 plnohodnotných doménových entit. |
| **Alespoň jedna vazba M:N** | Vazba mezi `Rental` a `EquipmentItem` přes entitu `RentalItem` s dodatečnými atributy. |
| **Testy** | Unit testy doménových pravidel (kolize výpůjček, penále) a integrační testy API/databáze. |
| **Spuštění `docker compose up`** | Kompletní stack (databáze + aplikační backend) startuje jediným příkazem. |
| **Syntetická data** | Seeding skripty generují výhradně realistická syntetická data; žádné reálné osobní údaje. |

---

## 7. Návod na spuštění

### 7.1 Požadavky
- Docker a Docker Compose
- Git

### 7.2 Spuštění v kontejneru
```bash
docker compose up -d
```
Po nastartování je aplikace dostupná na standardním portu s automaticky aplikovanými migracemi a syntetickými seed daty.

---

## 8. Záznamy o postupu a změnách (Changelog & Technical Log)

- **2026-09-30**:
  - Inicializace Git repozitáře a napojení na vzdálený repozitář `https://github.com/Corsomexx/ppro2026.git`.
  - Definice projektových pravidel pro AI asistenta v [AGENTS.md](file:///u:/ppro2026/AGENTS.md).
  - Vytvoření autoritativní technické dokumentace `README.md` pro **Zadání D: Půjčovna vybavení**.
  - Zpracování všech 5 architektonických rozhodnutí k otevřeným bodům klienta.
  - Nastavení pre-commit hooku pro kontrolu aktualizace technické dokumentace.
