# Queensland Dam Levels

A live, static GitHub Pages dashboard for the 45 Seqwater and Sunwater dam records represented in the supplied Power BI reports.

## What is included

- Statewide Leaflet map and searchable dam list
- A reusable detail view for every dam
- Current percentage full, stored volume, capacity basis and observation time
- Historical percentage, volume, storage level, outflow, rainfall and river-level charts where the source provides those fields
- Verified and automatically discovered BOM/Queensland river-gauge mappings
- Provider-health reporting and stale-data warnings
- Last-good-data preservation when an upstream source fails
- Responsive mobile layout and persistent dark mode
- Hourly GitHub Actions collection and GitHub Pages deployment

## Repository layout

```text
index.html                         Web application
favicon.svg                        Dashboard icon
config/dams.json                   Canonical 45-dam registry and aliases
config/gauges_overrides.json       Manually verified gauge mappings
data/dams.json                     Published registry
data/latest.json                   Latest normalized observations
data/history/*.json                Per-dam historical observations
data/gauges.json                   Gauge mappings and current bulletin values
data/provider_health.json          Source-health manifest
scripts/update_dam_data.py         Live collector and normalizer
scripts/validate_data.py           Data-contract checks
.github/workflows/update-dam-data.yml
```

## First deployment

1. Create a new GitHub repository and copy the contents of this folder into its `main` branch.
2. In **Settings → Actions → General → Workflow permissions**, select **Read and write permissions**.
3. In **Settings → Pages → Build and deployment**, select **GitHub Actions** as the source.
4. Open **Actions → Update Queensland dam data → Run workflow**.
5. The initial PBIX seed values will be replaced by live values and the site will deploy.

The scheduled workflow then runs at 17 minutes past each hour. GitHub schedules may begin a little later during periods of high platform load.

## Local test

Opening `index.html` directly as `file://` will not work because browsers block its JSON requests. From the repository folder run:

```powershell
py -m http.server 8000
```

Then open `http://localhost:8000`.

To test the collector locally:

```powershell
py -m pip install -r scripts/requirements.txt
py scripts/update_dam_data.py --history-days 400 --verbose
py scripts/validate_data.py
```

## Data-source behaviour

### Seqwater

The collector reads the current dam-level table and submits the historical Drupal form using the page's current form token. It does not use the hard-coded Power BI token. Historical data is normalized from a wide operator structure into one observation stream per dam.

### Sunwater

The collector discovers station identifiers from the Queensland monitoring-station registry and official Sunwater pages, retrieves current API values, and follows every historical continuation token. The first live run backfills up to 30 days per dam; later hourly runs use a small overlapping incremental window. Older high-frequency observations are compacted while recent detail is retained. The public Sunwater dam page is retained as a fallback for current percentage values.

### Gauges

The two PBIX reports supplied five manually verified gauge mappings. For other dams, the collector examines Queensland monitoring stations and BOM river-height bulletins. Exact dam/headwater/tailwater matches are preferred. A station chosen only because it is nearby is explicitly labelled **candidate** and **nearby gauge — relationship not verified**.

## Failure handling

A provider failure does not erase working data. The collector keeps the last good value/history, marks the provider and affected observations accordingly, publishes `provider_health.json`, and deploys the still-usable site. The final workflow job then fails when a required current feed is not healthy, providing a visible GitHub Actions alert after the data has been preserved and deployed.

## Important interpretation notes

- Operator readings can be automated and unverified.
- Values above 100% are intentionally retained.
- Some dams use temporary or seasonal operating capacities, so the published percentage should be read with the capacity note and operator source.
- A nearby river gauge is not necessarily upstream, downstream or otherwise hydrologically connected to a dam.
