import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from timeline_titles import place_titles


class NativeTitlesTest(unittest.TestCase):
    def test_preserves_native_tracks_and_bus_data(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder)
            base='''<!--21.1.2.0010--><Root><VideoTrackVec><Element><Sm2TiTrack DbId="v1"><Items><Element><Sm2TiVideoClip><Start>108000</Start></Sm2TiVideoClip></Element></Items></Sm2TiTrack></Element><Element><Sm2TiTrack DbId="v2"><Items/></Sm2TiTrack></Element></VideoTrackVec><AudioTrackVec><Element id="a1"/><Element id="a2"/></AudioTrackVec></Root>'''
            seed='''<Root><VideoTrackVec><Element><Sm2TiTrack><Items><Element><Sm2TiVideoClip DbId="seed"><PrettyType>Fusion Title</PrettyType><Start>0</Start><Duration>150</Duration><In/></Sm2TiVideoClip></Element></Items></Sm2TiTrack></Element></VideoTrackVec></Root>'''
            for name,data in [('base',base),('seed',seed)]:
                with zipfile.ZipFile(folder/(name+'.drt'),'w') as z:
                    z.writestr('SeqContainer/sequence.xml',data)
                    z.writestr('project.xml','opaque native bus configuration')
            captions=[{'in_seconds':0,'out_seconds':1},{'in_seconds':1.5,'out_seconds':2}]
            place_titles(folder/'base.drt',folder/'seed.drt',folder/'out.drt',captions)
            with zipfile.ZipFile(folder/'out.drt') as z:
                root=ET.fromstring(z.read('SeqContainer/sequence.xml'))
                self.assertEqual(z.read('project.xml'),b'opaque native bus configuration')
            self.assertEqual(root.find('VideoTrackVec')[1].find('Sm2TiTrack').get('DbId'),'v2')
            clips=root.find('VideoTrackVec')[1].findall('Sm2TiTrack/Items/Element/Sm2TiVideoClip')
            self.assertEqual([c.findtext('Start') for c in clips],['108000','108045'])
            self.assertEqual([c.findtext('Duration') for c in clips],['30','15'])
            self.assertEqual(len({c.get('DbId') for c in clips}),2)
            self.assertEqual(root.find('AudioTrackVec')[1].get('id'),'a2')
            with self.assertRaises(ValueError):
                place_titles(folder/'base.drt',folder/'seed.drt',folder/'bad.drt',captions[::-1])
