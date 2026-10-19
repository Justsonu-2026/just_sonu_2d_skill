"""Style-match review image: reference crop | rebuild | 50% overlay.
python -m tools.style_match <preview.png> <view_center_x> <out.png>"""
import sys
from PIL import Image
prev = Image.open(sys.argv[1]).convert('RGBA')
cx = int(sys.argv[2])
ref = Image.open('assets/reference/character_ref.png').convert('RGBA').crop((cx-90, 555, cx+90, 1005))
ref = ref.resize(prev.size, Image.LANCZOS)
bg = Image.new('RGBA', prev.size, (255, 255, 255, 255))
reb = Image.alpha_composite(bg, prev)
ov = Image.blend(ref, reb, 0.5)
W, H = prev.size
sheet = Image.new('RGB', (W * 3, H), 'white')
for i, im in enumerate((ref, reb, ov)):
    sheet.paste(im.convert('RGB'), (W * i, 0))
sc = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
sheet = sheet.resize((int(sheet.width * sc), int(sheet.height * sc)), Image.LANCZOS)
sheet.save(sys.argv[3])
