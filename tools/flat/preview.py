"""Build a flat-style view and composite a preview with default swaps.
python -m tools.flat.preview kanha_front out.png [hand_default]"""
import sys, importlib
from tools.art.common import compose
modname = sys.argv[1]
mod = importlib.import_module(f'tools.flat.{modname}')
metas = mod.build()
hand_default = sys.argv[3] if len(sys.argv) > 3 else 'side_relaxed'
byname = {m['name']: m for m in metas}
show = []
for m in metas:
    base = byname[m['line_of']] if m.get('line_of') else m
    sw = base.get('swap')
    if sw is None:
        show.append(m); continue
    default = 'rest' if sw == 'mouth' else ('open' if sw.startswith('eye') else hand_default)
    if base.get('state') == default:
        show.append(m)
compose(show, mod.OUT, bg=(255, 255, 255, 255)).save(sys.argv[2])
print('ok', len(metas))
