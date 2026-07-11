# Codex task: implement the completed 45-dam EAP audit in the current qlddams repository

Work in the **current repository version in this workspace**. Do not apply an older patch or reconstruct the audit from memory. The user will provide these audited files with this prompt:

- `qld_45_dam_eap_audit.json`
- `qld_45_dam_eap_overrides_candidate.json`
- `qld_45_dam_eap_audit.md`

Treat the JSON audit as reviewed source data. Preserve its exact threshold values, compound conditions, alternate pathways, document warnings and source URLs unless you verify a newer official EAP.

The repository is a static GitHub Pages application. Relevant files currently include:

- `config/eap_sources.json`
- `config/eap_overrides.json`
- `data/eap_documents.json`
- `data/eap_status.json`
- `data/latest.json`
- `scripts/update_eap_data.py`
- `scripts/assess_eap_status.py`
- `scripts/validate_data.py`
- `.github/workflows/update-eap-data.yml`
- `index.html`

The recently implemented BOM Queensland river-gauge work and all existing dam collection/history/provider-health functionality must continue to work.

## Completed audit facts

The audit covers all **45 dashboard dams**:

- 44 have an EAP listed in the current official Queensland directory.
- Nindooinbah Dam has no applicable listing and must be represented explicitly as `not_listed`, not as a retrieval error.
- Flood-trigger rules are supplied for all 44 listed dams.
- Formal EAP activation must always remain `not_confirmed`.
- `data/latest.json` currently has `storage_level_m: null` for all 45 dams. Therefore adding the rules does **not** make every dam live-assessable.

The implementation must distinguish:

1. EAP document/rules unavailable;
2. EAP rules verified but live reservoir elevation unavailable;
3. some public conditions available but one or more required conditions unknown;
4. a public condition demonstrably below/false;
5. a public trigger component met;
6. document conflict, expiry or change-review required;
7. not applicable/not listed.

Do not continue showing the generic message “public data does not contain enough information to assess the published flood-trigger rules” when a more precise reason is available.

## Import the audited records

Use `qld_45_dam_eap_audit.json` as the canonical reviewed audit input.

Refactor `config/eap_overrides.json` or introduce a backward-compatible reviewed audit file so every dashboard dam has an explicit audit record.

Preserve:

- document version;
- issue and approval dates;
- expiry;
- official source URL;
- directory status;
- audit result;
- all activation pathways;
- `AND` logic within pathways;
- alternate `OR` pathways as separate rules/pathways;
- condition assessability;
- source section/page;
- implementation notes;
- `formal_activation_status: "not_confirmed"`.

Do not flatten multiple Stand Up stages into one generic threshold where the EAP distinguishes Stand Up 1, 2, 3, 4 or 5.

Do not replace a reviewed record automatically when a live extraction produces different values. Generate a change-review candidate and preserve the reviewed rules until approved.

## Critical special cases

Implement these exactly:

### Callide Dam

The government-hosted issue 9.0 rules were audited, but Sunwater’s current operator link points to a filename ending `Callide_Dam_EAP_2026.pdf`.

- mark the record `change_review_required`;
- preserve the audited rules;
- compare a successfully retrieved current operator PDF before changing thresholds;
- do not treat source-table wording such as “outflow up to 370 m³/s” as a simple `<= 370` trigger;
- model outflow bands only after resolving their lower and upper bounds from the current full table.

### Glenlyon Dam

The current EAP contains a document conflict:

- trigger table Alert: 411.73 m;
- nearby narrative: 411.63 m.

Store both values and mark Alert `document_conflict`. Disable automatic Alert assessment until the owner/regulator clarifies it. Other Glenlyon stages may still be evaluated if their inputs are suitable.

### Ewen Maddock Dam

The audited EAP expired 30 June 2026.

- preserve its audited rules;
- mark the document expired;
- do not describe it as a current verified plan;
- detect and stage a replacement EAP when one becomes available.

### Near-expiry plans

- EJ Beardmore: expires 1 August 2026.
- Tinaroo Falls: expires 1 September 2026.

Expose an expiry warning without suppressing the audited rules.

### Lake Macdonald Dam

The current EAP is construction/cofferdam-specific. Show that context and require version/configuration review before applying it after the project configuration changes.

