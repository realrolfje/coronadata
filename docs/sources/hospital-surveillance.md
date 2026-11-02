# Current hospital surveillance decision

The historical LCPS and NICE series describe COVID-specific ward and intensive-care occupancy or
admissions. LCPS stopped adding national daily COVID figures in June 2024, and the old NICE public
COVID endpoints were retired.

RIVM currently reports severe acute respiratory infection (SARI) surveillance. Since September
2025 this includes weekly adult intensive-care admissions with a respiratory infection. This is a
broader syndrome, uses a new surveillance process, and is not definition-compatible with the old
COVID occupancy series. Ward data from Dutch Hospital Data was described as not yet available in
the reviewed RIVM methodology.

Decision:

- retain the final LCPS and NICE COVID observations unchanged;
- do not call their retired endpoints;
- do not append SARI observations to COVID occupancy metrics; and
- publish SARI as a separately named weekly ICU-admissions metric using the authoritative RIVM
  open-data feed and keep its source observations separate from COVID occupancy.

Reviewed official references:

- https://lcps.nu/datafeed/
- https://www.rivm.nl/luchtweginfecties/zicht-houden-op-luchtweginfecties
- https://www.rivm.nl/luchtweginfecties/sari
