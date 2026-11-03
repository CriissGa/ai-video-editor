"""Conversión HLG a SDR mediante Resolve Color Management; sin LUT horneada."""
from edit_video import keys, require

PRESET = 'iphone-hlg-to-sdr-v1'
GRAPHICS_SCALE = 4.0  # Compensación comprobada de gráficos Fusion en este perfil RCM.
SETTINGS = {'colorScienceMode':'davinciYRGBColorManagedv2', 'isAutoColorManage':'0',
            'rcmPresetMode':'Custom', 'separateColorSpaceAndGamma':'0',
            'colorSpaceInput':'Rec.2100 HLG', 'colorSpaceTimeline':'DaVinci WG/Intermediate',
            'colorSpaceOutput':'Rec.709 Gamma 2.4', 'colorSpaceOutputToneMapping':'DaVinci',
            'outputDRT':'DaVinci', 'inputDRT':'None', 'graphicsWhiteLevel':'100', 'colorSpaceOutputToneLuminanceMax':'100'}


SOFT_PRESET = 'iphone-hlg-sdr-soft-v2'
SOFT_SETTINGS = dict(SETTINGS, colorSpaceTimeline='Rec.709 Gamma 2.4',
                     timelineWorkingLuminanceMode='SDR 100', timelineWorkingLuminance='100',
                     inputDRT='DaVinci', outputDRT='None', colorSpaceOutputToneMapping='None')
PROFILES = {PRESET: SETTINGS, SOFT_PRESET: SOFT_SETTINGS}
CAMERA_SOFT = {'Saturation1':0.90,'MasterRGBContrast':1.01,'MasterRGBGain':0.98,'MasterRGBGamma':0.995}


def graphics_scale_for(color):
    return 1.0 if color.get('preset') == SOFT_PRESET else GRAPHICS_SCALE


def camera_adjustments(color):
    return CAMERA_SOFT.copy() if color.get('preset') == SOFT_PRESET else {}


def validate_color(color):
    keys(color, ['preset'])
    require(color['preset'] in PROFILES, 'Preset de color desconocido')


def apply_color_settings(project, color):
    validate_color(color)
    settings = PROFILES[color['preset']]
    for key, value in settings.items():
        require(project.SetSettings({key:value}), 'Ajuste de color rechazado: ' + key)
    actual = project.GetSettings()
    for key, value in settings.items():
        require(str(actual[key]) == value, 'Ajuste de color no conservado: ' + key)
    return {'preset':color['preset'], 'settings':{key:actual[key] for key in settings}}


def verify_hlg_sources(media):
    result = {}
    for name, clip in media.items():
        props = clip.GetClipProperty()
        require(props.get('Input Color Space') == 'Rec.2100 HLG', 'Fuente no identificada como HLG: ' + name)
        require(clip.SetClipProperty('Input Color Space','Rec.2100 HLG'), 'No se pudo fijar entrada HLG')
        result[name] = {k:clip.GetClipProperty(k) for k in ['Input Color Space','Input Gamma','Resolution','FPS']}
    return result


def apply_graphics_luminance(timeline, plan):
    """Mantener legible la paleta Text+ bajo el perfil RCM; no modificar MediaIn."""
    from caption_style import caption_intersections
    scale = graphics_scale_for(plan.get('color',{'preset':PRESET}))
    offset = 0
    count = 0
    for item in timeline.GetItemListInTrack('video',1):
        captions = caption_intersections(plan['captions'],plan['timeline']['fps'],offset,int(item.GetDuration()))
        comp = item.GetFusionCompByIndex(1)
        texts = sorted(comp.GetToolList(False,'TextPlus').values(), key=lambda t:t.GetAttrs()['TOOLS_Name'])
        require(len(texts)==len(captions), 'Textos y plan no coinciden')
        for text,(caption,_,_) in zip(texts,captions):
            require(text.GetInput('StyledText')==caption['text'], 'Texto distinto al plan')
            values = {'Red1':scale, 'Green1':scale*(0.85 if caption['emphasis'] else 1),
                      'Blue1':scale*(0.12 if caption['emphasis'] else 1)}
            for key,value in values.items():
                text.SetInput(key,value)
                require(abs(text.GetInput(key)-value)<0.00001, 'Luminancia gráfica no aplicada')
            count += 1
        offset += int(item.GetDuration())
    return {'text_nodes':count,'graphics_scale':scale}
