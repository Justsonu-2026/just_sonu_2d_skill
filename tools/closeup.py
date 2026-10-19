"""Side-by-side close-up of reference vs rebuild for a box in U coords.
python -m tools.closeup <preview.png> <view_cx> <x0,y0,x1,y1 in U> <out.png> [width]"""
import sys
from PIL import Image
a = Image.open(sys.argv[1]).convert('RGB')
cx = int(sys.argv[2]); x0, y0, x1, y1 = map(float, sys.argv[3].split(','))
ref = Image.open('assets/reference/character_ref.png').crop((cx-90, 555, cx+90, 1005)).resize(a.size, Image.LANCZOS)
sc = a.width / 720
box = tuple(int(v * sc) for v in (x0, y0, x1, y1))
A, R = a.crop(box), ref.crop(box)
w = Image.new('RGB', (A.width * 2 + 10, A.height), 'white'); w.paste(R, (0, 0)); w.paste(A, (A.width + 10, 0))
W = int(sys.argv[5]) if len(sys.argv) > 5 else 1200
w.resize((W, int(w.height * W / w.width)), Image.LANCZOS).save(sys.argv[4])
