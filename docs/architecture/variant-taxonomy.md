# Variantentaxonomie

De RIVM-variantenfeed bevat zowel brede lineagegroepen als hun sublineages. `Variant_cases` is
daarom niet rechtstreeks optelbaar: dezelfde monsters komen in een ouder en een kind voor. De oude
grafiek probeerde kinderen recursief af te trekken, maar kende nieuwere relaties niet en bevatte een
hardcoded uitzondering voor `BA.2+S:L452X`. Daardoor konden weektotalen boven 100% uitkomen.

## Versie en herkomst

De gebruikte relaties staan in `data/variant-taxonomy-v1.json`. Versie 1 is afgeleid van
`cov-lineages/pango-designation` commit
`ac2096989d03dd34dbe44bc0929acf52d7f615d0` van 28 oktober 2026. Het bestand legt bron-URL's en
SHA-256-checksums vast. De snapshot wordt niet tijdens een normale Coronadata-update gewijzigd.

De lokale regels zijn klein en controleerbaar:

- `LP.8.1` wordt via zijn uitgebreide Pango-pad onder de dichtstbijzijnde in de RIVM-feed aanwezige
  voorouder `JN.1` geplaatst.
- `NB.1.8.1` loopt via recombinant `XDV` en wordt onder de RIVM-groep `Recombinants` geplaatst.
- `BA.2.12.1` wordt rechtstreeks onder `BA.2` geplaatst.
- `BA.2+S:L452X` is een overlappende RIVM-mutatiegroep, geen Pango-lineage, en wordt niet als
  afzonderlijke grafiekcategorie geteld.

## Exclusieve weekaantallen

Per week trekt de transformatie van iedere ouder alleen de ruwe aantallen van zijn directe kinderen
af. De overblijvende ouderwaarde en de kindwaarden zijn dan wederzijds uitsluitend. Een ontbrekende
ouder blijft expliciet als onopgelost gemarkeerd. Negatieve restwaarden en een exclusief totaal boven
de steekproefomvang maken alleen die variantenweek ongeldig; de renderer schrijft een waarschuwing
naar de site-status, slaat de week over en bouwt de rest van de site verder. De code normaliseert een
ongeldige som nooit naar 100%.

Dit verandert bewust de variantverdeling van weken waarin de oude grafiek dubbel telde. De totale
steekproefomvang, ruwe cache en andere historische metrieken veranderen niet. Vroege weken waarin
het RIVM slechts een deel van de monsters aan een gevolgde variant kon toewijzen behouden een
expliciete categorie `Onbekend`.

## Presentatie van kleine steekproeven

De ruwe exclusieve weekaantallen blijven in de validatie beschikbaar, maar zijn bij kleine
steekproeven te grillig voor een percentagesgrafiek. De variantengrafiek telt daarom per lineage de
laatste vier kalenderweken steekproefgewogen op. Een venster wordt pas getekend vanaf twintig
monsters; ontbrekende perioden worden als een echt gat weergegeven. De rest van de categorie
`Recombinants` heet in de grafiek `Overige recombinanten`, omdat benoemde recombinanten zoals XFG
ervan zijn afgetrokken. Dominantie betekent meer dan 50% in twee opeenvolgende geldige vensters.
Weergavenamen komen uit `Variant_name` in de RIVM-feed; alleen `Omicron` wordt voor de Nederlandse
site als `Omikron` geschreven. Lineagecodes zoals XFG blijven tussen haakjes staan. Er worden geen
niet-officiële bijnamen afgeleid of handmatig verzonnen.

## Controleren en bijwerken

`scripts/validateVariantTaxonomy.py` controleert alle weken in de lokale RIVM-cache en schrijft
`data/variant-taxonomy-validation.json`. De ontwikkel-, update- en publicatiescripts voeren deze
controle automatisch uit. De huidige snapshot omvat 306 weken van 30 november 2020 tot en met
19 oktober 2026, zonder onopgeloste relaties of totalen boven 100%.

Een nieuwe Pango-versie wordt bewust niet automatisch overgenomen. Bij een update worden commit,
bron-URL's en checksums in het taxonomiebestand vernieuwd, worden nieuwe of gewijzigde lokale regels
beoordeeld en draaien eerst de fixturetests en de volledige-feedvalidatie. Een regel kan met
`valid_from` en `valid_until` tot een bepaalde periode worden beperkt.
