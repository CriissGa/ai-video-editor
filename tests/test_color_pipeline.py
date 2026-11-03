from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from color_pipeline import SETTINGS, apply_color_settings, apply_graphics_luminance


class ColorTests(unittest.TestCase):
    def test_reject_silently_ignored_color_setting(self):
        class Project:
            def SetSettings(self,values):return True
            def GetSettings(self):return dict(SETTINGS,colorSpaceOutput='Rec.2100 HLG')
        with self.assertRaises(ValueError):apply_color_settings(Project(),{'preset':'iphone-hlg-to-sdr-v1'})

    def test_graphics_only_compensation_and_text_identity(self):
        class Text:
            inputs={'StyledText':'TEST','Red1':1,'Green1':1,'Blue1':1}
            def GetAttrs(self):return {'TOOLS_Name':'Caption_001'}
            def GetInput(self,key):return self.inputs[key]
            def SetInput(self,key,value):self.inputs[key]=value
        text=Text()
        class Comp:
            def GetToolList(self,*args):return {1:text}
        class Item:
            def GetDuration(self):return 30
            def GetFusionCompByIndex(self,index):return Comp()
        class Timeline:
            def GetItemListInTrack(self,*args):return [Item()]
        plan={'timeline':{'fps':30},'captions':[{'in_seconds':0,'out_seconds':1,'text':'TEST','emphasis':False}]}
        result=apply_graphics_luminance(Timeline(),plan)
        self.assertEqual(result['text_nodes'],1)
        self.assertEqual(text.inputs['Red1'],4)
        self.assertEqual(text.inputs['Green1'],4)
        plan['captions'][0]['text']='DIFFERENT'
        with self.assertRaises(ValueError):apply_graphics_luminance(Timeline(),plan)


if __name__=='__main__':unittest.main()
