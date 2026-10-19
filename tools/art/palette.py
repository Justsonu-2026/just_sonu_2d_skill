"""Colour model for Kanha, sampled from the reference with k-means (tools/segment_ref.py)
and tuned by eye against the reference. One base, one cel-shadow tone, one line colour
per material; highlights only on hair, eyes, jewellery."""

KANHA = dict(
    skin='#93a9d8', skin_sh='#7488c0', skin_sh2='#6577ae', skin_line='#4d5c94', hand_line='#2f3768', skin_hi='#aec0e6',
    blush='#c98fd0',
    hair='#262d48', hair_sh='#161a2c', hair_hi='#56658f', hair_line='#121524',
    dhoti='#fbad16', dhoti_sh='#e88d1a', dhoti_hi='#ffc94a', dhoti_line='#c0680c',
    sash='#ee6b14', sash_sh='#c9520c', sash_hi='#ff8a3a', sash_line='#9a3b06',
    gold='#eab43c', gold_sh='#bf8628', gold_hi='#fff0a8', gold_line='#8a5f1c',
    gem='#d8321f', gem_hi='#ff9a7a',
    eye_white='#f7f8fd', eye_white_sh='#c7cde6', iris='#6e4024', iris_dark='#2e1a0e', iris_light='#9c6638',
    pupil='#140d0a', lash='#1a1d33',
    lips='#d987a8', lips_line='#8f4a6e', mouth_in='#6e2238', tongue='#e0708a', teeth='#ffffff',
    brow='#222849',
    tilak='#fbfbff', tilak_line='#b5c2ea',
    feather_g='#3f6b1d', feather_g2='#6f9a2a', feather_g3='#2b4d14', feather_y='#f4b51c', feather_blue='#2c63a0',
    feather_teal='#5ab0bf', feather_dark='#1b2452', feather_line='#22380e',
)


def _mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def far_side(P, t=0.28, toward='#2a3060'):
    """Palette for limbs on the far side of the body: slightly darker/cooler so they read behind."""
    return {k: (_mix(v, toward, t) if isinstance(v, str) and v.startswith('#') else v) for k, v in P.items()}
