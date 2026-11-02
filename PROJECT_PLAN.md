# Plan voor herstel en modernisering van Coronadata

Status: actief<br>
Aangemaakt: 2026-11-01<br>
Doel: de historische COVID-19-dataset bewaren, de nog bruikbare delen van de gegevensketen
herstellen en het project onderhoudbaar maken zonder historische uitkomsten stilzwijgend te
veranderen.

## Doelen

- De oorspronkelijke gedownloade en afgeleide gegevens bewaren.
- De historische site reproduceerbaar maken zonder afhankelijkheid van beëindigde diensten.
- Vastleggen welke bronnen actief, bevroren, beëindigd of defect zijn.
- Indicatoren bijwerken wanneer nog een gezaghebbende en inhoudelijk compatibele bron bestaat.
- Reeksen die terecht zijn geëindigd duidelijk als historisch markeren.
- Pas refactoren nadat tests het bestaande gedrag beschermen.
- Alleen betekenisvolle en gevalideerde wijzigingen publiceren.

## Geen doelen

- Geen kunstmatige continuïteit maken door datasets met verschillende definities samen te voegen.
- Geen historische waarnemingen herschrijven omdat een bron zijn schema heeft gewijzigd.
- Geen oude gegevens verwijderen na migratie naar een nieuw formaat.
- Geen brede herschrijving uitvoeren voordat een offline referentiebouw reproduceerbaar is.
- Een geslaagd HTTP-verzoek niet behandelen als bewijs dat een dataset actueel of geldig is.

## Uitgangspunten

1. Eerst bewaren, dan herstellen, daarna refactoren.
2. Gearchiveerde ruwe brondata is onveranderlijk.
3. Iedere genormaliseerde waarde moet herleidbaar zijn tot bron en transformatie.
4. Actieve, bevroren, beëindigde en defecte bronnen vereisen verschillend gedrag.
5. Historische en actuele surveillance kunnen naast elkaar bestaan zonder te doen alsof ze één
   doorlopende reeks zijn.
6. Gegenereerde bestanden zijn uitvoer, niet de bron van waarheid.
7. Iedere fase laat het project in een bruikbare toestand achter.

## Beginsituatie

- `cache/` bevat ongeveer 3,3 GB genegeerde ruwe of gecachete brondata.
- `data/` bevat ongeveer 128 MB bijgehouden data, waaronder `data/daily-stats.json` en snapshots.
- De oude keten combineerde downloaden, transformeren, berekenen, grafieken, pagina's, Git en
  publiceren.
- De drie Stichting NICE-JSON-endpoints waren verwijderd.
- Andere endpoints leverden oude maar geldige bestanden en konden daardoor ten onrechte gezond
  lijken.
- Het oude `update.sh` publiceerde ook zonder epidemiologische wijziging.

## Bronneninventaris

Deze tabel wordt ondersteund door `sources.json` en het gegenereerde `SOURCE_STATUS.md`.
Compatibiliteit moet zijn bewezen voordat een vervangende bron aan een historische reeks wordt
gekoppeld.

| Bron of metriek | Endpoint/module | Beginsituatie | Behandeling | Gecontroleerd |
|---|---|---|---|---|
| RIVM-rioolwater | `download_rioolwaterdata.py` | Actief | Behouden en valideren | [x] |
| RIVM-varianten | `download_varianten.py` | Actief | Behouden; schema en actualiteit valideren | [x] |
| Infectieradar-klachten | Oude `COVID-19_Infectieradar...` | Bevroren | Actieve ARI-bron als afzonderlijke metriek; historie ongewijzigd | [x] |
| RIVM-reproductiegetal | `download_Rt.py` | Bevroren | Bewaren met expliciete einddatum | [x] |
| RIVM-casusdata | `download_casus_landelijk.py` | Bevroren/beëindigd | Bewaren met expliciete einddatum | [x] |
| RIVM-tests | `brondata.py` en CoronaWatchNL | Bevroren | Bewaren; niet als actuele testdekking tonen | [x] |
| RIVM-prevalentieschatting | `brondata.py` | Bevroren | Als historische schatting bewaren | [x] |
| RIVM-vaccinatiegraad | `brondata.py` | Bevroren | Bewaren met expliciete einddatum | [x] |
| LCPS-ziekenhuis en IC | `download_lcps_ziekenhuisopnames.py` | Geëindigd in 2024 | Eindstand bewaren; alleen definitiecompatibele opvolgers overwegen | [x] |
| Stichting NICE | `download_Zkh.py` | Endpoints verwijderd | Live verzoeken stoppen; cachehistorie bewaren | [x] |
| Coronadashboard-JSON | `brondata.py` | Onbekend | Endpoint, schema, actualiteit en gebruik controleren | [x] |
| Apple Mobility | `brondata.py` | Bevroren in 2022 | Als afgeronde historische reeks behandelen | [x] |
| ECDC-kaart | uitgeschakeld | Beëindigd | Uit actieve keten; historisch artefact bewaren | [x] |
| CoronaWatchNL-tests | `brondata.py` | Onbekend/bevroren | Alleen historisch behouden waar nodig | [x] |
| Paginateller | `updatePageHits.py` | Niet-epidemiologisch | Buiten de epidemiologische keten houden | [x] |

