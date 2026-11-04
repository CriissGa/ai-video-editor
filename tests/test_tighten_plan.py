import array
import sys
import tempfile
import unittest
import wave
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tighten_plan import tighten


class SilenceTest(unittest.TestCase):
    def test_removes_confirmed_gap_and_preserves_words(self):
        plan={'timeline':{'fps':30},'segments':[{'in_seconds':0,'out_seconds':84/30}]}
        words=[{'start_frame':10,'end_frame':19,'text':'Hola'}, {'start_frame':60,'end_frame':69,'text':'people'}]
        transcript={'words':words,'source_frames':84}
        data=array.array('h',(6000 if 10<=f<=19 or 60<=f<=69 else 0 for f in range(84) for _ in range(100)))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'voice.wav'
            with wave.open(str(path),'wb') as w:
                w.setparams((1,2,3000,0,'NONE','not compressed'));w.writeframes(data.tobytes())
            result=tighten(plan,transcript,path)
            self.assertLess(result['duration_frames'],84)
            self.assertEqual(len(result['segments']),2)
            for word in words:
                self.assertTrue(any(round(s['in_seconds']*30)<=word['start_frame'] and round(s['out_seconds']*30)>word['end_frame'] for s in result['segments']))
            self.assertEqual(plan['segments'][0]['out_seconds'],84/30)
            # Un reconocimiento largo protege incluso una región de energía baja.
            transcript['words']=[{'start_frame':10,'end_frame':69,'text':'continuous'}]
            protected=tighten(plan,transcript,path)
            self.assertTrue(all(g['in_frame']>69 or g['out_frame']<10 for g in protected['silence_analysis']['removed']))
