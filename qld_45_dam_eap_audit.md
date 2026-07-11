# Comprehensive Queensland 45-Dam EAP Flood-Trigger Audit

**Audit date:** 11 July 2026

## Coverage

- Dashboard dams audited: **45**
- Dams with an EAP listed in the current Queensland directory: **44**
- Not listed: **Nindooinbah Dam**
- Records with flood rules captured: **44**
- Formal EAP activations confirmed: **0** — this audit is indicative only.

## Critical implementation finding

The current repository's `data/latest.json` contains `storage_level_m: null` for all 45 dams. Most EAP flood triggers are expressed as reservoir elevation, so adding the rules will remove the “rules unavailable” problem but will not, by itself, permit a live threshold comparison. Codex must show **Rules verified; live storage elevation unavailable** rather than claiming that EAP data is missing.

Do not substitute percentage full, volume, spill status, or a nearby BOM river-gauge height for an EAP reservoir elevation. An elevation comparison is valid only when the live field uses the same datum and units as the EAP.

## Exceptions requiring special treatment

- **Callide Dam:** rules were extracted from the government-hosted issue 9.0 copy, but Sunwater's current operator link points to a `Callide_Dam_EAP_2026.pdf` filename. Treat as `change_review_required` until compared.
- **Glenlyon Dam:** the EAP contains an internal Alert conflict: **411.73 m** in the table versus **411.63 m** in nearby narrative. Do not automate Alert.
- **Ewen Maddock Dam:** the audited cover expired **30 June 2026**. Preserve the rules but flag the document expired and seek the replacement.
- **EJ Beardmore Dam:** expiry **1 August 2026**; near expiry.
- **Tinaroo Falls Dam:** expiry **1 September 2026**; near expiry.
- **Lake Macdonald Dam:** current rules are construction/cofferdam-specific.
- **Somerset Dam:** use the current authoritative dynamic OFSL; percentage full is invalid.
- **Nindooinbah Dam:** no applicable EAP was found in the current official directory; do not borrow another dam's rules.

## 45-dam coverage table

