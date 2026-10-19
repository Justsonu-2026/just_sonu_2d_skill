"""Flat-style colour model for Kanha (v2 design). One base, one hard cel-shadow, one line
colour for the whole character (bold uniform outline), highlights only on eyes, hair, gold."""

LINE_COL = '#23234a'

KANHA = dict(
    line=LINE_COL,
    skin='#7d9cf2', skin_sh='#6481dc', skin_hi='#a3baf7', blush='#e58fd0',
    hair='#232647', hair_sh='#171936', hair_hi='#3d4580',
    dhoti='#ffbf2e', dhoti_sh='#f39a1c', dhoti_hem='#e8781a',
    sash='#ff7433', sash_sh='#de5418',
    gold='#ffd04f', gold_sh='#e3a332', gold_hi='#fff2b0',
    gem='#e8384a',
    eye_white='#ffffff', iris='#5a3418', iris_hi='#8c5a2c', pupil='#1a0f0c',
    mouth_in='#7a2340', tongue='#ff7a95', lips='#e86a8a', teeth='#ffffff',
    brow='#232647', tilak='#ffffff', tilak_red='#ff4d4d',
    feather_g='#2f9a4a', feather_g2='#5cc760', feather_y='#ffd04f', feather_teal='#2fc3c9',
    feather_blue='#2a57c9', feather_dark='#1b1f5c',
)
