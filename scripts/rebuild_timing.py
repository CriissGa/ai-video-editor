"""Actualizar tiempos de un DRT propio conservando pistas/buses y medios nativos."""
import copy
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from edit_video import require
from timeline_titles import fresh_ids


def rebuild(base_path, output_path, plan):
    require(not Path(output_path).exists(), 'No sobrescribir DRT existente')
    with zipfile.ZipFile(base_path) as z:
        name=next(n for n in z.namelist() if n.startswith('SeqContainer/'))
        require('21.1.2.0010' in z.read(name).decode(),'Versión no probada')
        root=ET.fromstring(z.read(name))
        video=root.find('VideoTrackVec');audio=root.find('AudioTrackVec')
        require(len(video)==len(audio)==2,'Conservar dos pistas nativas por tipo')
        vitems=video[0].find('Sm2TiTrack/Items');aitems=audio[0].find('Sm2TiTrack/Items')
        footage=next(copy.deepcopy(e) for e in vitems if e.find('Sm2TiVideoClip/CompositionTable') is None)
        voice=copy.deepcopy(aitems[0])
        origin=int(vitems[0].findtext('Sm2TiVideoClip/Start'));fps=plan['timeline']['fps']
        def timed(template,tag,start,duration,source_in):
            e=copy.deepcopy(template);fresh_ids(e);c=e.find(tag)
            for key,value in [('Start',start),('Duration',duration),('In',source_in)]:c.find(key).text=str(value)
            if c.find('LinkedItemSync') is not None:c.find('LinkedItemSync').clear()
            return e
        vitems.clear();aitems.clear();offset=0
        for segment in plan['segments']:
            start=round(segment['in_seconds']*fps);end=round(segment['out_seconds']*fps)
            require(0<=start<end<=plan['source_frames'],'Rango de fuente inválido')
            vitems.append(timed(footage,'Sm2TiVideoClip',origin+offset,end-start,start))
            aitems.append(timed(voice,'Sm2TiAudioClip',origin+offset,end-start,start))
            offset+=end-start
        require(offset==plan['duration_frames'],'Duración distinta del plan')
        titles=video[1].find('Sm2TiTrack/Items');template=copy.deepcopy(titles[0]);titles.clear()
        previous=0
        for caption in plan['captions']:
            a=round(caption['in_seconds']*fps);b=round(caption['out_seconds']*fps)
            require(previous<=a<b<=offset,'Título fuera de rango o superpuesto')
            titles.append(timed(template,'Sm2TiVideoClip',origin+a,b-a,0));previous=b
        sounds=audio[1].find('Sm2TiTrack/Items');templates=list(sounds)
        require(len(templates)==len(plan['audio']['sounds']),'SFX distintos del respaldo')
        sounds.clear()
        for template,sound in zip(templates,plan['audio']['sounds']):
            a=round(sound['in_seconds']*fps);b=round(sound['out_seconds']*fps);at=round(sound['at_seconds']*fps)
            require(0<=at<at+b-a<=offset,'SFX fuera de rango')
            sounds.append(timed(template,'Sm2TiAudioClip',origin+at,b-a,a))
        with zipfile.ZipFile(output_path,'w',zipfile.ZIP_DEFLATED) as out:
            for n in z.namelist():out.writestr(n,ET.tostring(root,encoding='utf-8',xml_declaration=True) if n==name else z.read(n))
