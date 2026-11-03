import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from edit_video import load_plan, export_draft
from sound_edit import choose_sfx_track


class StoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for name in ['a.mov','b.mov']:(self.root/name).write_bytes(b'video')
        self.plan={'schema_version':3,'sources':{'a':'a.mov','b':'b.mov'},'project_prefix':'AIEditor_Test_Story',
                   'timeline':{'name':'Test','width':1080,'height':1920,'fps':30},'output_dir':'out',
                   'segments':[{'source':'b','in_seconds':1,'out_seconds':2,'zoom':1,'zoom_end':1.1}],
                   'captions':[{'in_seconds':0,'out_seconds':1,'text':'TEST','emphasis':False}],
                   'style':{'preset':'bold-party-v3'},'color':{'preset':'iphone-hlg-to-sdr-v1'}}

    def load(self,plan):
        path=self.root/'plan.json';path.write_text(json.dumps(plan));return load_plan(path)

    def test_multiple_sources_and_zoom_end(self):
        result=self.load(self.plan)
        self.assertEqual(result['sources']['b'],str((self.root/'b.mov').resolve()))
        self.assertEqual(result['segments'][0]['source'],'b')
        self.assertEqual(result['segments'][0]['zoom_end'],1.1)

    def test_reject_unknown_source_missing_file_or_color(self):
        for changes in ['reference','missing','color','zoom']:
            plan=copy.deepcopy(self.plan)
            if changes=='reference':plan['segments'][0]['source']='absent'
            if changes=='missing':plan['sources']['b']='missing.mov'
            if changes=='color':plan['color']['preset']='HDR guessing'
            if changes=='zoom':plan['segments'][0]['zoom_end']=2
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.load(plan)

    def test_reuse_compatible_track_without_addtrack(self):
        class Clip:
            def GetClipProperty(self,key):return '1'
        class Timeline:
            def GetTrackCount(self,kind):return 3
            def GetItemListInTrack(self,kind,index):return []
            def GetTrackSubType(self,kind,index):return 'mono' if index==2 else 'stereo'
            def AddTrack(self,*args):raise AssertionError('No volver a crear pistas')
        self.assertEqual(choose_sfx_track(Timeline(),{'x':Clip()}),2)
        class Full(Timeline):
            def GetItemListInTrack(self,kind,index):return [object()]
        with self.assertRaises(ValueError):choose_sfx_track(Full(),{'x':Clip()})

    def test_render_async_saves_before_start_and_has_sdr_tags(self):
        class Project:
            rendering=False
            def GetName(self):return 'AIEditor_Test_Story'
            def GetRenderCodecs(self,*args):return {'H.264':'H264'}
            def SetCurrentRenderFormatAndCodec(self,*args):return True
            def SetCurrentRenderMode(self,*args):return True
            def SetRenderSettings(self,settings):self.settings=settings;return True
            def AddRenderJob(self):return 'job'
            def StartRendering(self,*args):self.rendering=True;return True
        project=Project()
        class Manager:
            def ExportProject(self,name,path,*args):Path(path).write_bytes(b'drp');return True
            def SaveProject(self):
                if project.rendering:raise AssertionError('No guardar durante render')
                return True
        report={'run_dir':str(self.root)}
        export_draft(project,Manager(),self.plan,report,lambda:None,10,wait=False)
        self.assertEqual(report['stage'],'render_started')
        self.assertEqual(project.settings['ColorSpaceTag'],'Rec.709')
        self.assertEqual(project.settings['GammaTag'],'Gamma 2.4')


if __name__=='__main__':unittest.main()
