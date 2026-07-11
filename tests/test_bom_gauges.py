import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.update_dam_data import parse_bom_bulletin_page, join_observations, freshness, build_gauges, Registry, fetch_bom_bulletins

URL='https://www.bom.gov.au/cgi-bin/wrap_fwo.pl?IDQ60286.html'

class BomGaugeTests(unittest.TestCase):
    def records(self):
        return parse_bom_bulletin_page(Path('tests/fixtures/bom_bulletin_sample.html').read_text(), URL)
    def test_parser_columns_metadata_links_time(self):
        r=self.records()[0]
        self.assertEqual(r['height_m'], 0.78)
        self.assertEqual(r['tendency'], 'falling')
        self.assertEqual(r['bom_station_number'], '540054')
        self.assertEqual((r['minor_flood_m'], r['moderate_flood_m'], r['major_flood_m']), (1.0,2.0,3.0))
        self.assertEqual(r['plot_url'], 'https://www.bom.gov.au/fwo/IDQ65388/IDQ65388.540054.plt.shtml')
        self.assertEqual(r['table_url'], 'https://www.bom.gov.au/fwo/IDQ65388/IDQ65388.540054.tbl.shtml')
        self.assertEqual(r['observed_at'], '2024-07-12T14:46:00+10:00')
        self.assertLessEqual(datetime.fromisoformat(r['observed_at']), datetime.fromisoformat(r['bulletin_issue_time']))
    def test_join_priority_and_ambiguous_names(self):
        obs=self.records()[0]
        network=[{'id':'n1','bom_station_number':'540054','awrc_stateid':'x','name':'Different Name'}, {'id':'n2','bom_station_number':'999','awrc_stateid':'y','name':'Example Station'}, {'id':'n3','bom_station_number':'998','awrc_stateid':'z','name':'Example Station'}]
        joined, stats=join_observations(network, [obs, {**obs, 'bom_station_number':None, 'station_number':None}])
        self.assertEqual(next(g for g in joined if g['id']=='n1')['join_method'], 'station_number')
        self.assertEqual(len(stats['unmatched']), 1)
    def test_stale_freshness(self):
        old=(datetime.now(timezone(timedelta(hours=10)))-timedelta(hours=25)).isoformat()
        self.assertEqual(freshness(old, 1.0)['freshness_status'], 'stale')

    def test_bulletin_index_failure_uses_fallback_failures_without_raising(self):
        class Response:
            text = ''
            def raise_for_status(self):
                raise RuntimeError('403 Forbidden')
        class Session:
            def get(self, *args, **kwargs):
                return Response()
        records, stats = fetch_bom_bulletins(Session())
        self.assertEqual(records, [])
        self.assertGreaterEqual(stats['attempted'], 1)
        self.assertEqual(stats['succeeded'], 0)
        self.assertGreaterEqual(len(stats['failures']), 1)

    def test_network_locations_publish_without_bulletin_observations(self):
        dams=[{'id':'dam-a','name':'Example Dam','operator':'Seqwater','latitude':-27.1,'longitude':153.1,'aliases':[]}]
        network=[{'id':'540054','bom_station_number':'540054','awrc_stateid':None,'name':'Example Station','latitude':-27.0,'longitude':153.0,'state':'QLD','basin':'Basin','agency':'BOM'}]
        out=build_gauges(Registry(dams), [], [], {}, network)
        self.assertEqual(len(out['gauges']), 1)
        self.assertEqual(out['gauges'][0]['current']['freshness_status'], 'unavailable')
        self.assertEqual(out['stats']['qld_network_gauges'], 1)

    def test_statewide_and_dam_share_enriched_record(self):
        dams=[{'id':'dam-a','name':'Example Dam','operator':'Seqwater','latitude':-27.1,'longitude':153.1,'aliases':[]}]
        network=[{'id':'540054','bom_station_number':'540054','awrc_stateid':None,'name':'Example Station','latitude':-27.0,'longitude':153.0,'state':'QLD','basin':'Basin','agency':'BOM'}]
        overrides={'dam-a':[{'id':'540054','relationship':'verified downstream gauge','confidence':'verified'}]}
        out=build_gauges(Registry(dams), [], self.records(), overrides, network)
        self.assertEqual(out['gauges'][0]['current']['height_m'], out['dams']['dam-a'][0]['current']['height_m'])
        self.assertEqual(out['dams']['dam-a'][0]['relationship'], 'verified downstream gauge')
        self.assertEqual(out['dams']['dam-a'][0]['confidence'], 'verified')

if __name__ == '__main__':
    unittest.main()