| Dam | Operator | Version | Expiry | Audit status | Flood-trigger summary |
|---|---|---:|---:|---|---|
| Atkinson Dam | Seqwater | 10.2 | 2028-07-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 65.72 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 66.62 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 67.50 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 67.50 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 67.50 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Baroon Pocket Dam | Seqwater | 10.2 | 2028-07-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 217.00 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 219.62 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 221.50 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 221.50 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 221.50 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Bill Gunn Dam | Seqwater | 11 | 2030-07-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 110.00 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 110.65 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 111.00 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 111.00 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 111.00 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Bjelke-Petersen Dam | Sunwater | 10.2 | 2027-10-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 307.20 m and is rising. Lean Forward: Storage elevation exceeds EL 307.30 m. Stand Up 1: Storage elevation exceeds EL 310.20 m (moderate flood classification level). Stand Up 2: Storage elevation exceeds EL 311.82 m (greater than January 2011 Flood of Record). Stand Up 3: Storage elevation exceeds EL 317.45 m (upper emergency level allowing for wave action). (+1 alternate pathway) |
| Boondooma Dam | Sunwater | 9.2 | 2028-04-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 280.30 m and is rising. Lean Forward: Storage elevation exceeds EL 280.40 m. Stand Up 1: Storage elevation exceeds EL 282.50 m (moderate flood classification level). Stand Up 2: Storage elevation exceeds EL 286.56 m (greater than January 2013 Flood of Record). Stand Up 3: Storage elevation exceeds EL 296.70 m (upper emergency level allowing for wave action). (+1 alternate pathway) |
| Borumba Dam | Seqwater | 10.2 | 2027-06-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 135.01 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 141.02 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 143.50 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 143.50 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 143.50 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Burdekin Falls Dam | Sunwater | 9.4 | 2027-05-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 153.90 m and is rising. Lean Forward: Storage elevation exceeds EL 154.00 m. Stand Up 1: Storage elevation exceeds EL 157.00 m (minor flood classification level). Stand Up 2: Storage elevation exceeds EL 160.85 m (greater than February 1991 Flood of Record). Stand Up 3: Storage elevation exceeds EL 162.00 m (major flood classification level). Stand Up 4: Storage elevation exceeds EL 171.00 m (upper emergency level allowing for wave action). (+1 alternate pathway) |
| Callide Dam | Sunwater | 9.0 | — | rules_extracted_version_comparison_required | Alert: Forecast outflow exceeds 200 m³/s, storage is above EL 212.50 m, and rainfall/streamflow is observed. (+1 alternate pathway) Lean Forward: Storage exceeds EL 215.50 m. (+1 alternate pathway) Stand Up 1: Storage exceeds EL 216.37 m. (+1 alternate pathway) Stand Up 2: Storage exceeds EL 216.49 m. (+1 alternate pathway) Stand Up 3: Storage exceeds EL 216.66 m. (+1 alternate pathway) Stand Up 4: Storage exceeds EL 217.20 m, the published Flood of Record stage. (+1 alternate pathway) Stand Up 5: Storage exceeds EL 219.13 m allowing for wave action. (+1 alternate pathway) |
| Cania Dam | Sunwater | 10.0 | 2029-04-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 331.00 m. Lean Forward: Storage elevation exceeds EL 332.40 m. Stand Up 1: Storage elevation exceeds EL 334.45 m (greater than January 2013 Flood of Record). Stand Up 2: Storage elevation exceeds EL 338.00 m (overtopping/upper emergency level allowing for wave action). (+1 alternate pathway) |
| Cedar Pocket Dam | Seqwater | 11.1 | 2029-07-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 101.07 m AHD and a relevant BOM flood warning is expected. (+1 alternate pathway) Lean Forward: Current lake level reaches the Flood of Record level of 103.28 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 104.50 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 104.50 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 104.50 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Clarendon Dam | Seqwater | 10.2 | 2027-06-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 96.00 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 96.12 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 96.30 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 96.30 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 96.30 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Coolmunda Dam | Sunwater | 9.1 | 2029-07-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 314.18 m. (+1 alternate pathway) Lean Forward: Storage elevation exceeds EL 314.34 m. Stand Up 1: Storage elevation exceeds EL 314.47 m (major flooding level). Stand Up 2: Storage elevation exceeds EL 314.92 m (greater than February 1976 Flood of Record). Stand Up 3: Storage elevation exceeds EL 315.32 m (fuse-plug overtopping allowing for wave action). (+1 alternate pathway) Stand Up 4: Storage elevation exceeds EL 316.58 m (main embankment overtopping allowing for wave action). (+1 alternate pathway) |
| Cooloolabin Dam | Seqwater | 11.2 | 2028-05-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 293.00 m AHD and a relevant BOM flood warning is expected. (+1 alternate pathway) Lean Forward: Current lake level reaches the Flood of Record level of 296.48 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 296.60 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 296.60 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 296.60 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| EJ Beardmore Dam | Sunwater | 9.2 | 2026-08-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 207.02 m and is rising. Lean Forward: Storage elevation exceeds EL 207.12 m. Stand Up 1: Storage elevation exceeds EL 207.87 m (higher flood stage). Stand Up 2: Storage elevation exceeds EL 208.32 m (greater than February 2012 Flood of Record). Stand Up 3: Storage elevation exceeds EL 208.65 m (right embankment overtopping allowing for wave action). (+1 alternate pathway) |
| Enoggera Dam | Seqwater | 10.3 | 2027-07-01 | partial_public_assessment_supported | Alert: Lake level at or above 74.40 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current or predicted lake level reaches 78.60 m AHD. Stand Up 1: Level at or above 80.00 m AHD, Near-PAR flooding likely, and imminent failure judged unlikely. Stand Up 2: Lake level likely to reach 80.47 m AHD and imminent failure judged unlikely. Stand Up 3: Lake level likely to reach 82.50 m AHD and failure is occurring or judged likely. (+1 alternate pathway) |
| Eungella Dam | Sunwater | 9.0 | 2029-03-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 562.71 m. Lean Forward: Storage elevation exceeds EL 566.04 m. Stand Up 1: Storage elevation exceeds EL 569.21 m (upper emergency level allowing for wave action). (+1 alternate pathway) |
| Ewen Maddock Dam | Seqwater | 11.5 | 2026-06-30 | rules_extracted_but_document_expired | Alert: Lake level is at or above FSL 25.38 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 26.92 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 27.50 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 27.50 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 27.50 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Fairbairn Dam | Sunwater | 11.2 | 2028-03-14 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 204.13 m and is rising. Lean Forward: Storage elevation exceeds EL 204.23 m. Stand Up 1: Storage elevation exceeds EL 207.73 m (moderate flood classification level). Stand Up 2: Storage elevation exceeds EL 209.80 m (greater than Flood of Record). Stand Up 3: Storage elevation exceeds EL 217.39 m (upper emergency level allowing for wave action). (+1 alternate pathway) |
| Fred Haigh Dam | Sunwater | 9.1 | 2029-05-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 75.46 m and is rising. Lean Forward: Storage elevation exceeds EL 75.56 m. Stand Up 1: Storage elevation exceeds EL 77.06 m (moderate flood classification level). Stand Up 2: Storage elevation exceeds EL 82.42 m (greater than January 2013 Flood of Record). Stand Up 3: Storage elevation exceeds EL 85.94 m (top of crest parapet allowing for wave action). (+1 alternate pathway) |
| Glenlyon Dam | Sunwater | 8.1 | 2027-04-01 | document_conflict_manual_review_required | Alert: The trigger table gives Alert above FSL 411.73 m. (+1 alternate pathway) Lean Forward: Storage exceeds EL 413.19 m, the published minor-flood stage. Stand Up 1: Storage exceeds EL 414.02 m, the December 2021 Flood of Record stage. Stand Up 2: Storage exceeds EL 418.00 m. Stand Up 3: Storage exceeds EL 423.60 m allowing for wave action. (+1 alternate pathway) |
| Gold Creek Dam | Seqwater | 10.2 | 2028-04-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 92.75 m AHD and a relevant BOM flood warning is expected. (+1 alternate pathway) Lean Forward: Current lake level reaches the Flood of Record level of 96.91 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 99.00 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 99.00 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 99.00 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Hinze Dam | Seqwater | 11.2 | 2027-12-18 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 94.50 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 100.28 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 104.00 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 104.00 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 104.00 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Julius Dam | Sunwater | 8.3 | 2027-05-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 223.44 m and is rising. Lean Forward: Storage elevation exceeds EL 223.54 m. Stand Up 1: Storage elevation exceeds EL 228.17 m (greater than January 2004 Flood of Record). |
| Kinchant Dam | Sunwater | 7.2 | 2027-01-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 57.21 m and is rising. Lean Forward: Storage elevation exceeds EL 58.00 m. Stand Up 1: Storage elevation exceeds EL 58.21 m (spillway crest). Stand Up 2: Storage elevation exceeds EL 58.56 m (greater than January 1991 Flood of Record). Stand Up 3: Storage elevation exceeds EL 61.21 m (upper emergency level allowing for wave action). (+1 alternate pathway) |
| Kroombit Dam | Sunwater | 11.1 | 2027-12-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 265.70 m and is rising. Lean Forward: Storage elevation exceeds EL 265.80 m. Stand Up 1: Storage elevation exceeds EL 267.08 m (approximately 750 m³/s). Stand Up 2: Storage elevation exceeds EL 267.78 m (approximately 1,500 m³/s). Stand Up 3: Storage elevation exceeds EL 268.36 m (greater than 2,250 m³/s and February 2015 Flood of Record). |
| Lake MacDonald Dam | Seqwater | 12.0 | 2029-05-01 | partial_public_assessment_supported | Alert: At least one siphon is activated to maintain the operating level at or below 93.00 m AHD. (+1 alternate pathway) Lean Forward: Current or predicted level reaches 94.00 m AHD with outflows affecting Lake Macdonald Drive. Stand Up 1: Current or predicted level reaches 95.00 m AHD with no imminent-failure indicators. Stand Up 2: Lake level likely to reach 96.00 m AHD and failure is possible but unlikely within 12 hours. Stand Up 3: Lake level likely to reach 96.00 m AHD and failure is occurring or likely within 12 hours. |
| Lake Manchester Dam | Seqwater | 11.2 | 2028-07-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 50.90 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 53.34 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 57.00 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 57.00 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 57.00 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Leslie Dam | Sunwater | 8.1 | 2027-10-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 472.41 m and is rising. Lean Forward 1: Storage elevation exceeds EL 472.51 m. Lean Forward 2: Storage exceeds EL 472.59 m, where impacts to the Cunningham Highway are likely. Stand Up 1: Storage elevation exceeds EL 472.70 m (Flood of Record). Stand Up 2: Storage elevation exceeds EL 473.63 m (dam crest). |
| Leslie Harrison Dam | Seqwater | 10.2 | 2027-07-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 15.24 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 18.62 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 21.00 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 21.00 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 21.00 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Little Nerang Dam | Seqwater | 11.2 | 2027-12-18 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 168.02 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 171.74 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 172.00 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 172.00 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 172.00 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Maroon Dam | Seqwater | 10.2 | 2028-06-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 207.14 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 210.04 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 216.50 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 216.50 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 216.50 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Moogerah Dam | Seqwater | 10.2 | 2027-08-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 154.81 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 158.64 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 159.50 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 159.50 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 159.50 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Nindooinbah Dam | Seqwater | — | — | not_applicable_no_official_eap_listed | No applicable EAP listed. |
| North Pine Dam | Seqwater | 13.0 | 2029-10-01 | partial_public_assessment_supported | Alert: Possible Flood Event commencement and relevant BOM warning conditions. Lean Forward: Flood Event likely due to significant catchment rainfall. Stand Up 1: Flood Event has commenced under the Flood Manual. (+1 alternate pathway) Stand Up 2: Extreme Flood Level 40.30 m AHD plus failure possible but unlikely within 12 hours. Stand Up 3: Maximum flood storage 41.40 m AHD plus failure occurring or likely within 12 hours. |
| Paradise Dam | Sunwater | 12.2 | 2029-06-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 61.70 m and is rising. Lean Forward: Storage elevation exceeds EL 61.80 m. Stand Up 1: Storage elevation exceeds EL 64.30 m (moderate flood level). Stand Up 2: Storage elevation exceeds EL 71.40 m (equivalent flow from 2013 event). |
| Peter Faust Dam | Sunwater | 9.0 | 2029-03-08 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 85.60 m and is rising. Lean Forward: Storage elevation exceeds EL 87.08 m. Stand Up 1: Storage elevation exceeds EL 88.80 m (Petters Creek bridge inundation possible). Stand Up 2: Storage elevation exceeds EL 94.23 m (upper emergency level allowing for wave action). (+1 alternate pathway) |
| Poona Dam | Seqwater | 11.1 | 2028-05-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 152.70 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 152.98 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 153.50 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 153.50 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 153.50 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Sideling Creek Dam | Seqwater | 10.1 | 2027-07-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 20.37 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 22.14 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 23.00 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 23.00 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 23.00 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Somerset Dam | Seqwater | 11.0 | 2028-04-01 | partial_public_assessment_supported | Alert: Lake level is within 1 m of the current dynamic OFSL, Flood Event commencement is possible, and BOM warning criteria apply. Lean Forward: Lake level is within 1 m of dynamic OFSL and a Flood Event is likely. Stand Up 1: Level at or above current dynamic OFSL and Flood Event commenced under the Flood Manual. (+1 alternate pathway) Stand Up 2: Level reaches 106.26 m AHD and failure is possible but unlikely within 12 hours. Stand Up 3: Level reaches 107.45 m AHD where applicable and failure is occurring or likely within 12 hours. (+1 alternate pathway) |
| Teemburra Dam | Sunwater | 10.1 | 2029-07-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 290.00 m. Lean Forward: Storage elevation exceeds EL 291.32 m. Stand Up 1: Storage elevation exceeds EL 292.70 m (top of clay core at Saddle Dam 1). Stand Up 2: Storage elevation exceeds EL 294.70 m (Saddle Dam 1 overtopping allowing for wave action). (+1 alternate pathway) |
| Tinaroo Falls Dam | Sunwater | 10.2 | 2026-09-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 670.32 m and is rising. Lean Forward: Storage elevation exceeds EL 670.42 m. Stand Up 1: Storage elevation exceeds EL 671.92 m (greater than moderate flood level). Stand Up 2: Storage elevation exceeds EL 672.74 m (greater than Flood of Record). Stand Up 3: Storage elevation exceeds EL 674.31 m (non-overflow section trigger). |
| Wappa Dam | Seqwater | 11.1 | 2028-05-01 | partial_public_assessment_supported | Alert: Lake level is at or above FSL 44.81 m AHD and a relevant BOM flood warning is expected. Lean Forward: Current lake level reaches the Flood of Record level of 46.68 m AHD. (+1 alternate pathway) Stand Up 1: Extreme Flood Level 48.00 m AHD plus the EAP’s dam failure judged unlikely criterion. Stand Up 2: Extreme Flood Level 48.00 m AHD plus the EAP’s dam failure possible but unlikely within 12 hours criterion. Stand Up 3: Extreme Flood Level 48.00 m AHD plus the EAP’s dam failure occurring or likely within 12 hours criterion. |
| Wivenhoe Dam | Seqwater | 10.3 | 2027-05-01 | partial_public_assessment_supported | Alert: Possible Flood Event commencement and relevant BOM warning criteria. Lean Forward: Flood Event likely due to significant catchment rainfall. Stand Up 1: Level at or above OFSL 65.90 m AHD and Flood Event commenced under the Flood Manual. (+1 alternate pathway) Stand Up 2: Level reaches 75.06 m AHD and failure is possible but unlikely within 12 hours. Stand Up 3: Level reaches 75.70 m AHD and failure is occurring or likely within 12 hours. |
| Wuruma Dam | Sunwater | 8.2 | 2027-01-01 | partial_public_assessment_supported | Alert: Storage elevation reaches EL 228.19 m and is rising. Lean Forward: Storage elevation exceeds EL 228.29 m. Stand Up 1: Storage elevation exceeds EL 229.29 m (moderate flood level). Stand Up 2: Storage elevation exceeds EL 232.03 m (greater than January 2013 Flood of Record). Stand Up 3: Storage elevation exceeds EL 239.27 m (saddle embankment crest allowing for wave action). (+1 alternate pathway) |
| Wyaralong Dam | Seqwater | 11.0 | 2029-07-01 | partial_public_assessment_supported | Alert: Lake level at or above FSL 63.60 m AHD and relevant BOM warning expected. Lean Forward 1: Current lake level reaches Flood of Record 65.37 m AHD. Lean Forward 2: Lake level is judged likely to reach the secondary spillway level of 66.30 m AHD. Stand Up 1: Extreme Flood Level 69.00 m AHD plus failure judged unlikely. Stand Up 2: Extreme Flood Level 69.00 m AHD plus failure possible but unlikely within 12 hours. Stand Up 3: Extreme Flood Level 69.00 m AHD plus failure occurring or likely within 12 hours. |

