import copy
import io
import json
import unittest
from stt_monitor.protocol import encode, decode
from stt_monitor.perf_analyze import analyze

def sample():
    return dict(version=4,session='synthetic',source='simulator',seq=0,uptime_ms=1000,battery_pct=70,
        perf=dict(tick=60,frames=12,window_us=1000000,update_us=500,render_us=70000,present_us=12000,
        telemetry_us=30,equipment=2,ground_mode=1,cpu_mhz=333,gpu_mhz=111,xbar_mhz=111,
        ram_free=1000000,cdram_free=2000000,phy_free=None,cdlg_free=None,cpu_load_pct=None,
        gpu_load_pct=None,fg_app=None,vnz=None,send_ok=0,send_errors=0))

class PerfTests(unittest.TestCase):
    def test_trial_targets_are_separate(self):
        a=sample();a["session"]="vita-0019-f45-abc"
        b=copy.deepcopy(a);b["session"]="vita-0019-f30-def"
        groups=analyze({"packet":p} for p in (a,b))["groups"]
        self.assertEqual([g["target_fps"] for g in groups],[45,30])
        self.assertEqual(groups[0]["build"],"00.19")
        self.assertIsNone(analyze([{"packet":sample()}])["groups"][0]["target_fps"])
    def test_roundtrip(self):
        p=sample();self.assertEqual(decode(encode(p)),p)
    def test_no_fabricated_counters(self):
        for key in ('cpu_load_pct','gpu_load_pct','fg_app','vnz'):
            p=sample();p['perf'][key]=0
            with self.assertRaises(ValueError):encode(p)
    def test_ranges_and_duplicates(self):
        for key,value in [('frames',0),('window_us',0),('ram_free',-1),('cpu_mhz',True),('equipment',4)]:
            p=sample();p['perf'][key]=value
            with self.assertRaises(ValueError):encode(p)
        with self.assertRaises(ValueError):decode(b'{"version":4,"version":4}')
    def test_weighted_fps_and_separate_modes(self):
        a=sample();b=copy.deepcopy(a);b['seq']=1;b['perf']['frames']=24;b['perf']['window_us']=2000000
        c=copy.deepcopy(a);c['seq']=2;c['perf']['ground_mode']=0
        result=analyze({'packet':p} for p in [a,b,c,a])
        self.assertEqual(result['duplicate_packets_ignored'],1)
        self.assertEqual(len(result['groups']),2)
        self.assertEqual(result['groups'][0]['fps'],12)
        self.assertIsNone(result['groups'][0]['minimum_free_bytes']['phy_free'])
    def test_v5_stages_and_raster_modes(self):
        p=sample();p['version']=5
        p['perf'].update(raster_mode=1,clear_us=100,ground_us=1000,body_us=2000,weapon_us=3000,target_us=400,hud_us=500)
        self.assertEqual(decode(encode(p)),p)
        q=copy.deepcopy(p);q['seq']=1;q['perf']['raster_mode']=0
        result=analyze({'packet':x} for x in [p,q])
        self.assertEqual(len(result['groups']),2)
        self.assertEqual(result['groups'][0]['render_stages_us']['weapon_us'],3000)
        del p['perf']['body_us']
        with self.assertRaises(ValueError):encode(p)
    def test_v6_ground_spans_and_old_range(self):
        p=sample();p['version']=6
        p['perf'].update(ground_mode=2,raster_mode=1,clear_us=1,ground_us=2,body_us=3,weapon_us=4,target_us=5,hud_us=6)
        self.assertEqual(decode(encode(p)),p)
        self.assertEqual(analyze([{'packet':p}])['groups'][0]['ground_mode'],2)
        p['version']=5
        with self.assertRaises(ValueError):encode(p)
    def test_v7_ceiling_contract_and_grouping(self):
        p=sample();p["version"]=7;p["session"]="vita-0020-f45-c2-abc"
        p["perf"].update(ground_mode=2,raster_mode=1,clear_us=1,ground_us=2,body_us=3,weapon_us=4,target_us=5,hud_us=6,ceiling_mode=2,ceiling_us=2300,target_fps=45)
        self.assertEqual(decode(encode(p)),p)
        q=copy.deepcopy(p);q["seq"]=1;q["perf"]["ceiling_mode"]=1
        groups=analyze({"packet":x} for x in (p,q))["groups"]
        self.assertEqual(len(groups),2)
        self.assertEqual(groups[0]["ceiling_mode"],2)
        self.assertEqual(groups[0]["render_stages_us"]["ceiling_us"],2300)
        self.assertEqual(groups[0]["target_fps"],45)
        self.assertEqual(groups[0]["build"],"00.20")
        q["seq"]=2;q["perf"]["ceiling_mode"]=2;q["perf"]["target_fps"]=30
        self.assertEqual(len(analyze({"packet":x} for x in (p,q))["groups"]),2)
        for key,value in (("ceiling_mode",3),("ceiling_us",-1),("target_fps",44),("target_fps",True)):
            bad=copy.deepcopy(p);bad["perf"][key]=value
            with self.assertRaises(ValueError):encode(bad)
        del p["perf"]["ceiling_us"]
        with self.assertRaises(ValueError):encode(p)
    def test_receiver_accepts_performance(self):
        from stt_monitor.receiver import receive
        class Socket:
            def settimeout(self,t):pass
            def recvfrom(self,n):return encode(sample()),('127.0.0.1',1234)
        out=io.StringIO();result=receive(Socket(),out,max_packets=1)
        self.assertEqual(result['accepted'],1)
        self.assertEqual(json.loads(out.getvalue())['packet']['version'],4)

if __name__=='__main__':unittest.main()