### Somerset Dam

Somerset uses a dynamic operating full supply level.

- resolve the current authoritative OFSL before comparing;
- never use percentage full as a substitute;
- retain Wivenhoe cascade activation/assessment requirements.

### Nindooinbah Dam

No applicable EAP was found in the current official directory.

Return a clear `not_applicable` result such as:

> No applicable EAP is listed for this dam in the current Queensland referable-dam EAP directory.

Do not reuse another dam’s thresholds.

## Evaluation engine

Update `scripts/assess_eap_status.py` to support:

- separate activation pathways;
- `all` logic within a pathway;
- alternate pathways for the same activation stage;
- stages such as `lean_forward_1`, `stand_up_1` through `stand_up_5`;
- exact public conditions;
- public conditions requiring suitable history;
- official-public-feed-dependent conditions;
- non-public modelling, warning, gate, cascade and operator-judgement conditions;
- document status gates;
- source-data staleness;
- datum verification.

Recommended per-condition states:

- `met`
- `not_met`
- `unknown`
- `input_unavailable`
- `datum_unverified`
- `stale`
- `document_conflict`

Recommended rule results:

- `met`
- `not_met`
- `indeterminate`
- `input_unavailable`
- `document_conflict`
- `document_expired`
- `change_review_required`
- `not_applicable`

A rule cannot be `met` when any required `AND` condition is unknown.

Where a level condition is met but a required non-public condition is unknown, return `indeterminate` and state exactly which condition is unavailable.

For alternate pathways, a stage can be publicly supported only when one complete pathway is met.

Formal activation must always be:

```json
"formal_activation_status": "not_confirmed"
```

## Live data and datum safety

At audit time every record in `data/latest.json` had `storage_level_m: null`.

Do not:

- compare EAP levels to `percent_full`;
- derive elevation from volume without a current official storage curve and an explicitly verified method;
- compare a BOM river-gauge height with a dam storage elevation;
- assume “spilling” means an EAP trigger is met;
- assume a value with unknown datum is AHD.

Extend the collectors to populate `storage_level_m` only from an official operator source that explicitly publishes reservoir/storage elevation with a verified datum.

Store, at minimum:

```json
{
  "storage_level_m": 0.0,
  "storage_level_datum": "AHD",
  "storage_level_observed_at": "...",
  "storage_level_source_url": "...",
  "storage_level_quality": "official_exact"
}
```

For Sunwater, investigate the official station/water-data feeds already used by the repository and capture reservoir level where the station exposes it.

For Seqwater, use an official published lake-level/elevation source if one is available. Where only percentage full and volume are public, leave `storage_level_m` null.

The expected UI result in that case is:

> Verified EAP flood rules are available, but the official live reservoir elevation needed for comparison is not currently available.

That is materially different from “EAP data unavailable”.

## BOM conditions

The BOM gauge layer is contextual and must not be used as a substitute for EAP warning conditions.

A gauge’s flood class or river height does not prove that:

- BOM has issued a relevant flood warning;
- BOM is expected to issue a warning;
- a dam’s modelled reservoir level will be exceeded.

Only an official matching BOM warning product can satisfy a BOM-warning condition. Otherwise leave it unknown.

## Source refresh and last-good behaviour

Update `scripts/update_eap_data.py` to:

- dynamically discover official directory links;
- validate PDF bytes;
- preserve last-good reviewed rules on retrieval failure;
- reject HTML/Cloudflare challenge pages;
- calculate PDF SHA-256 when the actual PDF is retrieved;
- detect version/hash changes;
- generate candidate diffs instead of silently replacing reviewed values;
- retain official source URL, retrieval time and document status;
- tolerate partial provider failure.

Do not require every EAP PDF to download successfully on every run before using reviewed rules.

## Generated output

Update `data/eap_documents.json` and `data/eap_status.json` so each dam exposes:

```json
{
  "dam_id": "...",
  "document_status": "current",
  "version": "...",
  "expiry_date": "...",
  "source_url": "...",
  "indicative_result": "input_unavailable",
  "highest_publicly_supported_level": null,
  "confidence": "rules_verified_live_input_unavailable",
  "formal_activation_status": "not_confirmed",
  "observed_inputs": {
    "storage_level_m": null,
    "storage_level_datum": null
  },
  "rules": [],
  "unavailable_required_inputs": [],
  "reason": "Verified EAP rules are available, but official live reservoir elevation is unavailable."
}
```

