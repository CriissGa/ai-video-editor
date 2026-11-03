"""Validar y montar efectos WAV en pista dedicada conservando la voz editable."""
from pathlib import Path
import wave

from edit_video import frame, keys, number, require


def validate_audio(audio, plan_path, fps, duration):
    keys(audio, ['dialogue_gain_db', 'sounds'])
    require(number(audio['dialogue_gain_db']) and -12 <= audio['dialogue_gain_db'] <= 0, 'Ganancia de voz fuera de -12–0 dB')
    require(isinstance(audio['sounds'], list) and 0 < len(audio['sounds']) <= 40, 'Se requieren 1–40 sonidos')
    intervals = []
    for sound in audio['sounds']:
        keys(sound, ['source', 'in_seconds', 'out_seconds', 'at_seconds', 'gain_db', 'fade_in_frames', 'fade_out_frames'])
        require(isinstance(sound['source'], str) and bool(sound['source']), 'Ruta de sonido inválida')
        path = (plan_path.parent / sound['source']).resolve()
        require(path.is_file() and path.suffix.lower() == '.wav', 'Usar WAV preparado localmente')
        sound['source'] = str(path)
        try:
            with wave.open(str(path), 'rb') as source:
                require(source.getnchannels() == 2 and source.getsampwidth() == 2 and source.getframerate() == 48000, 'Sonidos deben ser PCM16 estéreo/48 kHz')
                source_duration = source.getnframes() / source.getframerate()
        except (wave.Error, EOFError) as exc:
            raise ValueError('WAV inválido') from exc
        a, b, at, gain = (sound[k] for k in ['in_seconds', 'out_seconds', 'at_seconds', 'gain_db'])
        require(all(number(v) for v in [a, b, at, gain]), 'Tiempos/ganancia de sonido inválidos')
        require(0 <= a < b <= source_duration and at >= 0 and -36 <= gain <= -6, 'Rango/ganancia de sonido fuera de límites')
        start, end, record = frame(a, fps), frame(b, fps), frame(at, fps)
        require(start < end and end <= int(source_duration * fps) and record + end - start <= duration, 'Sonido excede fuente o timeline')
        for key in ['fade_in_frames', 'fade_out_frames']:
            require(type(sound[key]) is int and 0 <= sound[key] <= fps, 'Fundido inválido')
        require(sound['fade_in_frames'] + sound['fade_out_frames'] <= end - start, 'Fundidos exceden clip')
        intervals.append((record, record + end - start))
    intervals.sort()
    require(all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:])), 'No superponer sonidos en la pista SFX')


def import_sounds(pool, audio, fps):
    imported = {}
    for sound in audio['sounds']:
        path = sound['source']
        if path not in imported:
            clips = pool.ImportMedia([path]) or []
            require(len(clips) == 1 and float(clips[0].GetClipProperty('FPS')) == fps, 'Importación/FPS de sonido incorrectos')
            imported[path] = clips[0]
    return imported


def apply_audio(project, timeline, audio, imported, fps):
    require(timeline.AddTrack('audio', 'stereo'), 'No se pudo crear pista SFX')
    track = timeline.GetTrackCount('audio')
    require(timeline.SetTrackName('audio', track, 'AI Editor - SFX'), 'No se pudo nombrar pista SFX')
    for item in timeline.GetItemListInTrack('audio', 1):
        require(item.SetProperties({'AudioVolume': audio['dialogue_gain_db']}), 'Ganancia de voz rechazada')
        require(abs(item.GetProperties()['AudioVolume'] - audio['dialogue_gain_db']) < 0.001, 'Ganancia de voz incorrecta')
    checks = []
    origin = timeline.GetStartFrame()
    pool = project.GetMediaPool()
    for sound in audio['sounds']:
        start, end, at = (frame(sound[k], fps) for k in ['in_seconds', 'out_seconds', 'at_seconds'])
        require(pool.AppendToTimeline([{'mediaPoolItem': imported[sound['source']], 'mediaType': 2,
             'startFrame': start, 'endFrame': end, 'trackIndex': track, 'recordFrame': origin + at}]), 'No se pudo montar sonido')
        item = sorted(timeline.GetItemListInTrack('audio', track), key=lambda i: i.GetStart())
        matched = [i for i in item if i.GetStart() == origin + at]
        require(len(matched) == 1, 'Posición de sonido incorrecta')
        item = matched[0]
        fades = {'FadeIn': sound['fade_in_frames'], 'FadeOut': sound['fade_out_frames']}
        require(item.SetProperties({'AudioVolume': sound['gain_db']}) and item.SetFades(fades), 'Ganancia/fundidos rechazados')
        require(item.GetDuration() == end - start and item.GetLeftOffset() == start, 'Recorte de sonido incorrecto')
        require(abs(item.GetProperties()['AudioVolume'] - sound['gain_db']) < 0.001 and item.GetFades() == fades, 'Ganancia/fundidos incorrectos')
        checks.append({'at_frame': at, 'duration_frames': end - start, 'gain_db': sound['gain_db'], 'fades': fades})
    require(len(timeline.GetItemListInTrack('audio', track)) == len(audio['sounds']), 'Cantidad SFX incorrecta')
    return {'track': track, 'dialogue_gain_db': audio['dialogue_gain_db'], 'clips': checks}
