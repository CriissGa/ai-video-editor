"""Revisar una timeline propia existente sin crear proyectos, pistas ni renders."""
from edit_video import require
from caption_animation import kinetic_expressions


def revise(project, face=(0.43, 0.60), end_zoom=1.10):
    require(1 <= end_zoom <= 1.15, 'Zoom conservador fuera de rango')
    require(all(0.25 <= v <= 0.75 for v in face), 'Centro facial fuera de rango')
    timeline = project.GetCurrentTimeline()
    require(project.GetTimelineCount() == 1, 'Se requiere una timeline única')
    items = timeline.GetItemListInTrack('video', 1)
    comps = [item.GetFusionCompByIndex(1) for item in items]
    require(all(c and c.FindTool('AIEditor_Zoom') for c in comps), 'Composiciones incompatibles')
    report = []
    caption_number = 0
    for item, comp in zip(items, comps):
        start = int(comp.GetAttrs()['COMPN_RenderStart'])
        end = start + int(item.GetDuration()) - 1
        zoom = comp.FindTool('AIEditor_Zoom')
        # Pivot fijo en el rostro: al crecer Size ese punto no se desplaza.
        zoom.SetInput('Pivot', {1:face[0], 2:face[1]})
        zoom.SetInput('Center', {1:0.5, 2:0.5})
        zoom.Size.SetExpression(None)
        if not comp.FindTool('AIEditor_ZoomSize'):
            require(zoom.AddModifier('Size','BezierSpline'), 'No se pudo crear spline')
        zoom.SetInput('Size', 1.0, start)
        zoom.SetInput('Size', end_zoom, end)
        spline = comp.FindTool('AIEditor_ZoomSize')
        require(spline is not None, 'Falta spline de zoom')
        span = end-start
        spline.SetKeyFrames({start:{1:1.0,'Flags':{'Linear':True}},end:{1:end_zoom,'Flags':{'Linear':True}}}, True)
        accent = comp.FindTool('AIEditor_Accents')
        if accent:
            # Mantener el rostro estable: retirar desplazamientos/zooms bruscos.
            for key,value in [('Size',1.0),('Center',{1:0.5,2:0.5}),('Angle',0.0)]:
                getattr(accent,key).SetExpression(None)
                accent.SetInput(key,value)
        for tool in comp.GetToolList(False,'TextPlus').values():
            expr = tool.Size.GetExpression()
            if not expr:
                continue
            size = float(expr.split('*',1)[0])
            gate = comp.FindTool(tool.GetAttrs()['TOOLS_Name'].replace('Caption_','CaptionGate_'))
            import re
            bounds = re.findall(r'time\s*[<>]=?\s*(\d+)',gate.Blend.GetExpression())
            require(len(bounds)==2,'No se pudo recuperar tiempo del texto')
            begin,finish = map(int,bounds)
            variant = caption_number % 3
            a,b = kinetic_expressions(begin,finish,size,variant)
            tool.Size.SetExpression(a)
            tool.Center.SetExpression(b)
            caption_number += 1
        values = [zoom.GetInput('Size',at) for at in [start,(start+end)//2,end]]
        require(abs(values[0]-1)<0.0001 and abs(values[-1]-end_zoom)<0.0001 and 1 <= values[1] <= end_zoom,'Zoom no verificado')
        report.append({'start':start,'end':end,'zoom':values,'face':face})
    return {'clips':report,'captions':caption_number,'rendered':False,'face_tracking':False}


def revise_from_plan(project, plan):
    """Entrada persistida, cargada por MCP; no exporta ni cambia de proyecto."""
    require(set(plan) == {'project','face','end_zoom','caption_variants','render'}, 'Plan de revisión inválido')
    require(project.GetName() == plan['project'], 'Proyecto distinto del autorizado')
    require(plan['render'] is False and plan['caption_variants'] == [0,1,2], 'Opciones no soportadas')
    return revise(project, tuple(plan['face']), plan['end_zoom'])
