"""Guide-layer analysis of the reference: classify every pixel of a figure crop into
material classes (skin, hair, dhoti, sash, gold, ...) so we can trace shapes as a guide.
Usage: python tools/segment_ref.py <x0> <y0> <x1> <y1> <out_prefix> [scale]
"""
import sys, numpy as np, cv2
from PIL import Image

REF = 'assets/reference/character_ref.png'
# class name -> representative colours sampled with k-means from the reference
CLASSES = {
    'bg':      ['#fdfdfd', '#e6e8e1', '#d1d1bf'],
    'ground':  ['#babb95', '#b7c092'],
    'skin':    ['#90a7d3', '#9fb3dc', '#a8bce2'],
    'skin_sh': ['#7183a7', '#7c8fc0'],
    'hair':    ['#212639', '#161925', '#2a3150', '#384160'],
    'dhoti':   ['#fbac13', '#e89422', '#f4b232'],
    'sash':    ['#eb6712', '#bc4f0a', '#f07a20'],
    'gold':    ['#cba65c', '#927851', '#e0b040'],
    'green':   ['#3f5b1a', '#6b8a24'],
}

def hex2rgb(h):
    h = h.lstrip('#'); return [int(h[i:i+2], 16) for i in (0, 2, 4)]

def classify(rgb):
    names, cols = [], []
    for k, v in CLASSES.items():
        for h in v:
            names.append(k); cols.append(hex2rgb(h))
    cols = np.array(cols, np.float32)
    lab_img = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    lab_c = cv2.cvtColor(cols[None].astype(np.uint8), cv2.COLOR_RGB2LAB)[0].astype(np.float32)
    d = ((lab_img[:, :, None, :] - lab_c[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    uniq = list(dict.fromkeys(names))
    return np.vectorize(lambda i: uniq.index(names[i]))(idx), uniq

if __name__ == '__main__':
    x0, y0, x1, y1 = map(int, sys.argv[1:5]); out = sys.argv[5]
    sc = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    im = Image.open(REF).convert('RGB').crop((x0, y0, x1, y1))
    im = im.resize((im.width * sc, im.height * sc), Image.LANCZOS)
    rgb = np.array(im)
    lab, names = classify(rgb)
    pal = np.array([hex2rgb(CLASSES[n][0]) for n in names], np.uint8)
    Image.fromarray(pal[lab]).save(out + '_classes.png')
    np.save(out + '_classes.npy', lab.astype(np.uint8))
    print(names)