Nuttige officiële verwijzingen:

- [RIVM COVID-19-datasets](https://data.rivm.nl/covid-19/)
- [LCPS-datafeed](https://lcps.nu/datafeed/)
- [Stichting NICE](https://www.stichting-nice.nl/)

## Fase 1: bewaren en een referentie vastleggen

### 1.1 Huidige data archiveren

Dit blijft bewust eenvoudig: een handmatige veiligheidskopie, geen nieuw opslagsysteem.

- [x] Updateproces tijdens archivering stilzetten.
- [x] Gedateerd ZIP-archief met `cache/` en `data/` maken.
- [x] ZIP buiten de Git-repository bewaren.
- [x] Archief met `unzip -t` controleren.
- [x] SHA-256-bestand naast de ZIP maken.
- [x] Bestandsnaam, checksum, datum en herstelcommando vastleggen.

Herstelprocedure:

```shell
cd /pad/naar/coronadata
unzip /pad/buiten/repository/coronadata-data-YYYY-MM-DD.zip
```

| Veld | Waarde |
|---|---|
| Archief | `/Users/rolf/github/coronadata-data-2026-11-01.zip` (101 MB) |
| Aangemaakt | 2026-11-01 |
| SHA-256 | `6dbe5218e6aeb84e7228b8507b1461f050a19a51e8b534c402bab5d52feb91a4` |
| Inhoud | `cache/`, `data/` |

### 1.2 Offline referentiebouw

`data/daily-stats.json` geldt als volledige historische basis. De laptopcache bevat mogelijk niet
alle oorspronkelijke bronbestanden van de oude productieserver. Een volledige historische
herimport is daarom geen eis en mag de basis niet overschrijven.

- [x] Rendercommando zonder downloads, bronverwerking, berekeningen of writes naar
  `daily-stats.json` toevoegen.
- [x] Grafieken en pagina's uit bewaarde invoer genereren.
- [x] Ontbrekende renderinvoer identificeren en bewaren of als fixture vastleggen.
- [x] Representatieve grafiekwaarden en datumbereiken als regressiebasis vastleggen.
- [x] Deterministische uitvoer of invoer van de renderer vergelijken.
- [x] Regressietests voor belangrijke totalen, datums en einddatums toevoegen.
- [x] Met SHA-256 bewijzen dat de offline bouw `daily-stats.json` niet wijzigt.
- [x] Documenteren dat volledige herimport zonder oorspronkelijke servercache niet reproduceerbaar
  is.

### 1.3 Veilig publiceren

- [x] Voorkomen dat alleen een nieuwe timestamp een commit veroorzaakt.
- [x] Publicatie blokkeren wanneer een verplichte actieve bron faalt.
- [x] `git pull -X theirs` vervangen door expliciete `git pull --ff-only`.
- [x] Ophalen/bouwen scheiden van committen/pushen.
- [x] Voor publicatie een bouw- en brongezondheidsrapport maken.

### Voltooiingscriteria fase 1

- [x] Er is een gecontroleerd en herstelbaar extern archief.
- [x] De historische site rendert offline zonder bronherimport.
- [x] Historische regressietests slagen.
- [x] Een mislukte of ongewijzigde run veroorzaakt geen misleidende publicatiecommit.

## Fase 2: bronnenregister en gezondheidsrapport

Iedere bron krijgt een kleine eigen downloader en parser. Parsers leveren via een algemene
opslaginterface een gedocumenteerd tussenresultaat; berekeningen en grafieken blijven daarbuiten.
SQLite is na een pilot gekozen als herbouwbare tussenopslag, terwijl de bewaarde JSON de
historische basis blijft.

- [x] Machineleesbaar register `sources.json` toevoegen.
- [x] Iedere bron een stabiele identifier geven, onafhankelijk van URL.
- [x] Leverancier, URL, formaat, verwacht interval en levenscyclus opslaan.
- [x] Velden, eenheden, geografie en datumsemantiek vastleggen.
- [x] Afnemende metrieken en grafieken registreren.
- [x] Cachebewijs, publicatiedatum en nieuwste waarneming registreren.
- [x] Aanwezigheid, inhoud, schema, publicatiedatum en nieuwste waarneming valideren.
- [x] `active`, `frozen`, `retired`, `broken` en `unknown` onderscheiden.
- [x] Leesbaar brongezondheidsrapport genereren.
- [x] Alle regels uit de bronneninventaris controleren.
- [x] Gemeenschappelijk parserresultaat met bron-ID, waarnemingen, datums, herkomst en waarschuwingen
  definiëren.
- [x] Iedere actieve epidemiologische bron een parser en gevalideerde downloader geven.
- [x] Parsing scheiden van berekeningen, correlaties, grafieken en publicatie.
- [x] Opslaginterface voor schrijven en later uitlezen definiëren.
- [x] SQLite-pilot uitvoeren met idempotente import en een bestaande grafiekquery.
- [x] Opslagkeuze op basis van de pilot documenteren.
- [x] SQLite herbouwbaar houden; historische JSON niet vervangen.

### Voltooiingscriteria fase 2

- [x] Iedere externe invoer heeft eigenaar, levenscyclus en verwachte actualiteit.
- [x] Een downloadbaar maar oud bestand wordt als verouderd gemeld.
- [x] Register koppelt bronnen aan metrieken en grafieken en verklaart fouten.
- [x] Parsing en bronoverstijgende berekeningen zijn gescheiden.
- [x] Opslagkeuze is door een pilot onderbouwd.

## Fase 3: actieve bronnen herstellen

- [x] Per bron een Markdown-document maken.
- [x] Eigenaar, doel, URL-geschiedenis, schema, eenheden, interval, datumbereik,
  levenscyclus, parser, afnemers, hiaten en vervangingsbesluit documenteren.
- [x] Brondocumentatie vanuit register en index linken.

### 3.1 Standaard innamestroom

- [x] Naar tijdelijk bestand downloaden.
- [x] HTTP-status, contenttype, omvang en schema valideren.
- [x] Publicatiedatum en nieuwste waarneming valideren.
- [x] Gewijzigde inhoud als gedateerde onveranderlijke snapshot bewaren.
- [x] Via bronspecifieke adapter transformeren.
- [x] Velden, eenheden, bereiken, dubbelen, volgorde en continuïteit valideren.
- [x] Fatale fouten van waarschuwingen onderscheiden.
- [x] Ontbrekende bronwaarnemingen als hiaten bewaren; niet stilzwijgend interpoleren.
- [x] Bronspecifiek beleid voor dagelijkse, wekelijkse en onregelmatige bronnen toestaan.
- [x] Via SQLite samenvoegen zonder ongerelateerde historische waarden te wijzigen.
- [x] Datums, SHA-256, bronpad en recordaantal als herkomst vastleggen.
- [x] Imports idempotent maken.
- [x] Tests met kleine rioolwater-, varianten- en ARI-fixtures toevoegen.
- [x] Gezondheid en transformatieresultaten rapporteren.

### 3.2 Uitgevoerde volgorde

- [x] Rioolwaterinname herstellen en valideren.
- [x] Varianteninname herstellen en valideren.
- [x] Actieve ARI/Infectieradar als afzonderlijke metriek toevoegen.
- [x] Actuele ziekenhuis- en luchtwegbronnen onderzoeken.
- [x] Alleen definitiecompatibele ziekenhuisbronnen toestaan; SARI niet aan historische
  COVID-bezetting koppelen.
- [x] Herhaalde NICE-verzoeken uitschakelen.
- [x] ECDC, Apple Mobility en oud dashboard uit actieve uitvoering verwijderen.

### Voltooiingscriteria fase 3

- [x] Actieve rioolwater-, varianten- en ARI-indicatoren komen uit gezaghebbende RIVM-bronnen.
- [x] Bevroren/beëindigde indicatoren blijven ongewijzigd en hebben een einddatum.
- [x] Bron- of schemafouten stoppen publicatie met bruikbare foutmelding.

## Fase 4: versiegebonden datamodel

Het brede dagrecord combineert uiteenlopende bronnen, eenheden, bereiken en levenscycli. Het nieuwe
genormaliseerde observatiemodel draait ernaast en vervangt de historische basis niet.

```yaml
date: 2026-10-28
metric: wastewater_sars_cov_2
value: 123.4
unit: particles_per_100000_inhabitants
geography: NL
source_id: rivm_wastewater_national
source_publication_date: 2026-10-28
status: reported
provenance:
  raw_snapshot: path-or-checksum
  transformer_version: 1
```

- [x] Namen, eenheden, geografie, null-beleid en datumsemantiek definiëren.
- [x] Gerapporteerde, herziene, geïmputeerde en berekende waarden onderscheiden.
- [x] Bron- en transformatieherkomst toevoegen.
- [x] Schema van een versie voorzien.
- [x] Adapter voor bestaand `daily-stats.json` schrijven.
- [x] Historische data converteren zonder origineel te vervangen.
- [x] Oude en nieuwe grafiekinvoer per metriek vergelijken: alle 43 metrieken hebben gelijke
  aantallen en SHA-256-digests.
- [x] Afnemers pas omschakelen na bewezen gelijkheid; compatibiliteitsbestand blijft voorlopig
  leidend.
- [x] Bewuste verschillen documenteren.

### Voltooiingscriteria fase 4

- [x] Nieuwe en historische observaties delen schema v1 en opslaginterface.
- [x] Originele bestanden blijven bewaard; conversie schrijft `daily-stats.json` niet.
- [x] Iedere numerieke grafiekwaarde is herleidbaar tot bron of berekening, oud veld en transformer.

## Fase 5: veilig refactoren

- [x] Downloaden, valideren, transformeren, opslaan, grafieken en publiceren scheiden.
- [x] Grote `brondata.py`-workflow vervangen door expliciete stappen; module is compatibiliteitslaag.
- [x] Dubbele downloads en transformaties verwijderen.
- [x] Werkmapafhankelijke paden vervangen door projectrootpaden.
- [x] Getypeerde in- en uitvoer voor adapters en stappen definiëren.
- [x] Tests voor datumparsing, samenvoegen en brontransformaties toevoegen.
- [x] Fixturetests met kleine bewaarde bronformaten toevoegen.
- [x] Grafieken waar praktisch deterministisch maken.
- [x] Dependencies vastzetten en Python 3.11 documenteren.
- [x] Eén ontwikkelcommando toevoegen: `./dev.sh`.
- [x] Dode code pas na dekking verwijderen; historische transformaties behouden.

### Voltooiingscriteria fase 5

- [x] Ketenstappen zijn afzonderlijk uitvoerbaar en testbaar.
- [x] Bronspecifieke wijzigingen vereisen geen wijziging in ongerelateerde grafiekcode.
- [x] Historische regressietests slagen.

## Fase 6: site en automatisering

- [x] Historische volledige grafieken behouden en actuele surveillance daarvan inhoudelijk
  onderscheiden, zonder de vertrouwde dashboardvormgeving te vervangen.
- [x] Bestaande SVG's als betrouwbaar archief, JavaScriptloze fallback en regressiereferentie
  behouden.
- [x] Eén interactieve, zoombare rioolwatergrafiek op basis van statische JSON maken, met pannen,
  tooltips, reeksselectie en afzonderlijke y-assen.
- [x] Verdere migratie pas na een gebruiksbesluit uitvoeren; ongerelateerde eenheden en reeksen niet
  in één grafiek stoppen.
- [x] Bronnen en einddatums via grafiekbijschriften, bronstatus en historische weergave duidelijk
  maken.
- [x] Berekende/experimentele waarden van gerapporteerde waarden onderscheiden.
- [x] HTML- en JSON-bronstatus genereren.
- [x] Alleen gevalideerde, betekenisvolle wijzigingen publiceren; renders gebruiken de nieuwste
  waarneming als reproduceerbare referentiedatum.
- [x] Tests, parity en bronvalidatie vóór publicatie uitvoeren.
- [x] Paginateller in `update-pagehits.sh` buiten epidemiologische bouw houden.
- [x] Herstel en rollback in `docs/operations.md` documenteren.

### Voltooiingscriteria fase 6

- [x] Actuele en historische status is voor lezers controleerbaar zonder historische tijdlijnen te
  verliezen.
- [x] Interactieve grafiek is progressieve uitbreiding en behoudt een SVG-fallback.
- [x] Publicatie vermeldt brondatums en ketengezondheid.
- [x] Automatisering kan verouderde of ongeldige data niet stilzwijgend als actueel publiceren.

## Mijlpalen

### Mijlpaal A: beschermde historie

- [x] Extern cache/data-archief en vastgelegde checksum/manifest bestaan.
- [x] Offline referentiebouw werkt.
- [x] Onveilig automatisch publiceren is uitgeschakeld.

### Mijlpaal B: zichtbare keten

- [x] Bronnenregister bestaat.
- [x] Gezondheidsrapport onderscheidt actieve, verouderde, beëindigde en defecte invoer.
- [x] Historische regressietests draaien vóór update en publicatie.

### Mijlpaal C: bruikbare actuele data

- [x] Rioolwater werkt betrouwbaar bij.
- [x] Varianten werken betrouwbaar bij.
- [x] Actuele Infectieradar/ARI is opgenomen zonder oude reeks te herschrijven.

### Mijlpaal D: onderhoudbare architectuur

- [x] Versiegebonden observatiemodel bestaat.
- [x] Bronadapters hebben fixtures en tests.
- [x] Ketenstappen zijn gescheiden.

### Mijlpaal E: betrouwbare publicatie

- [x] Site maakt levenscyclus en waarnemingsdatums controleerbaar.
- [x] Tests, parity, brongezondheid en betekenisvolle uitvoer bewaken publicatie.
- [x] Herstel en rollback zijn gedocumenteerd.

## Afgerond na de refactoring: variantentaxonomie

De RIVM-variantenfeed bevat overlappende ouder- en kindcategorieën. Nieuwere lineages zoals
`LP.8.1` kunnen een lege `Is_subvariant_of` hebben terwijl dezelfde monsters ook in een bredere
lineage meetellen. De oude correctie kan daardoor boven 100% uitkomen.

- [x] Kleine ruwe fixtures bewaren voor correcte en problematische weken, waaronder 2025-02-17 en
  2025-03-10.
- [x] Gezaghebbende, versiegebonden bron voor lineagerelaties kiezen en herkomst en geldigheidsdatum
  vastleggen; geen permanente relatie alleen uit een naam afleiden.
- [x] Taxonomiemodel definiëren met lineagecode, uitgebreide lineage, ouder, bewijsbron en
  geldigheidsperiode.
- [x] Overlappende ouder-/kindaantallen één keer naar wederzijds uitsluitende restcategorieën
  omzetten; onbekend/onopgelost expliciet bewaren.
- [x] Valideren dat restaantallen niet negatief zijn, steekproefomvang niet overschrijden en per week
  maximaal 100% vormen.
- [x] Ongeldige totalen niet naar 100% normaliseren; onopgeloste overlap bewaren en verklaren.
- [x] Hardcoded `BA.2+S:L452X`-uitzondering vervangen door taxonomietransformatie.
- [x] Fixturetests voor gewijzigde hiërarchie, ontbrekende ouders, aliassen, recombinanten en correcte
  historische weken toevoegen.
- [x] Alle 306 bewaarde weken controleren; verschillen op probleemweken zijn de bedoelde verwijdering
  van dubbeltellingen en staan in `docs/architecture/variant-taxonomy.md`.

### Voltooiingscriteria variantentaxonomie

- [x] Iedere wekelijkse grafiekcategorie is wederzijds uitsluitend of expliciet onopgelost.
- [x] Totalen boven 100% leveren een zichtbare sitewaarschuwing op en slaan alleen de ongeldige
  variantenweek over; andere grafieken blijven bouwen.
- [x] Iedere externe lineagerelatie is herleidbaar tot taxonomieversie en bron.

## Nog te nemen besluiten

| Besluit | Opties | Huidige voorkeur | Status |
|---|---|---|---|
| Formaat bronnenregister | YAML / JSON / Python | JSON: geen nieuwe runtime-dependency | Besloten: JSON |
| Genormaliseerde opslag | JSON Lines / CSV / Parquet / SQLite | SQLite achter interface; JSON blijft basis | Besloten: SQLite |
| Historische grafiekcompatibiliteit | Pixelgelijk / datagelijk / gedocumenteerde verschillen | Datagelijk | Open |
| Actuele ziekenhuismetriek | Compatibele opvolger / afzonderlijke nieuwe metriek / alleen historisch | LCPS-bezetting t/m 31 mei 2024 als historische aanvulling; daarna geen compatibele openbare landelijke bron | Besloten: historie aanvullen, actueel niet fabriceren |
| Bron variantentaxonomie | RIVM / versiegebonden Pango / lokale mapping | Vastgezette Pango-versie met kleine beoordeelde RIVM-overrides | Besloten: Pango + lokale regels |
| Automatiseringsplatform | Bestaande host / GitHub Actions / handmatig | Beslissen nu offline bouw betrouwbaar is | Open |

## Risico's

| Risico | Maatregel |
|---|---|
| Refactoring verandert historische cijfers | Eerst fixtures en regressietests |
| Werkend endpoint levert bevroren data | Nieuwste waarneming en interval valideren |
| Vervangende bron gebruikt andere definitie | Nieuwe metriek maken, niet aan oude reeks plakken |
| Genegeerde cache raakt verloren | Gecontroleerde ZIP en SHA-256 buiten repository bewaren |
| Leverancier herziet oude records | Gedateerde snapshots en revisies expliciet bewaren |
| Gegenereerde uitvoer veroorzaakt enorme diffs | Artefacten scheiden van bron en betekenisvolle wijzigingen |
| Automatisering publiceert gedeeltelijke resultaten | Alle verplichte actieve bronnen vooraf valideren |

## Eerstvolgende acties

1. [x] Extern ZIP-archief uit fase 1.1 maken en controleren.
2. [x] Alleen-lezen inventaris voor externe invoer bouwen.
3. [x] Gezondheidsrapporten voor datum en schema maken zonder brondata te wijzigen.
4. [x] Offline bouw toevoegen en aanvankelijke fouten vastleggen.
5. [x] Kleine historische regressiesuite toevoegen.
6. [x] Timestamp-only en mislukte runs niet meer laten publiceren.
7. [x] Bronnenregister uit inventaris maken.
8. [x] Rioolwaterpilot voor parser/opslag uitvoeren.
9. [x] Officiële LCPS-datafeed gecontroleerd gebruiken om ziekenhuis- en IC-bezetting tot en met
   31 mei 2024 aan te vullen; bronovergang zichtbaar documenteren zonder de historische basis te wijzigen.
10. [x] Afgesloten COVID-19-bezetting naar het archief verplaatsen en op de hoofdpagina vervangen
    door wekelijkse Nederlandse RIVM/NICE-SARI-IC-opnames als afzonderlijke actuele metriek.
11. [x] Het beëindigde officiële reproductiegetal naar het archief verplaatsen en actuele wekelijkse
    rioolwater-, Infectieradar- en laboratoriumtrends afzonderlijk valideren en opslaan, zonder ze als
    een nieuw reproductiegetal te presenteren.

## Voortgangslogboek

| Datum | Wijziging | Resultaat / vervolg |
|---|---|---|
| 2026-11-01 | Eerste herstelplan | Start met alleen-lezen inventaris |
| 2026-11-01 | `cache/` en `data/` extern gearchiveerd | ZIP en SHA-256 gecontroleerd |
| 2026-11-01 | Eerste offline renderpad | Historische JSON bleef ongewijzigd |
| 2026-11-01 | Offline render gecontroleerd | Exitcode 0, geen netwerk, checksum gelijk |
| 2026-11-01 | Historische regressietests | Zeven eerste tests dekten basis en bouwgezondheid |
| 2026-11-01 | Update en publicatie gescheiden | Publicatie expliciet en beperkt tot gegenereerde data |
| 2026-11-01 | Bronnenregister en gezondheidsrapport | Verouderde verplichte bronnen blokkeren publicatie |
| 2026-11-01 | SQLite-rioolwaterpilot | 158.423 observaties gelijk; herimport idempotent |
| 2026-11-01 | Gevalideerde actieve inname | Rioolwater, varianten en ARI met onveranderlijke snapshots |
| 2026-11-01 | Dode verzoeken beëindigd | NICE, ECDC, Apple en oud dashboard niet meer actief; SARI apart |
| 2026-11-01 | Genormaliseerd schema v1 | 69.205 observaties en 43 metrieken exact gelijk |
| 2026-11-02 | Historische korte grafieken hersteld | 365-dagenvensters eindigen bij laatste eigen waarneming |
| 2026-11-02 | Versiegebonden variantentaxonomie | 306 weken exclusief gevalideerd; ongeldige weken worden zichtbaar overgeslagen |
| 2026-11-02 | Ziekenhuisgrafieken gescheiden | COVID-bezetting t/m 31 mei 2024 in archief; actuele Nederlandse SARI-IC-opnames op hoofdpagina |
| 2026-11-02 | Reproductiegetal gearchiveerd | Drie actuele RIVM-trendfeeds afzonderlijk opgeslagen als basis voor een latere trendindicator |
