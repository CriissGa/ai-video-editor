"""Recorte conservador de silencios: PCM local + protección de palabras."""
import array
import copy
import math
import wave
from edit_video import require


def tighten(plan, transcript, wav_path, threshold_db=-38, minimum_gap=10, handles=2):
    require(math.isfinite(threshold_db) and -70<=threshold_db<=-20 and minimum_gap>2*handles>=0, 'Parámetros de silencio inválidos')
    fps=plan['timeline']['fps']
    with wave.open(str(wav_path)) as w:
        require(w.getnchannels()==1 and w.getsampwidth()==2,'Se requiere PCM16 mono')
        rate=w.getframerate();samples=array.array('h',w.readframes(w.getnframes()))
    require(rate%fps==0,'FPS incompatible con muestras')
    step=rate//fps
    levels=[]
    for i in range(0,len(samples),step):
        block=samples[i:i+step]
        levels.append(20*math.log10(max(1,math.sqrt(sum(v*v for v in block)/len(block)))/32768))
    protected=set()
    for word in transcript['words']:
        protected.update(range(max(0,word['start_frame']-2),word['end_frame']+3))
    output=copy.deepcopy(plan);pieces=[];removed=[]
    for index,seg in enumerate(plan['segments']):
        a=round(seg['in_seconds']*fps);b=round(seg['out_seconds']*fps)
        require(0<=a<b<=len(levels),'Segmento fuera del PCM')
        quiet=[];start=None
        for frame in range(a,b+1):
            silent=frame<b and levels[frame]<threshold_db and frame not in protected
            if silent and start is None:start=frame
            if not silent and start is not None:
                if frame-start>=minimum_gap:
                    left=start+handles if start>a else a;right=frame-handles if frame<b else b
                    if left<right:quiet.append((left,right))
                start=None
        cursor=a
        for left,right in quiet:
            if 0 < left-cursor < 12 or 0 < b-right < 12:continue
            if left>cursor:
                pieces.append(dict(seg,in_seconds=cursor/fps,out_seconds=left/fps,parent_segment=index))
            removed.append({'in_frame':left,'out_frame':right,'parent_segment':index})
            cursor=right
        if cursor<b:
            pieces.append(dict(seg,in_seconds=cursor/fps,out_seconds=b/fps,parent_segment=index))
    require(bool(pieces), 'No queda contenido tras recortar silencios')
    output['segments']=pieces
    output['source_frames']=transcript['source_frames']
    output['duration_frames']=sum(round(s['out_seconds']*fps)-round(s['in_seconds']*fps) for s in pieces)
    output['silence_analysis']={'threshold_db':threshold_db,'minimum_gap_frames':minimum_gap,'handles_frames':handles,'removed':removed}
    return output
