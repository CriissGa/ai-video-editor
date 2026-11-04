"""Cambiar intensidad/eventos de una timeline existente sin rehacer títulos o pistas."""
from edit_video import require, number
from edit_effects import apply_effects, validate_events, whip_blur_expression


def update_motion(project, plan, start_index=0, end_index=None):
    require(project.GetName()==plan['project'] and project.GetTimelineCount()==1,'Proyecto de revisión distinto')
    timeline=project.GetCurrentTimeline();fps=plan['timeline']['fps']
    items=timeline.GetItemListInTrack('video',1)
    require(len(items)==len(plan['segments']),'Planos distintos del plan')
    validate_events(plan['style']['events'],fps,plan['duration_frames'])
    for item,seg in zip(items,plan['segments']):
        require(item.GetDuration()==round(seg['out_seconds']*fps)-round(seg['in_seconds']*fps) and item.GetLeftOffset()==round(seg['in_seconds']*fps),'Tiempos de fuente distintos')
        require(all(number(v) and .95<=v<=1.30 for v in [seg['zoom'],seg['zoom_end']]),'Escala fuera de rango')
        require(len(seg['face'])==2 and all(number(v) and 0<=v<=1 for v in seg['face']),'Pivote inválido')
        comp=item.GetFusionCompByIndex(1)
        require(comp and comp.FindTool('AIEditor_Zoom') and comp.FindTool('AIEditor_Accents') and comp.FindTool('AIEditor_ZoomSize'),'Faltan nodos existentes')
    offset=0;checks=[]
    for index,(item,seg) in enumerate(zip(items,plan['segments'])):
        duration=int(item.GetDuration())
        if index<start_index or end_index is not None and index>=end_index:
            offset+=duration;continue
        comp=item.GetFusionCompByIndex(1);start=int(comp.GetAttrs()['COMPN_RenderStart']);end=start+duration-1
        zoom=comp.FindTool('AIEditor_Zoom');accent=comp.FindTool('AIEditor_Accents')
        pivot={1:seg['face'][0],2:seg['face'][1]}
        zoom.SetInput('Pivot',pivot);accent.SetInput('Pivot',pivot)
        comp.FindTool('AIEditor_ZoomSize').SetKeyFrames({start:{1:seg['zoom'],'Flags':{'Linear':True}},end:{1:seg['zoom_end'],'Flags':{'Linear':True}}},True)
        samples=apply_effects(accent,plan['style']['events'],fps,offset,duration,start,1.0)
        expression=whip_blur_expression(plan['style']['events'],fps,offset,duration,start)
        blur=comp.FindTool('AIEditor_WhipBlur')
        if expression!='0' and not blur:
            blur=comp.AddTool('Blur');blur.SetAttrs({'TOOLS_Name':'AIEditor_WhipBlur'})
        if blur:
            require(blur.ConnectInput('Input',accent),'No se pudo conectar blur')
            blur.SetInput('YBlurSize',0);blur.XBlurSize.SetExpression(expression)
        require(comp.FindToolByID('MediaOut').ConnectInput('Input',blur or accent),'Salida no conectada')
        values=[zoom.GetInput('Size',at) for at in [start,(start+end)//2,end]]
        require(abs(values[0]-seg['zoom'])<1e-5 and abs(values[-1]-seg['zoom_end'])<1e-5,'Keyframes no conservados')
        checks.append({'clip':index,'zoom':values,'events':samples,'transition':expression!='0'})
        offset+=duration
    return checks