## Detailed audited records

### Atkinson Dam (`atkinson-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **2025-09-01**
- Issue date: **not resolved/not shown**
- Expiry date: **2028-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0010/1619632/atkinson-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 65.72 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 66.62 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 66.62 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 67.50 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 67.50 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 67.50 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 65.72 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 65.72 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Baroon Pocket Dam (`baroon-pocket-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **2025-09-01**
- Issue date: **not resolved/not shown**
- Expiry date: **2028-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0003/1619634/baroon-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 217.00 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 219.62 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 219.62 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 221.50 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 221.50 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 221.50 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 217.00 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 217.00 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Bill Gunn Dam (`bill-gunn-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11**
- Approval date: **2026-02-25**
- Issue date: **not resolved/not shown**
- Expiry date: **2030-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619637/bill-gunn-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 110.00 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 110.65 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 110.65 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 111.00 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 111.00 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 111.00 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 110.00 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 110.00 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Bjelke-Petersen Dam (`bjelke-petersen-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2027-10-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0007/1619638/bjelke-petersen-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 307.20 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 20 |
| lean_forward / default | Storage elevation at or above EL 307.30 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_1 / level | Storage elevation at or above EL 310.20 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_2 / level | Storage elevation at or above EL 311.82 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_3 / level | Storage elevation at or above EL 317.45 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 20 |
| stand_up_3 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 20 |
| stand_down / default | Storage at or below EL 307.40 m **AND** Storage is falling **AND** no forecast increase in elevation | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 20 |

Implementation notes:
- At the highest Stand Up stage, assess possible impacts to Paradise Dam; this is an operational/cascade consideration, not a separate public level trigger.

Formal activation: **Not confirmed**.

### Boondooma Dam (`boondooma-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **9.2**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2028-04-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0009/1619640/boondooma-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 280.30 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 16 |
| lean_forward / default | Storage elevation at or above EL 280.40 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_1 / level | Storage elevation at or above EL 282.50 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_2 / level | Storage elevation at or above EL 286.56 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_3 / level | Storage elevation at or above EL 296.70 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 16 |
| stand_up_3 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 16 |
| stand_down / default | Storage at or below EL 280.50 m **AND** Storage is falling **AND** no forecast increase in elevation | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 16 |

Formal activation: **Not confirmed**.

### Borumba Dam (`borumba-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **2025-09-01**
- Issue date: **not resolved/not shown**
- Expiry date: **2027-06-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0010/1619641/borumba-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 135.01 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 141.02 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 141.02 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 143.50 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 143.50 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 143.50 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 135.01 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 135.01 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Burdekin Falls Dam (`burdekin-falls-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **9.4**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2027-05-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619644/burdekin-falls-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 153.90 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 19 |
| lean_forward / default | Storage elevation at or above EL 154.00 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_1 / level | Storage elevation at or above EL 157.00 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_2 / level | Storage elevation at or above EL 160.85 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_3 / level | Storage elevation at or above EL 162.00 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_4 / level | Storage elevation at or above EL 171.00 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 19 |
| stand_up_4 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 19 |
| stand_down / default | Storage at or below EL 154.30 m **AND** Storage is falling **AND** no forecast increase in elevation | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 19 |

Formal activation: **Not confirmed**.

### Callide Dam (`callide-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **9.0**
- Approval date: **not resolved/not shown**
- Issue date: **2025-05**
- Expiry date: **not resolved/not shown**
- Document status: **change_review_required_operator_link_appears_newer**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0011/1619660/callide-eap.pdf
- Audit result: **rules_extracted_version_comparison_required**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / forecast_combination | Forecast outflow exceeds 200 m³/s using 12-hour forecast rainfall **AND** Storage above EL 212.50 m (about 70%) **AND** Rainfall or streamflow is observed | publicly_observable_only_if_official_outflow_feed_available, publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 19 |
| alert / outflow_band | Published Alert outflow pathway described as up to 130 m³/s | publicly_observable_only_if_official_outflow_feed_available | Flood event activation trigger table, page 19 |
| lean_forward / level | Storage above EL 215.50 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| lean_forward / outflow_band | Published pathway described as outflow up to 370 m³/s | publicly_observable_only_if_official_outflow_feed_available | Flood event activation trigger table, page 19 |
| stand_up_1 / level | Storage above EL 216.37 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_1 / outflow_band | Published pathway described as outflow up to 750 m³/s | publicly_observable_only_if_official_outflow_feed_available | Flood event activation trigger table, page 19 |
| stand_up_2 / level | Storage above EL 216.49 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_2 / outflow_band | Published pathway described as outflow up to 1,500 m³/s | publicly_observable_only_if_official_outflow_feed_available | Flood event activation trigger table, page 19 |
| stand_up_3 / level | Storage above EL 216.66 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_3 / outflow_band | Published pathway described as outflow up to 3,500 m³/s | publicly_observable_only_if_official_outflow_feed_available | Flood event activation trigger table, page 19 |
| stand_up_4 / level | Storage above EL 217.20 m (Flood of Record) | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_4 / outflow | Outflow exceeds 3,500 m³/s | publicly_observable_only_if_official_outflow_feed_available | Flood event activation trigger table, page 19 |
| stand_up_5 / level | Storage above EL 219.13 m allowing for wave action **AND** Wave-action allowance verified | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 19 |
| stand_up_5 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 19 |
| stand_down / default | Storage at or below EL 215.50 m **AND** Storage is falling **AND** No forecast increase for four days | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 19 |

Implementation notes:
- The government-hosted copy extracted for this audit is issue 9.0 (May 2025), but Sunwater’s current operator link points to a filename ending Callide_Dam_EAP_2026.pdf. Treat this as a change-detection flag and compare the 2026 operator copy before production deployment.
- The source table uses “up to” outflow bands. Codex must preserve ranges and must not implement them as simple <= checks without resolving each band’s lower bound from the full table.

Formal activation: **Not confirmed**.

### Cania Dam (`cania-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **10.0**
- Approval date: **not resolved/not shown**
- Issue date: **2025-05**
- Expiry date: **2029-04-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619671/cania-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 331.00 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| lean_forward / default | Storage elevation at or above EL 332.40 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_1 / level | Storage elevation at or above EL 334.45 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_2 / level | Storage elevation at or above EL 338.00 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 19 |
| stand_up_2 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 19 |
| stand_down / default | Storage below EL 331.00 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |

Formal activation: **Not confirmed**.

### Cedar Pocket Dam (`cedar-pocket-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.1**
- Approval date: **2025-09-08**
- Issue date: **not resolved/not shown**
- Expiry date: **2029-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0005/1619672/cedar-pocket-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 101.07 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| alert / road_impact | Lake level reaches 102.20 m AHD, the published additional road-impact Alert trigger. | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 103.28 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 103.28 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 104.50 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 104.50 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 104.50 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 101.07 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 101.07 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Clarendon Dam (`clarendon-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **2025-08-26**
- Issue date: **not resolved/not shown**
- Expiry date: **2027-06-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619675/clarendon-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 96.00 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 96.12 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 96.12 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 96.30 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 96.30 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 96.30 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 96.00 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 96.00 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Coolmunda Dam (`coolmunda-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **9.1**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2029-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0011/1619678/coolmunda-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 314.18 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 18 |
| alert / gates_open | One or more gates are open | not_publicly_observable_gate_operations | Flood event activation trigger table, page 18 |
| lean_forward / default | Storage elevation at or above EL 314.34 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 18 |
| stand_up_1 / level | Storage elevation at or above EL 314.47 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 18 |
| stand_up_2 / level | Storage elevation at or above EL 314.92 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 18 |
| stand_up_3 / level | Storage elevation at or above EL 315.32 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 18 |
| stand_up_3 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 18 |
| stand_up_4 / level | Storage elevation at or above EL 316.58 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 18 |
| stand_up_4 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 18 |
| stand_down / default | Storage below EL 314.07 m **AND** Gates are closed | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_gate_operations | Flood event activation trigger table, page 18 |

Formal activation: **Not confirmed**.

### Cooloolabin Dam (`cooloolabin-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.2**
- Approval date: **2025-08-26**
- Issue date: **not resolved/not shown**
- Expiry date: **2028-05-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0012/1619679/cooloolabin-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 293.00 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| alert / spillway_high | Lake level reaches 296.00 m AHD, the published additional high-spillway Alert trigger. | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 296.48 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 296.48 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 296.60 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 296.60 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 296.60 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 293.00 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 293.00 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Implementation notes:
- At Stand Up, activate the Wappa Dam EAP and assess possible cascade implications.

Formal activation: **Not confirmed**.

### EJ Beardmore Dam (`e-j-beardmore-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **9.2**
- Approval date: **not resolved/not shown**
- Issue date: **2024-09**
- Expiry date: **2026-08-01**
- Document status: **current_near_expiry**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619635/beardmore-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 207.02 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 17 |
| lean_forward / default | Storage elevation at or above EL 207.12 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 17 |
| stand_up_1 / level | Storage elevation at or above EL 207.87 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 17 |
| stand_up_2 / level | Storage elevation at or above EL 208.32 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 17 |
| stand_up_3 / level | Storage elevation at or above EL 208.65 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 17 |
| stand_up_3 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 17 |
| stand_down / default | Storage at or below EL 207.12 m **AND** Storage is falling **AND** at FSL and falling/no forecast increase | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 17 |

Formal activation: **Not confirmed**.

### Enoggera Dam (`enoggera-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.3**
- Approval date: **2026-03-09**
- Issue date: **not resolved/not shown**
- Expiry date: **2027-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0003/1619706/enoggera-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Lake level at or above FSL 74.40 m AHD **AND** Relevant BOM flood warning expected | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / default | Current or likely lake level at or above 78.60 m AHD (1% AEP level) | publicly_observable_exact_if_live_elevation_datum_matches | Flood Event activation table |
| stand_up_1 / default | Current or likely level at or above 80.00 m AHD **AND** Outflows likely to flood Near-PAR area **AND** Imminent failure indicators absent | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / default | Lake level likely to reach secondary spillway level 80.47 m AHD **AND** Imminent failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / level_and_failure | Lake level likely to reach 82.50 m AHD **AND** Dam failure occurring or likely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / modelled_failure | Hydrologic model indicates overtopping/potential failure at 84.25 m AHD within 12–24 hours | not_publicly_observable_hydrologic_model | Detailed Flood Event activation table |
| stand_down / default | Lake level below FSL 74.40 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |

Implementation notes:
- Stand Up stages contain downstream-impact and failure-judgement conditions; storage level alone is not sufficient.

Formal activation: **Not confirmed**.

### Eungella Dam (`eungella-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **9.0**
- Approval date: **not resolved/not shown**
- Issue date: **2024-11**
- Expiry date: **2029-03-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0005/1619708/eungella-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 562.71 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| lean_forward / default | Storage elevation at or above EL 566.04 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_1 / level | Storage elevation at or above EL 569.21 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 20 |
| stand_up_1 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 20 |
| stand_down / default | Storage at or below EL 563.00 m **AND** Storage is falling **AND** no forecast increase for 48 hours | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 20 |

Formal activation: **Not confirmed**.

### Ewen Maddock Dam (`ewen-maddock-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.5**
- Approval date: **2025-08-26**
- Issue date: **not resolved/not shown**
- Expiry date: **2026-06-30**
- Document status: **expired_but_still_listed**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619709/ewen-maddock-eap.pdf
- Audit result: **rules_extracted_but_document_expired**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 25.38 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 26.92 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 26.92 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 27.50 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 27.50 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 27.50 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 25.38 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 25.38 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Fairbairn Dam (`fairbairn-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **11.2**
- Approval date: **2025-09-29**
- Issue date: **2025-09**
- Expiry date: **2028-03-14**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619711/fairbairn-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 204.13 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 26 |
| lean_forward / default | Storage elevation at or above EL 204.23 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 26 |
| stand_up_1 / level | Storage elevation at or above EL 207.73 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 26 |
| stand_up_2 / level | Storage elevation at or above EL 209.80 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 26 |
| stand_up_3 / level | Storage elevation at or above EL 217.39 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 26 |
| stand_up_3 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 26 |
| stand_down / default | Storage at or below EL 204.73 m **AND** Storage is falling **AND** no forecast increase for 48 hours | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 26 |

Implementation notes:
- The FODM may activate before the tabulated levels based on forecast rainfall and flood modelling. The uploaded official PDF is issue 11.2, September 2025, expiring 14 March 2028.

Formal activation: **Not confirmed**.

### Fred Haigh Dam (`fred-haigh-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **9.1**
- Approval date: **2026-03-24**
- Issue date: **2026-03**
- Expiry date: **2029-05-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0010/1619713/fred-haigh-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 75.46 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 16 |
| lean_forward / default | Storage elevation at or above EL 75.56 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_1 / level | Storage elevation at or above EL 77.06 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_2 / level | Storage elevation at or above EL 82.42 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_3 / level | Storage elevation at or above EL 85.94 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 16 |
| stand_up_3 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 16 |
| stand_down / default | Storage at or below EL 75.86 m **AND** Storage is falling **AND** no forecast increase for 48 hours | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 16 |

Formal activation: **Not confirmed**.

### Glenlyon Dam (`glenlyon-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **8.1**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2027-04-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0011/1619714/glenlyon-eap.pdf
- Audit result: **document_conflict_manual_review_required**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / table_value | Quick-reference/table Alert value above FSL 411.73 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| alert / narrative_value | Narrative says EAP is not triggered until 411.63 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| lean_forward / default | Storage elevation at or above EL 413.19 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_1 / default | Storage elevation at or above EL 414.02 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_2 / default | Storage elevation at or above EL 418.00 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_3 / level | Storage elevation at or above EL 423.60 m **AND** Wave-action allowance verified | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 20 |
| stand_up_3 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 20 |
| stand_down / default | Storage at or below EL 412.03 m **AND** Storage is falling **AND** No forecast increase for 48 hours | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 20 |

Implementation notes:
- The current EAP contains an internal Alert-threshold conflict: 411.73 m in the trigger table versus 411.63 m in narrative text. Do not automate Alert until formally clarified.

Formal activation: **Not confirmed**.

### Gold Creek Dam (`gold-creek-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **2025-08-26**
- Issue date: **not resolved/not shown**
- Expiry date: **2028-04-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619716/gold-creek-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 92.75 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| alert / spillway_high | Lake level reaches 95.75 m AHD, the published spillway high-level Alert trigger. | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 96.91 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 96.91 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 99.00 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 99.00 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 99.00 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 92.75 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 92.75 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Hinze Dam (`hinze-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.2**
- Approval date: **2025-09-15**
- Issue date: **not resolved/not shown**
- Expiry date: **2027-12-18**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619720/hinze-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 94.50 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 100.28 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 100.28 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 104.00 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 104.00 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 104.00 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 94.50 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 94.50 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Julius Dam (`julius-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **8.3**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2027-05-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619725/julius-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 223.44 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 16 |
| lean_forward / default | Storage elevation at or above EL 223.54 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_1 / level | Storage elevation at or above EL 228.17 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_down / default | Storage at or below EL 223.54 m **AND** Storage is falling **AND** no forecast increase for 48 hours | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 16 |

Implementation notes:
- The flood trigger table has one Stand Up level; do not manufacture additional Stand Up sub-stages.

Formal activation: **Not confirmed**.

### Kinchant Dam (`kinchant-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **7.2**
- Approval date: **not resolved/not shown**
- Issue date: **2024-09**
- Expiry date: **2027-01-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619727/kinchant-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 57.21 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 20 |
| lean_forward / default | Storage elevation at or above EL 58.00 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_1 / level | Storage elevation at or above EL 58.21 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_2 / level | Storage elevation at or above EL 58.56 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_3 / level | Storage elevation at or above EL 61.21 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 20 |
| stand_up_3 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 20 |
| stand_down / default | Storage at or below EL 57.21 m **AND** Storage is falling **AND** no forecast increase | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 20 |

Formal activation: **Not confirmed**.

### Kroombit Dam (`kroombit-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **11.1**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2027-12-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619729/kroombit-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 265.70 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 15 |
| lean_forward / default | Storage elevation at or above EL 265.80 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 15 |
| stand_up_1 / level | Storage elevation at or above EL 267.08 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 15 |
| stand_up_2 / level | Storage elevation at or above EL 267.78 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 15 |
| stand_up_3 / level | Storage elevation at or above EL 268.36 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 15 |
| stand_down / default | Storage at or below EL 266.00 m **AND** Storage is falling **AND** no significant forecast increase for 48 hours | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 15 |

Implementation notes:
- A former 270.20 m flood stage is superseded by the separate overturning/sliding hazard section and must not be implemented as a current flood trigger.

Formal activation: **Not confirmed**.

### Lake MacDonald Dam (`lake-macdonald-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **12.0**
- Approval date: **2025-08-06**
- Issue date: **not resolved/not shown**
- Expiry date: **2029-05-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619736/lake-macdonald-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / siphon | At least one siphon activated to keep the lake at or below OFSL 93.00 m AHD | not_publicly_observable_gate_operations | Emergency activation quick reference — Flood Event |
| alert / bom_warning | Relevant BOM flood warning expected | not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / default | Current or predicted level at or above 94.00 m AHD **AND** Outflows impact Lake Macdonald Drive | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_1 / default | Current or predicted level at or above 95.00 m AHD **AND** No imminent-failure indicators | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / default | Lake level likely to reach 96.00 m AHD **AND** Failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / default | Lake level likely to reach 96.00 m AHD **AND** Failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / default | Lake at or below OFSL 93.00 m AHD **AND** No relevant BOM warning expected | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Implementation notes:
- This EAP is project-specific and applies to the temporary cofferdam/construction operating configuration. Do not apply it after configuration changes without version review.

Formal activation: **Not confirmed**.

### Lake Manchester Dam (`lake-manchester-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.2**
- Approval date: **2025-09-15**
- Issue date: **not resolved/not shown**
- Expiry date: **2028-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0007/1619737/lake-manchester-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 50.90 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 53.34 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 53.34 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 57.00 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 57.00 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 57.00 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 50.90 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 50.90 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Leslie Dam (`leslie-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **8.1**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2027-10-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0003/1619742/leslie-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 472.41 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 19 |
| lean_forward_1 / default | Storage elevation at or above EL 472.51 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| lean_forward_2 / default | Storage elevation at or above EL 472.59 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_1 / level | Storage elevation at or above EL 472.70 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_up_2 / level | Storage elevation at or above EL 473.63 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 19 |
| stand_down / default | Storage at or below EL 472.51 m **AND** Storage is falling **AND** no forecast increase for 48 hours | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 19 |

Formal activation: **Not confirmed**.

### Leslie Harrison Dam (`leslie-harrison-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **2025-09-01**
- Issue date: **not resolved/not shown**
- Expiry date: **2027-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619743/leslie-harrison-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 15.24 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 18.62 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 18.62 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 21.00 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 21.00 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 21.00 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 15.24 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 15.24 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Little Nerang Dam (`little-nerang-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.2**
- Approval date: **2025-09-01**
- Issue date: **not resolved/not shown**
- Expiry date: **2027-12-18**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619745/little-nerang-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 168.02 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 171.74 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 171.74 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 172.00 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 172.00 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 172.00 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 168.02 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 168.02 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Implementation notes:
- At Stand Up, activate the Hinze Dam EAP and assess possible cascade implications.

Formal activation: **Not confirmed**.

### Maroon Dam (`maroon-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **2025-09-08**
- Issue date: **not resolved/not shown**
- Expiry date: **2028-06-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0009/1619748/maroon-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 207.14 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 210.04 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 210.04 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 216.50 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 216.50 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 216.50 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 207.14 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 207.14 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Moogerah Dam (`moogerah-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **2025-09-08**
- Issue date: **not resolved/not shown**
- Expiry date: **2027-08-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619754/moogerah-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 154.81 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 158.64 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 158.64 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 159.50 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 159.50 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 159.50 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 154.81 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 154.81 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Nindooinbah Dam (`nindooinbah-dam`)

- Operator: **Seqwater**
- Directory status: **not_listed**
- Version: **not applicable**
- Approval date: **not resolved/not shown**
- Issue date: **not resolved/not shown**
- Expiry date: **not resolved/not shown**
- Document status: **not_listed_in_current_official_directory**
- Official EAP URL: No listing found
- Audit result: **not_applicable_no_official_eap_listed**

Implementation notes:
- No applicable Nindooinbah Dam EAP was found in the current Queensland referable-dam EAP directory. Do not reuse another dam’s rules.

Formal activation: **Not confirmed**.

### North Pine Dam (`north-pine-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **13.0**
- Approval date: **2025-02-24**
- Issue date: **not resolved/not shown**
- Expiry date: **2029-10-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0010/1619758/north-pine-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Possible commencement of a Flood Event **AND** Relevant BOM warnings expected/current | not_publicly_observable_operator_judgement, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / default | Flood Event likely due to significant catchment rainfall | not_publicly_observable_operator_judgement | Emergency activation quick reference — Flood Event |
| stand_up_1 / flood_event | Flood Event commenced under the Flood Manual | not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_1 / gate_failure | Radial gate failure | not_publicly_observable_gate_operations | Detailed Flood Event activation table |
| stand_up_2 / default | Level reaches Extreme Flood Level 40.30 m AHD **AND** Failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / default | Level reaches maximum flood storage 41.40 m AHD **AND** Failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / default | Lake below OFSL **AND** Flood releases have ceased | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_gate_operations | Detailed Flood Event activation table |

Implementation notes:
- Additional key levels: 41.11 m AHD Flood of Record, 41.12 m AHD winch floor, 41.66 m AHD electrical control gear. These are context levels, not separate activation rules unless the current EAP says otherwise.

Formal activation: **Not confirmed**.

### Paradise Dam (`paradise-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **12.2**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2029-06-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0003/1619760/paradise-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 61.70 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 20 |
| lean_forward / default | Storage elevation at or above EL 61.80 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_1 / level | Storage elevation at or above EL 64.30 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_up_2 / level | Storage elevation at or above EL 71.40 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 20 |
| stand_down / default | Storage at or below EL 63.30 m **AND** Storage is falling | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 20 |

Implementation notes:
- Flood levels above EL 73.30 m transfer to the separate overturning hazard section; do not invent an additional flood Stand Up stage.

Formal activation: **Not confirmed**.

### Peter Faust Dam (`peter-faust-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **9.0**
- Approval date: **2026-04-24**
- Issue date: **2026-04**
- Expiry date: **2029-03-08**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619763/peter-faust-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 85.60 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 17 |
| lean_forward / default | Storage elevation at or above EL 87.08 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 17 |
| stand_up_1 / level | Storage elevation at or above EL 88.80 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 17 |
| stand_up_2 / level | Storage elevation at or above EL 94.23 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 17 |
| stand_up_2 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 17 |
| stand_down / default | Storage at or below EL 85.70 m **AND** Storage is falling **AND** no forecast increase for five days | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 17 |

Formal activation: **Not confirmed**.

### Poona Dam (`poona-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.1**
- Approval date: **2024-09-16**
- Issue date: **not resolved/not shown**
- Expiry date: **2028-05-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0007/1619764/poona-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 152.70 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 152.98 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 152.98 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 153.50 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 153.50 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 153.50 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 152.70 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 152.70 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Implementation notes:
- At Stand Up, activate the Wappa Dam EAP and assess possible cascade implications.

Formal activation: **Not confirmed**.

### Sideling Creek Dam (`sideling-creek-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.1**
- Approval date: **2024-09-16**
- Issue date: **not resolved/not shown**
- Expiry date: **2027-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619770/sideling-creek-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 20.37 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 22.14 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 22.14 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 23.00 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 23.00 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 23.00 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 20.37 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 20.37 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Somerset Dam (`somerset-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.0**
- Approval date: **2025-01-16**
- Issue date: **not resolved/not shown**
- Expiry date: **2028-04-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0005/1619771/somerset-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Lake level within 1 m of current dynamic OFSL **AND** Possible Flood Event commencement **AND** Relevant BOM warning expected/current | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / default | Lake level within 1 m of current dynamic OFSL **AND** Flood Event likely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_1 / flood_event | Level at or above current dynamic OFSL **AND** Flood Event commenced per manual | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_1 / gate_failure | Gate failure | not_publicly_observable_gate_operations | Detailed Flood Event activation table |
| stand_up_2 / default | Level reaches Flood of Record/Extreme Flood Level 106.26 m AHD **AND** Failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / breezeway | Level reaches breezeway trigger when defence wall is not installed **AND** Failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / dam_crest | Level reaches dam crest 108.70 m AHD **AND** Failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / default | Lake below current dynamic OFSL **AND** Flood releases have ceased | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_gate_operations | Detailed Flood Event activation table |

Implementation notes:
- The operating FSL/OFSL can be changed by regulation. Resolve the current authoritative OFSL before assessment. Activate Wivenhoe EAP and assess cascade implications at Stand Up. Percentage full is not a valid substitute.

Formal activation: **Not confirmed**.

### Teemburra Dam (`teemburra-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **10.1**
- Approval date: **not resolved/not shown**
- Issue date: **2025-09**
- Expiry date: **2029-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0006/1619781/teemburra-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 290.00 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 31 |
| lean_forward / default | Storage elevation at or above EL 291.32 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 31 |
| stand_up_1 / level | Storage elevation at or above EL 292.70 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 31 |
| stand_up_2 / level | Storage elevation at or above EL 294.70 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 31 |
| stand_up_2 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 31 |
| stand_down / default | Storage below EL 290.20 m **AND** below 290.20 m and no forecast increase | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 31 |

Formal activation: **Not confirmed**.

### Tinaroo Falls Dam (`tinaroo-falls-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **10.2**
- Approval date: **not resolved/not shown**
- Issue date: **2024-09**
- Expiry date: **2026-09-01**
- Document status: **current_near_expiry**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0008/1619783/tinaroo-falls-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 670.32 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 16 |
| lean_forward / default | Storage elevation at or above EL 670.42 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_1 / level | Storage elevation at or above EL 671.92 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_2 / level | Storage elevation at or above EL 672.74 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_3 / level | Storage elevation at or above EL 674.31 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_down / default | Storage at or below EL 671.42 m **AND** Storage is falling **AND** minor flood level and no forecast increase for 48 hours | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 16 |

Formal activation: **Not confirmed**.

### Wappa Dam (`wappa-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.1**
- Approval date: **2024-09-16**
- Issue date: **not resolved/not shown**
- Expiry date: **2028-05-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0009/1619784/wappa-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / alert_fsl_and_bom_warning | Lake level at or above FSL 44.81 m AHD **AND** BOM expected to issue a relevant flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / current_level | Current lake level at or above Flood of Record 46.68 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| lean_forward / predicted_level | Predicted lake level at or above Flood of Record 46.68 m AHD | not_publicly_observable_hydrologic_model | Emergency activation quick reference — Flood Event |
| stand_up_1 / stand_up_1 | Current or predicted lake level at or above Extreme Flood Level 48.00 m AHD **AND** Dam failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / stand_up_2 | Current or predicted lake level at or above Extreme Flood Level 48.00 m AHD **AND** Dam failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / stand_up_3 | Current or predicted lake level at or above Extreme Flood Level 48.00 m AHD **AND** Dam failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / below_fsl | Lake level below FSL 44.81 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |
| stand_down / no_warning | Lake level at or above FSL 44.81 m AHD **AND** No current relevant BOM flood warning | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.

### Wivenhoe Dam (`wivenhoe-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **10.3**
- Approval date: **2026-05-07**
- Issue date: **not resolved/not shown**
- Expiry date: **2027-05-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0011/1619786/wivenhoe-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Possible Flood Event commencement **AND** Relevant BOM warning expected/current | not_publicly_observable_operator_judgement, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward / default | Flood Event likely due to significant catchment rainfall | not_publicly_observable_operator_judgement | Emergency activation quick reference — Flood Event |
| stand_up_1 / flood_event | Level at or above OFSL 65.90 m AHD **AND** Flood Event commenced per Flood Manual | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_1 / gate_failure | Radial gate failure | not_publicly_observable_gate_operations | Detailed Flood Event activation table |
| stand_up_2 / default | Level reaches Flood of Record 75.06 m AHD **AND** Failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / default | Level reaches centre fuse-plug trigger 75.70 m AHD **AND** Failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / default | Lake below OFSL 65.90 m AHD **AND** Flood releases have ceased | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_gate_operations | Detailed Flood Event activation table |

Implementation notes:
- Additional key levels: 76.20 m AHD left fuse plug, 76.70 m AHD right fuse plug, 80.00 m AHD saddle-dam crests, 80.10 m AHD main embankment. Gate and sluice failures are separate non-public pathways.

Formal activation: **Not confirmed**.

### Wuruma Dam (`wuruma-dam`)

- Operator: **Sunwater**
- Directory status: **listed**
- Version: **8.2**
- Approval date: **not resolved/not shown**
- Issue date: **2024-09**
- Expiry date: **2027-01-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0004/1619788/wuruma-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Storage elevation at or above EL 228.19 m **AND** Storage is rising | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available | Flood event activation trigger table, page 16 |
| lean_forward / default | Storage elevation at or above EL 228.29 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_1 / level | Storage elevation at or above EL 229.29 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_2 / level | Storage elevation at or above EL 232.03 m | publicly_observable_exact_if_live_elevation_datum_matches | Flood event activation trigger table, page 16 |
| stand_up_3 / level | Storage elevation at or above EL 239.27 m **AND** Published level is applied allowing for wave action | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Flood event activation trigger table, page 16 |
| stand_up_3 / dstmd_advice | DSTDM advises activation | not_publicly_observable_operator_judgement | Flood event activation trigger table, page 16 |
| stand_down / default | Storage at or below EL 228.39 m **AND** Storage is falling **AND** no forecast increase | publicly_observable_exact_if_live_elevation_datum_matches, publicly_observable_if_sufficient_live_history_available, not_publicly_observable_without_official_matching_forecast | Flood event activation trigger table, page 16 |

Formal activation: **Not confirmed**.

### Wyaralong Dam (`wyaralong-dam`)

- Operator: **Seqwater**
- Directory status: **listed**
- Version: **11.0**
- Approval date: **2025-04-29**
- Issue date: **not resolved/not shown**
- Expiry date: **2029-07-01**
- Document status: **current**
- Official EAP URL: https://www.dlgwv.qld.gov.au/__data/assets/pdf_file/0005/1619789/wyaralong-eap.pdf
- Audit result: **partial_public_assessment_supported**

| Activation/pathway | Conditions | Assessability | Source |
|---|---|---|---|
| alert / default | Lake level at or above FSL 63.60 m AHD **AND** Relevant BOM flood warning expected | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_without_official_bom_warning_product | Emergency activation quick reference — Flood Event |
| lean_forward_1 / default | Current or predicted level at or above Flood of Record 65.37 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Detailed Flood Event activation table |
| lean_forward_2 / default | Lake level judged likely to reach secondary spillway 66.30 m AHD | not_publicly_observable_hydrologic_model | Detailed Flood Event activation table |
| stand_up_1 / default | Level reaches Extreme Flood Level 69.00 m AHD **AND** Failure judged unlikely | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_2 / default | Level reaches Extreme Flood Level 69.00 m AHD **AND** Failure possible but unlikely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_up_3 / default | Level reaches Extreme Flood Level 69.00 m AHD **AND** Failure occurring or likely within 12 hours | publicly_observable_exact_if_live_elevation_datum_matches, not_publicly_observable_operator_judgement | Detailed Flood Event activation table |
| stand_down / default | Lake below FSL 63.60 m AHD | publicly_observable_exact_if_live_elevation_datum_matches | Emergency activation quick reference — Flood Event |

Formal activation: **Not confirmed**.
