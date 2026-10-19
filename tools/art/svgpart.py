"""SVG part writer + rasteriser.

A *part* is a list of layers drawn bottom-to-top. Each layer is a dict:
    d        : SVG path data (U units)
    fill     : '#rrggbb' or None
    shade    : None | dict(color, dx, dy, k, blur)   soft cel shadow, clipped to the shape
    light    : None | dict(color, dx, dy, k, blur)   soft highlight, clipped to the shape
    stroke   : '#rrggbb' or None
    sw       : stroke width (U)
    opacity  : float
    blur     : gaussian blur of the whole layer (for blush, soft shadows)
    clip     : path data to clip this layer to (e.g. a shadow inside a limb)
    cap/join : stroke caps/joins
The whole part is rendered on the view canvas, then cropped to its alpha bounding box.
"""
import os, re, json, subprocess, tempfile
import numpy as np
from PIL import Image

SCALE = 1.5          # raster pixels per U  (=6 px per reference px)
_uid = [0]


def _id(prefix):
    _uid[0] += 1
    return f'{prefix}{_uid[0]}'


def d_bbox(d):
    nums = list(map(float, re.findall(r'-?\d+\.?\d*', d)))
    xs, ys = nums[0::2], nums[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def _shade_group(d, spec, base, clip_id, kind):
    """Inside the clip: full colour `spec.color`, then a blurred base-coloured copy
    offset/scaled so only a soft band of `spec.color` remains at one side."""
    x0, y0, x1, y1 = d_bbox(d)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = spec.get('k', 1.0)
    kx = spec.get('kx', k); ky = spec.get('ky', k)
    dx, dy = spec.get('dx', -6), spec.get('dy', -6)
    blur = spec.get('blur', 4)
    fid = _id('f')
    tr = f'translate({cx+dx:.1f},{cy+dy:.1f}) scale({kx:.3f},{ky:.3f}) translate({-cx:.1f},{-cy:.1f})'
    op = spec.get('opacity', 1.0)
    s = [f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">'
         f'<feGaussianBlur stdDeviation="{blur}"/></filter>']
    if kind == 'shade':
        s.append(f'<g clip-path="url(#{clip_id})" opacity="{op}">'
                 f'<path d="{d}" fill="{spec["color"]}"/>'
                 f'<path d="{d}" fill="{base}" transform="{tr}" filter="url(#{fid})"/></g>')
    else:  # light: a blurred light-coloured copy, clipped
        s.append(f'<g clip-path="url(#{clip_id})" opacity="{op}">'
                 f'<path d="{d}" fill="{spec["color"]}" transform="{tr}" filter="url(#{fid})"/></g>')
    return ''.join(s)


def layer_svg(L):
    d = L['d']
    out = []
    op = L.get('opacity', 1.0)
    wrap_open, wrap_close = '', ''
    if L.get('clip'):
        cid = _id('c')
        out.append(f'<clipPath id="{cid}"><path d="{L["clip"]}" clip-rule="{L.get("clip_rule", "nonzero")}"/></clipPath>')
        wrap_open += f'<g clip-path="url(#{cid})">'
        wrap_close = '</g>' + wrap_close
    if L.get('blur'):
        fid = _id('f')
        out.append(f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">'
                   f'<feGaussianBlur stdDeviation="{L["blur"]}"/></filter>')
        wrap_open += f'<g filter="url(#{fid})">'
        wrap_close = '</g>' + wrap_close
    if op != 1.0:
        wrap_open += f'<g opacity="{op}">'
        wrap_close = '</g>' + wrap_close
    out.append(wrap_open)
    fill = L.get('fill')
    if fill:
        rule = L.get('rule', 'nonzero')
        out.append(f'<path d="{d}" fill="{fill}" fill-rule="{rule}"/>')
        if L.get('shade') or L.get('light') or L.get('extra'):
            cid = _id('c')
            out.append(f'<clipPath id="{cid}"><path d="{d}" clip-rule="{rule}"/></clipPath>')
            if L.get('shade'):
                specs = L['shade'] if isinstance(L['shade'], list) else [L['shade']]
                for sp in specs:
                    out.append(_shade_group(d, sp, fill, cid, 'shade'))
            if L.get('light'):
                specs = L['light'] if isinstance(L['light'], list) else [L['light']]
                for sp in specs:
                    out.append(_shade_group(d, sp, fill, cid, 'light'))
            for ex in L.get('extra', []):  # extra layers clipped to this shape
                out.append(f'<g clip-path="url(#{cid})">' + layer_svg(ex) + '</g>')
    if L.get('stroke'):
        cap = L.get('cap', 'round'); join = L.get('join', 'round')
        out.append(f'<path d="{d}" fill="none" stroke="{L["stroke"]}" stroke-width="{L.get("sw", 5)}" '
                   f'stroke-linecap="{cap}" stroke-linejoin="{join}"/>')
    out.append(wrap_close)
    return ''.join(out)


def part_svg(layers, w=720, h=1800, x0=0, y0=0):
    body = ''.join(layer_svg(L) for L in layers)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" '
            f'width="{w}" height="{h}">{body}</svg>')


