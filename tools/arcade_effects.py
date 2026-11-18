"""Original Phoenix death dispatcher ($0BBA/$2070/$20E8), with supplied art.

The arcade alternates particle masks and a background core on odd ticks.
Even ticks leave these layers intact while maintaining bird-hit animations.
Source shapes are not stretched; only the Atari's existing 2:1 pixel aspect
is used for original fragments absent from the supplied sheet.
"""
import json
from pathlib import Path
import numpy as np
from effect_art import artwork, EFFECT_COLORS

R = Path(__file__).resolve().parents[1]

def player_frames(t):
    a = artwork()
    supplied = dict(zip(a['particle_codes'], a['particles']))
    fg = json.loads((R/'src/arcade-assets/foreground-rgb.json').read_text())['fg']
    page = t['explosion_particle_page']
    ptrs = t['mothership_explosion_pointers']
    def fragment(code):
        if code in supplied:
            return supplied[code]
        rgb = np.asarray(fg[str(code)], dtype=int)
        colors = np.asarray(EFFECT_COLORS, dtype=int)
        pens = ((rgb[:,:,None,:]-colors[None,None,:,:])**2).sum(3).argmin(2)
        # Original ROM glyphs have 8 square pixels, the port has 4 wide ones.
        out = np.zeros((8,4), np.uint8)
        for y in range(8):
            for x in range(4):
                p = pens[y,x*2:x*2+2]
                out[y,x] = 1 if 1 in p else next((v for v in p if v), 0)
        return out
    fragments = {c:fragment(c) for c in set(page[:256])}
    field = np.zeros((128,64), np.uint8)
    core = np.zeros((32,16), np.uint8)
    frames, records = [], []
    for timer in range(95,32,-1):
        if timer & 3 == 3:
            off = 0x100 + 0xe0 - (((timer-32)*4)&0xe0)
            field.fill(0)
            for i, code in enumerate(page[:256]):
                if page[off+i//8] & (1<<(i%8)):
                    x,y = divmod(i,16)
                    field[y*8:y*8+8,x*4:x*4+4] = fragments[code]
        elif timer & 3 == 1:
            off = 0x50 + ((timer>>2)&14)
            addr = int.from_bytes(ptrs[off:off+2],'big')
            core = np.zeros((32,16),np.uint8) if addr==0x17f0 else a['ship'][{0x1b60:1,0x1b70:0,0x1b80:3}[addr]]
        image = np.zeros_like(field)
        image[80:112,24:40] = core
        image[field!=0] = field[field!=0]
        frames.append(image)
        records.append(dict(timer=timer,particle_mask=(0xe0-(((timer-32)*4)&0xe0))//32,
                            operation='particles' if timer&3==3 else 'core' if timer&3==1 else 'hold'))
    return frames, records
