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


def emphasis_expressions(begin, end, size, variant):
    """Entradas más marcadas, con recuperación rápida para no tapar el remate."""
    require(begin < end and size > 0 and variant in (0,1,2,3,4), 'Énfasis inválido')
    t='min(1,max(0,(time-%d)/6))' % begin
    if variant == 0:
        return '%.9f*(0.65+0.35*%s+0.22*sin(%s*3.14159265))' % (size,t,t), 'Point(0.5,0.24)'
    if variant == 1:
        return '%.9f*(1.12-0.12*%s)' % (size,t), 'Point(0.5+0.06*(1-%s)*(1-%s),0.24)' % (t,t)
    if variant == 3:
        return '%.9f*(0.80+0.20*%s+0.16*sin(%s*3.14159265))' % (size,t,t), 'Point(0.5+0.025*sin(%s*6.2831853)*(1-%s),0.24)' % (t,t)
    if variant == 4:
        return '%.9f*(1.14-0.14*%s)' % (size,t), 'Point(0.5,0.24+0.05*sin(%s*3.14159265)*(1-%s))' % (t,t)
    return '%.9f*(0.78+0.22*%s+0.12*sin(%s*3.14159265))' % (size,t,t), 'Point(0.5,0.24+0.05*(1-%s)*(1-%s))' % (t,t)
