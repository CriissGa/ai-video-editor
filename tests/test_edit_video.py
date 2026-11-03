import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from edit_video import load_plan, source_ranges, frame, verify_timeline


class EditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'input.MOV').write_bytes(b'media')
        self.plan = {'schema_version': 1, 'source': 'input.MOV', 'output_dir': 'out',
                     'project_prefix': 'AIEditor_Test_Unit',
                     'timeline': {'name': 'Test', 'width': 1080, 'height': 1920, 'fps': 30},
                     'segments': [{'in_seconds': 1, 'out_seconds': 2}]}
        self.props = {'FPS': 30, 'Frames': '90', 'Resolution': '1080x1920', 'Audio Ch': '2'}

    def load(self, plan):
        path = self.root / 'plan.json'
        path.write_text(json.dumps(plan))
        return load_plan(path)

    def test_paths_and_ranges(self):
        result = self.load(self.plan)
        self.assertEqual(result['source'], str((self.root / 'input.MOV').resolve()))
        self.assertEqual(source_ranges(result, self.props), [(30, 60)])
        self.assertEqual(frame(0.05, 30), 2)

    def test_reject_invalid_before_resolve(self):
        for key, value in [('schema_version', True), ('project_prefix', 'Existing'),
                           ('source', 'missing.mov'), ('segments', []),
                           ('segments', [{'in_seconds': 2, 'out_seconds': 1}]),
                           ('segments', [{'in_seconds': False, 'out_seconds': 2}]),
                           ('segments', [{'in_seconds': 0, 'out_seconds': float('nan')}])]:
            with self.subTest(key=key, value=value):
                plan = copy.deepcopy(self.plan)
                plan[key] = value
                with self.assertRaises(ValueError):
                    self.load(plan)
        plan = copy.deepcopy(self.plan)
        plan['extra'] = 1
        with self.assertRaises(ValueError):
            self.load(plan)

    def test_source_restrictions(self):
        for changes in [{'FPS': 25}, {'Resolution': '1920x1080'}, {'Audio Ch': '0'}, {'Frames': '40'}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                source_ranges(self.plan, dict(self.props, **changes))
        self.plan['segments'] = [{'in_seconds': 0.001, 'out_seconds': 0.002}]
        with self.assertRaises(ValueError):
            source_ranges(self.plan, self.props)

    def test_timeline_detects_wrong_audio_cut(self):
        class Item:
            def GetStart(self): return 108000
            def GetDuration(self): return 30
            def GetLeftOffset(self): return self.offset
            offset = 30
        class Timeline:
            def GetStartFrame(self): return 108000
            def GetEndFrame(self): return 108030
            def GetTrackCount(self, kind): return 1
            def GetItemListInTrack(self, kind, index): return [self.video if kind == 'video' else self.audio]
            video, audio = Item(), Item()
        tl = Timeline()
        self.assertEqual(verify_timeline(tl, [(30, 60)]), 30)
        tl.audio.offset = 29
        with self.assertRaises(ValueError):
            verify_timeline(tl, [(30, 60)])


if __name__ == '__main__':
    unittest.main()
