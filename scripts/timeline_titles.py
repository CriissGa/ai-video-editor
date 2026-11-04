"""Pista de títulos nativos desde semilla DRT de Resolve 21.1.2.

Adaptador específico de versión: conserva blobs nativos sin interpretarlos.
Nunca edita la biblioteca; escribe un DRT nuevo para importación verificada.
"""
import copy
import uuid
import zipfile
import xml.etree.ElementTree as ET
from edit_video import require


def fresh_ids(element):
    for node in element.iter():
        if 'DbId' in node.attrib:
            node.set('DbId', str(uuid.uuid4()))


def place_titles(native_path, seed_path, output_path, captions, fps=30):
    """Reemplaza clips de V2 conservando el registro nativo de pistas y buses.

    Exige una base importada por Resolve con V1/V2 y A1/A2 reales. No crear
    pistas copiando nodos XML: pueden aparecer sin componer ni salir al bus.
    """
    with zipfile.ZipFile(native_path) as base, zipfile.ZipFile(seed_path) as seed:
        bn=[n for n in base.namelist() if n.startswith('SeqContainer/')]
        sn=[n for n in seed.namelist() if n.startswith('SeqContainer/')]
        require(len(bn)==len(sn)==1, 'DRT debe contener una secuencia')
        require('21.1.2.0010' in base.read(bn[0]).decode(), 'Versión DRT no probada')
        root=ET.fromstring(base.read(bn[0]))
        require(len(root.find('VideoTrackVec'))==2 and len(root.find('AudioTrackVec'))==2,
                'Preparar dos pistas nativas por tipo antes de Fusion')
        title=ET.fromstring(seed.read(sn[0])).find('VideoTrackVec/Element/Sm2TiTrack/Items/Element')
        require(title is not None and title.findtext('Sm2TiVideoClip/PrettyType')=='Fusion Title',
                'Falta semilla Text+ nativa')
        origin=int(root.findtext('VideoTrackVec/Element/Sm2TiTrack/Items/Element/Sm2TiVideoClip/Start'))
        items=root.find('VideoTrackVec')[1].find('Sm2TiTrack/Items')
        items.clear()
        previous=0
        for caption in captions:
            start=round(caption['in_seconds']*fps);end=round(caption['out_seconds']*fps)
            require(previous <= start < end, 'Títulos superpuestos o inválidos')
            previous=end
            node=copy.deepcopy(title);fresh_ids(node)
            clip=node.find('Sm2TiVideoClip')
            clip.find('Start').text=str(origin+start)
            clip.find('Duration').text=str(end-start)
            clip.find('In').text='0'
            items.append(node)
        with zipfile.ZipFile(output_path,'w',zipfile.ZIP_DEFLATED) as out:
            for n in base.namelist():
                out.writestr(n,ET.tostring(root,encoding='utf-8',xml_declaration=True) if n==bn[0] else base.read(n))


def style_titles(timeline, plan):
    """Configura Text+ nativos: texto accesible en Inspector y animación por clip."""
    from caption_style import PRESETS
    from caption_animation import fitted_size, kinetic_expressions
    preset=PRESETS[plan['style']['preset']]
    titles=timeline.GetItemListInTrack('video',2)
    require(len(titles)==len(plan['captions']), 'Cantidad de títulos distinta del plan')
    origin=timeline.GetStartFrame(); fps=plan['timeline']['fps']
    for item,caption in zip(titles,plan['captions']):
        require(item.GetStart()==origin+round(caption['in_seconds']*fps) and item.GetDuration()==round(caption['out_seconds']*fps)-round(caption['in_seconds']*fps), 'Tiempo de título incorrecto')
        require(item.GetFusionCompCount()==1, 'Título sin composición')
    checks=[]
    emphasis_index=0
    for index,(item,caption) in enumerate(zip(titles,plan['captions'])):
        comp=item.GetFusionCompByIndex(1)
        text=comp.FindTool('Template')
        require(text and text.GetAttrs()['TOOLS_RegID']=='TextPlus', 'Falta Text+ nativo')
        size=fitted_size(caption['text'],preset,caption['emphasis'])
        settings={'StyledText':caption['text'],'Font':'Arial','Style':'Bold','Size':size,
                  'Center':{1:.5,2:.24},'Red1':1,'Green1':.85 if caption['emphasis'] else 1,
                  'Blue1':.12 if caption['emphasis'] else 1,'Enabled2':1,'SelectElement':1,
                  'ElementShape2':1,'Thickness2':.08,'Red2':0,'Green2':0,'Blue2':0,'Alpha2':1,
                  'Enabled3':1,'ElementShape3':0,'Red3':0,'Green3':0,'Blue3':0,'Alpha3':.5,
                  'Offset3':{1:.025,2:-.025},'SoftnessX3':.012,'SoftnessY3':.012}
        for key,value in settings.items():text.SetInput(key,value)
        begin=int(comp.GetAttrs()['COMPN_RenderStart']);end=begin+int(item.GetDuration())
        variant=(index%3) if caption['emphasis'] else ((index//4)%3)
        if caption['emphasis'] and 'caption_emphasis' in plan:
            from caption_animation import emphasis_expressions
            size=min(plan['caption_emphasis']['size'],1.66/max(len(line) for line in caption['text'].splitlines()))
            variant=caption.get('emphasis_variant',emphasis_index%3);emphasis_index+=1
            a,b=emphasis_expressions(begin,end,size,variant)
            text.SetInput('Thickness2',plan['caption_emphasis']['outline'])
            if variant == 2:
                text.SetInput('Green1',1.0);text.SetInput('Blue1',1.0);text.SetInput('Red1',0.25)
            elif variant == 3:
                text.SetInput('Red1',1.0);text.SetInput('Green1',0.45);text.SetInput('Blue1',0.70)
        else:
            a,b=kinetic_expressions(begin,end,size,variant)
        text.Size.SetExpression(a);text.Center.SetExpression(b)
        item.SetName(caption['text'].replace('\n',' '))
        require(text.GetInput('StyledText')==caption['text'], 'Texto no conservado')
        checks.append({'start':item.GetStart()-origin,'duration':item.GetDuration(),'variant':variant,'emphasis':caption['emphasis']})
    return checks
