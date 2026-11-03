import array
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from sound_edit import validate_audio
from prepare_sounds import analyze
from prepare_captions import generate_captions
from edit_video import load_plan


class SoundTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / 'tone.wav'
        samples = array.array('h', [0] * (48000 * 2))
        for i in range(9600,19200): samples[i] = 16384 if i % 2 else -16384
        with wave.open(str(self.path), 'wb') as target:
            target.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
            if sys.byteorder != 'little': samples.byteswap()
            target.writeframes(samples.tobytes())
        self.sound = {'source': 'tone.wav', 'in_seconds': 0.1, 'out_seconds': 0.4,
                      'at_seconds': 1, 'gain_db': -20, 'fade_in_frames': 1, 'fade_out_frames': 2}
        self.audio = {'dialogue_gain_db': -3, 'sounds': [self.sound]}

    def test_pcm_peak_and_region(self):
        result = analyze(self.path)
        self.assertAlmostEqual(result['duration_seconds'], 1)
        self.assertAlmostEqual(result['sample_peak_dbfs'], -6.02, places=2)
        self.assertEqual(len(result['regions']), 1)
        self.assertLessEqual(result['regions'][0]['in_seconds'], 0.1)
        self.assertGreaterEqual(result['regions'][0]['out_seconds'], 0.2)

    def test_validate_paths_and_bounds(self):
        validate_audio(self.audio, self.root / 'plan.json', 30, 90)
        self.assertEqual(self.audio['sounds'][0]['source'], str(self.path.resolve()))
        for changes in [{'out_seconds': 2}, {'gain_db': 3}, {'at_seconds': 3},
                        {'fade_out_frames': 30}, {'source': 'absent.wav'}]:
            audio = copy.deepcopy(self.audio)
            audio['sounds'][0].update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_audio(audio, self.root / 'plan.json', 30, 90)
        audio = copy.deepcopy(self.audio)
        audio['sounds'].append(dict(self.sound))
        with self.assertRaises(ValueError):
            validate_audio(audio, self.root / 'plan.json', 30, 90)

    def test_malformed_wav_rejected(self):
        self.path.write_bytes(b'bad')
        with self.assertRaises(ValueError):
            validate_audio(self.audio, self.root / 'plan.json', 30, 90)

    def test_plan_audio_resolves_before_execute(self):
        source = self.root / 'test.mov'
        source.write_bytes(b'video')
        plan = {'schema_version': 2, 'source': 'test.mov', 'output_dir': 'out',
                'project_prefix': 'AIEditor_Test_Audio', 'timeline': {'name': 'Test', 'width':1080,'height':1920,'fps':30},
                'segments':[{'in_seconds':0,'out_seconds':3,'zoom':1}], 'style':{'preset':'bold-party-v3'},
                'captions':[{'in_seconds':0,'out_seconds':1,'text':'TEST','emphasis':False}], 'audio':self.audio}
        path = self.root / 'plan.json'
        path.write_text(json.dumps(plan))
        self.assertEqual(load_plan(path)['audio']['sounds'][0]['source'], str(self.path.resolve()))

    def test_native_audio_guard_precedes_connection(self):
        import edit_video
        with patch.object(sys, 'argv', ['edit_video.py', 'plan.json', '--execute']), \
             patch.object(edit_video, 'load_plan', return_value={'audio': self.audio}), \
             patch.object(edit_video, 'diagnose') as diagnostic:
            self.assertEqual(edit_video.main(), 1)
            diagnostic.assert_not_called()

    def test_focus_words_get_own_caption(self):
        plan = {'timeline':{'fps':30},'segments':[{'in_seconds':0,'out_seconds':2}]}
        words = [{'start_frame':i*10,'end_frame':(i+1)*10,'text':text} for i,text in enumerate(['soy','PROFESIONAL,','maybe.'])]
        captions=generate_captions(plan,{'fps':30,'source_frames':60,'words':words},'bold-party-v3')
        self.assertEqual([c['text'] for c in captions], ['SOY','PROFESIONAL,','MAYBE.'])
        self.assertEqual([c['emphasis'] for c in captions], [False,True,False])


if __name__ == '__main__':
    unittest.main()