Also generate `data/eap_audit_report.json` with:

- total dashboard dams;
- officially listed plans;
- reviewed rules;
- not listed;
- current;
- expired;
- near expiry;
- document conflicts;
- change-review required;
- records with exact live elevation;
- records missing exact live elevation;
- rules currently assessable;
- rules indeterminate due non-public conditions.

## Frontend

Revise the EAP panel in `index.html`.

Display separately:

1. **Indicative result**
2. **Formal activation — Not confirmed**
3. **Document status**
4. **Live-input availability**
5. **Audited rule table**

Use precise messages:

- `Rules verified; live elevation unavailable`
- `Indeterminate — level component met, BOM warning condition unavailable`
- `Below the first public elevation trigger`
- `Document conflict — automatic Alert assessment disabled`
- `EAP expired — replacement required`
- `Change review required`
- `No applicable EAP listed`

Show every activation stage and its conditions with `met`, `not met`, `unknown`, `unavailable`, or `conflict`.

Show:

- document version;
- expiry;
- official source;
- source section/page;
- whether the live datum matches;
- observation age;
- the exact unavailable condition;
- the statement that formal activation is not confirmed.

Do not display “Unable to assess” as the sole explanation.

## Validation

Extend `scripts/validate_data.py` to enforce:

- exactly 45 dashboard audit records;
- 44 listed and one Nindooinbah `not_listed`;
- every listed record has at least one flood rule;
- no duplicate dam IDs;
- finite numeric thresholds;
- valid condition logic;
- official HTTPS source URLs;
- valid document dates where supplied;
- formal activation always `not_confirmed`;
- no rule is `met` with a required unknown condition;
- `storage_level_m` comparisons require compatible datum;
- expired/conflict/change-review statuses cannot be presented as normal current confidence;
- Callide and Glenlyon safeguards remain present;
- all `data/latest.json` dam IDs map to an audit record.

## Tests

Add fixture-based tests covering:

1. all 45 audit records load;
2. Nindooinbah is not applicable;
3. standard Seqwater Alert remains indeterminate when level is met but BOM warning is unknown;
4. Seqwater Lean Forward can be supported by an exact current level;
5. Seqwater Stand Up sub-stage remains indeterminate without failure judgement;
6. Sunwater rising condition is not met without suitable history;
7. Sunwater final wave-action/DSTDM pathway remains indeterminate without operator judgement;
8. Fairbairn stages: 204.13, 204.23, 207.73, 209.80 and 217.39 m;
9. Callide outflow bands are not naively interpreted as simple upper-bound triggers;
10. Glenlyon Alert returns document conflict;
11. Ewen Maddock returns document expired;
12. Somerset refuses percent-full comparison;
13. Lake Macdonald reports construction-specific context;
14. Wivenhoe/North Pine/Somerset gate and Flood Manual conditions remain non-public;
15. a null live elevation produces `rules_verified_live_input_unavailable`;
16. a datum mismatch blocks comparison;
17. formal activation always remains not confirmed;
18. reviewed rules survive a failed PDF refresh.

Tests must not depend on live websites.

## Workflow

Update `.github/workflows/update-eap-data.yml` to:

1. install dependencies;
2. run EAP tests;
3. refresh official document metadata;
4. preserve reviewed last-good rules;
5. assess current status;
6. validate generated output;
7. commit generated EAP files only when valid.

Do not add temporary research workflows or unrelated repository changes.

## Completion checks

Before finishing:

- run all EAP tests;
- run `python scripts/validate_data.py`;
- run the EAP update and assessment scripts;
- confirm exactly 45 status records;
- confirm Nindooinbah is `not_applicable`;
- confirm Callide is `change_review_required`;
- confirm Glenlyon Alert is `document_conflict`;
- confirm Ewen Maddock is expired;
- confirm no percentage-full proxy is treated as exact;
- confirm the BOM gauge layer still works;
- confirm the dashboard no longer conflates “rules missing” with “live elevation missing”;
- report changed files and test results.

Implement the changes directly. Do not return only a plan.