def rasterise(svg_text, out_png, scale=SCALE, w=720, h=1800, crop=True, pad=4):
    """Render SVG with rsvg-convert; crop to alpha bbox. Returns bbox in U (x0,y0,x1,y1)."""
    with tempfile.NamedTemporaryFile('w', suffix='.svg', delete=False) as f:
        f.write(svg_text); tmp = f.name
    full = out_png + '.full.png'
    subprocess.run(['rsvg-convert', '-w', str(int(w * scale)), '-h', str(int(h * scale)),
                    '-o', full, tmp], check=True)
    os.unlink(tmp)
    im = Image.open(full)
    os.unlink(full)
    if not crop:
        im.save(out_png, optimize=True)
        return (0, 0, w, h)
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a > 0)
    if len(xs) == 0:
        im.crop((0, 0, 4, 4)).save(out_png)
        return (0, 0, 4 / scale, 4 / scale)
    px0 = max(xs.min() - pad, 0); py0 = max(ys.min() - pad, 0)
    px1 = min(xs.max() + pad + 1, im.width); py1 = min(ys.max() + pad + 1, im.height)
    im.crop((px0, py0, px1, py1)).save(out_png, optimize=True)
    return (px0 / scale, py0 / scale, px1 / scale, py1 / scale)


def split_line_backing(layers):
    """For parts drawn with an *outline backing*: layers flagged `outer=True` lose their
    stroke in the fill image; the line image is those shapes filled with the line colour and
    stroked at 2x width (only the outer half shows once the fills sit on top)."""
    fill_layers, line_layers = [], []
    for L in layers:
        if L.get('outer') and L.get('stroke'):
            F = dict(L); F.pop('stroke', None)
            fill_layers.append(F)
            line_layers.append(dict(d=L['d'], fill=L['stroke'], stroke=L['stroke'], sw=L.get('sw', 5) * 2,
                                    rule=L.get('rule', 'nonzero')))
        else:
            fill_layers.append(L)
    return fill_layers, line_layers


def write_part(name, layers, outdir, pivot, z=0.0, extra=None, svg_dir=None, w=720, h=1800,
               backing=False, line_z=None):
    """Write <outdir>/<name>.png (+ svg) and return metadata dict (list if backing)."""
    os.makedirs(outdir, exist_ok=True)
    sd = svg_dir or outdir
    os.makedirs(sd, exist_ok=True)
    out = []
    todo = [(name, layers, z)]
    if backing:
        fl, ll = split_line_backing(layers)
        todo = [(name, fl, z), (name + '__line', ll, line_z if line_z is not None else z - 0.5)]
    for nm, lay, zz in todo:
        svg = part_svg(lay, w, h)
        with open(os.path.join(sd, nm + '.svg'), 'w') as f:
            f.write(svg)
        bbox = rasterise(svg, os.path.join(outdir, nm + '.png'), w=w, h=h)
        meta = dict(name=nm, bbox=bbox, pivot=list(pivot), z=zz)
        if extra:
            meta.update(extra)
        if nm.endswith('__line'):
            meta['line_of'] = name
        out.append(meta)
    return out
