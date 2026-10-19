"""Build a view's parts and write a composite preview + overlay against the reference guide.
python -m tools.preview_view front"""
import sys, json, importlib
from PIL import Image
from tools.art.common import compose
view = sys.argv[1]
mod = importlib.import_module(f'tools.art.boy_{view}')
metas = mod.build()
# default swap states visible
show = []
for m in metas:
    if m['name'].endswith('__line'):
        base = next(x for x in metas if x['name'] == m['line_of'])
        sw = base.get('swap')
        if sw is None: show.append(m); continue
        default = {'mouth': 'rest'}.get(sw, 'open' if sw.startswith('eye') else 'side_relaxed')
        if base.get('state') == default: show.append(m)
        continue
    sw = m.get('swap')
    if sw is None: show.append(m); continue
    default = {'mouth': 'rest'}.get(sw, 'open' if sw.startswith('eye') else 'side_relaxed')
    if m.get('state') == default: show.append(m)
im = compose(show, mod.OUT)
out = sys.argv[2] if len(sys.argv) > 2 else f'build/{view}_preview.png'
im.save(out)
print('wrote', out, len(metas), 'parts')
