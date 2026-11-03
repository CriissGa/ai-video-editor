"""Animación cinética de texto con límites de tamaño para palabras largas."""
from edit_video import require


def fitted_size(text, preset, emphasis):
    size = preset.get('emphasis_size',preset['size']) if emphasis else preset['size']
    if preset.get('kinetic'):
        width = max((len(line) for line in text.splitlines()), default=1)
        limit = 12 if emphasis else 16
        size *= min(1.0,limit/max(1,width))
    return size


def kinetic_expressions(begin, end, size, variant=0):
    require(begin < end and size > 0, 'Animación de texto inválida')
    require(variant in (0,1,2), 'Variante desconocida')
    elapsed = '(time-%d)' % begin
    scale = '(0.78+0.22*min(1,max(0,(%s+1)/2))+0.12*sin(min(1,max(0,%s/6))*3.14159265))' % (elapsed,elapsed)
    if variant == 1:
        return '%.9f*(0.92+0.08*min(1,max(0,(%s+1)/5)))' % (size,elapsed), 'Point(0.5,0.24-0.035*(1-min(1,max(0,(%s+1)/5))))' % elapsed
    if variant == 2:
        return '%.9f*(1.10-0.10*min(1,max(0,(%s+1)/5)))' % (size,elapsed), 'Point(0.5+0.025*(1-min(1,max(0,(%s+1)/5))),0.24)' % elapsed
    return '%.9f*%s' % (size,scale), 'Point(0.5,0.24-0.025*(1-min(1,max(0,(%s+1)/4))))' % elapsed
