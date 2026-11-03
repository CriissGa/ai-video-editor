import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from caption_style import caption_intersections, validate_style, write_srt
from prepare_captions import generate_captions
from transcribe_video import normalize, timecode_frame


class CaptionTests(unittest.TestCase):
    def setUp(self):
        self.plan = {'timeline': {'fps': 30}, 'segments': [{'in_seconds': 10, 'out_seconds': 12}],
                     'style': {'preset': 'bold-yellow-v1'},
                     'captions': [{'in_seconds': 0, 'out_seconds': 1, 'text': 'FIRST TIME', 'emphasis': True}]}

    def test_timecodes_relative_to_source(self):
        raw = {'segments': [{'words': [{'start': '01:00:01:15', 'end': '01:00:02:00', 'text': 'hello'},
                                      {'start': '01:00:02:00', 'end': '01:00:03:00', 'text': '(...)'}]}]}
        props = {'FPS': 30, 'Start TC': '01:00:00:00', 'Frames': '90'}
        self.assertEqual(normalize(raw, props), [{'start_frame': 45, 'end_frame': 60, 'text': 'hello'}])
        for tc in ['00:00:00:30', '00:60:00:00', '00:00:01;00']:
            with self.assertRaises(ValueError):
                timecode_frame(tc, 30)
        raw['segments'][0]['words'][0]['end'] = '01:00:04:00'
        with self.assertRaises(ValueError):
            normalize(raw, props)

    def test_caption_rejects_overlap_outside_and_too_long(self):
        validate_style(self.plan)
        for changes in [{'out_seconds': 3}, {'text': 'x' * 25}, {'emphasis': 1}, {'in_seconds': float('nan')}]:
            plan = copy.deepcopy(self.plan)
            plan['captions'][0].update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_style(plan)
        plan = copy.deepcopy(self.plan)
        plan['captions'].append(dict(plan['captions'][0]))
        with self.assertRaises(ValueError):
            validate_style(plan)

    def test_intersection_across_edit_boundary(self):
        captions = [{'in_seconds': 0.5, 'out_seconds': 1.5}]
        self.assertEqual(caption_intersections(captions, 30, 0, 30)[0][1:], (15, 30))
        self.assertEqual(caption_intersections(captions, 30, 30, 30)[0][1:], (0, 15))
        self.assertEqual(caption_intersections(captions, 30, 60, 30), [])

    def test_reordered_segments_map_to_timeline(self):
        plan = {'timeline': {'fps': 30}, 'segments': [{'in_seconds': 10, 'out_seconds': 12},
                                                       {'in_seconds': 1, 'out_seconds': 2}]}
        transcript = {'fps': 30, 'source_frames': 600, 'words': [
            {'start_frame': 30, 'end_frame': 45, 'text': 'Earlier.'},
            {'start_frame': 300, 'end_frame': 330, 'text': 'Later.'}]}
        captions = generate_captions(plan, transcript)
        self.assertEqual([c['text'] for c in captions], ['LATER.', 'EARLIER.'])
        self.assertEqual([c['in_seconds'] for c in captions], [0, 2])

    def test_srt_uses_frame_quantization(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'captions.srt'
            write_srt(self.plan['captions'], 30, path)
            self.assertIn('00:00:00,000 --> 00:00:01,000', path.read_text())
            self.assertIn('FIRST TIME', path.read_text())


if __name__ == '__main__':
    unittest.main()
