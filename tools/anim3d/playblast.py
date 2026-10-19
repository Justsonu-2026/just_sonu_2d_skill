"""Fast review renders: Workbench (solid, material colours) contact sheets and MP4 playblasts."""
import os, subprocess
import bpy


def workbench(scene, res=(960, 540), samples=4):
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'MATERIAL'
    sh.show_cavity = True
    sh.cavity_type = 'WORLD'
    sh.show_shadows = True
    scene.display.render_aa = '8' if samples >= 8 else '5'
    scene.view_settings.view_transform = 'Standard'
    _png(scene)


def _png(scene):
    try:
        scene.render.image_settings.media_type = 'IMAGE'
    except Exception:
        pass
    scene.render.image_settings.file_format = 'PNG'


def render_frames(scene, frames, outdir, prefix='f'):
    os.makedirs(outdir, exist_ok=True)
    _png(scene)
    paths = []
    for f in frames:
        scene.frame_set(f)
        p = os.path.join(outdir, f'{prefix}{f:04d}.png')
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    return paths


def contact_sheet(paths, out, cols=4, width=1920, labels=True):
    from PIL import Image, ImageDraw
    ims = [Image.open(p).convert('RGB') for p in paths]
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (w * cols, h * rows), 'white')
    d = ImageDraw.Draw(sheet)
    for i, (p, im) in enumerate(zip(paths, ims)):
        x, y = (i % cols) * w, (i // cols) * h
        sheet.paste(im, (x, y))
        if labels:
            d.rectangle([x, y, x + 120, y + 26], fill='black')
            d.text((x + 6, y + 6), os.path.basename(p).split('.')[0], fill='white')
    sc = width / sheet.width
    sheet.resize((width, int(sheet.height * sc))).save(out)
    return out


def encode(pattern, out, fps=24, crf=18):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', pattern,
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-movflags', '+faststart', out], check=True)
    return out
