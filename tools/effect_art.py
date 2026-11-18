"""Lossless extraction of T1X's supplied wide-pixel explosions and mechanism.

The GIF is captured at 6x3 per Atari pixel; the lower PNG sheet is 2x1.
Only the clipped half-pixel at the sheet's left divider is reconstructed,
from its surviving other half. No shape interpolation or vertical scaling.
"""
from functools import lru_cache
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]
A = R / 'src/supplied-effects'
EFFECT_COLORS = [(0,0,0), (255,255,255), (246,246,67), (211,31,210), (202,21,23)]
MECHANISM_COLORS = [(0,0,0), (205,240,63), (237,198,57), (167,27,206)]
PILOT_COLORS = [(0,0,0), (41,181,182), (167,27,206), (209,29,170)]

def indexed(rgb, palette):
    out = np.full(rgb.shape[:2], 255, np.uint8)
    for i, color in enumerate(palette):
        out[np.all(rgb == color, axis=2)] = i
    assert not np.any(out == 255), np.unique(rgb[out == 255], axis=0)
    return out

@lru_cache(None)
def artwork():
    gif = Image.open(A/'mothership2.gif')
    pistons, pilots, durations = [], [], []
    for f in range(gif.n_frames):
        gif.seek(f)
        rgb = np.asarray(gif.convert('RGB'))
        native = rgb[::3, ::6]
        assert np.array_equal(rgb, native.repeat(3,0).repeat(6,1))
        pistons.append(indexed(native[:16], MECHANISM_COLORS))
        pilots.append(indexed(native[16:,4:12], PILOT_COLORS))
        assert not np.any(native[16:,:4]) and not np.any(native[16:,12:])
        durations.append(gif.info['duration'])
    assert len(pistons) == 5 and durations == [100]*5
    sheet = np.asarray(Image.open(A/'explosions5.png').convert('RGB'))
    def crop(box):
        x,y,r,b = box
        rgb = sheet[y:b,x:r].copy()
        if x == 1:
            # The divider obscures just the left half of this wide pixel.
            rgb[:,0] = rgb[:,1]
        assert np.array_equal(rgb[:,::2], rgb[:,1::2]), box
        return indexed(rgb[:,::2], EFFECT_COLORS)
    ship, core = [], []
    for y, target in [(142,ship),(176,core)]:
        for x in [2,35,69]:
            target.append(crop((x,y,x+32,y+32)))
        target.append(np.pad(crop((103,y+8,119,y+24)), ((8,8),(4,4))))
    bursts = [crop((x,240,x+24,256)) for x in [1,27,53]]
    tiny = np.zeros((16,12), np.uint8)
    tiny[8:,4:8] = crop((79,248,87,256))
    # Keep the original eight animation stages: blank, tiny, expanding burst.
    burst_sequence = [np.zeros((16,12),np.uint8),tiny,bursts[2],bursts[1],
                      bursts[0],bursts[1],bursts[0],bursts[1]]
    wings = [crop((x,240,x+24,256)) for x in [89,115]]
    # Retain the alternate yellow artwork as separate editable source frames.
    yellow = [crop((x,258,x+24,274)) for x in [1,27,53]]
    yellow_tiny = np.zeros((16,12),np.uint8)
    yellow_tiny[8:,4:8] = crop((79,266,87,274))
    yellow.append(yellow_tiny)
    yellow_wings = [crop((x,258,x+24,274)) for x in [89,115]]
    # Individual lower-sheet fragments used by the arcade's victory pattern.
    # Tile identities are matched against the corresponding upper-sheet tiles.
    particle_codes = [224,194,225,206,207,222,223,192,193,195,226,227]
    particles = [crop((x,210,x+8,218)) for x in range(41,152,10)]
    corners = crop((81,222,97,238))
    for code,cx,cy in [(200,0,0),(216,0,1),(202,1,0),(218,1,1)]:
        particle_codes.append(code)
        particles.append(corners[cy*8:cy*8+8,cx*4:cx*4+4].copy())
    for code,x in zip(range(208,212),[117,127,137,147]):
        particle_codes.append(code)
        particles.append(crop((x,222,x+8,230)))
    return dict(pistons=pistons, pilot=pilots, ship=ship, core=core,
                bursts=burst_sequence, bonus=wings, particles=particles,
                bursts_yellow=yellow, bonus_yellow=yellow_wings,
                particle_codes=particle_codes, durations_ms=durations)

def export():
    out = R/'build/artwork-frames'
    out.mkdir(parents=True, exist_ok=True)
    data = artwork()
    panels = []
    for group, palette in [('pistons',MECHANISM_COLORS),('pilot',PILOT_COLORS),
                           ('ship',EFFECT_COLORS),('core',EFFECT_COLORS),
                           ('bursts',EFFECT_COLORS),('bonus',EFFECT_COLORS),
                           ('particles',EFFECT_COLORS),('bursts_yellow',EFFECT_COLORS),
                           ('bonus_yellow',EFFECT_COLORS)]:
        for f, pixels in enumerate(data[group]):
            rgb = np.asarray(palette,np.uint8)[pixels]
            Image.fromarray(rgb).save(out/f'{group}-{f:02}-native.png')
            display = Image.fromarray(rgb.repeat(2,1))
            display.save(out/f'{group}-{f:02}-display.png')
            panels.append((f'{group} {f}', display.resize((display.width*3,display.height*3),Image.Resampling.NEAREST)))
    atlas = Image.new('RGB',(5*130,((len(panels)+4)//5)*122),(24,24,24))
    draw = ImageDraw.Draw(atlas)
    for i,(name,im) in enumerate(panels):
        x,y = (i%5)*130,(i//5)*122
        draw.text((x+4,y+3),name,fill='white')
        atlas.paste(im,(x+4,y+20))
    atlas.save(out/'extracted-sprites.png')
    manifest = {k:[a.tolist() for a in v] if k not in ('durations_ms','particle_codes') else v for k,v in data.items()}
    manifest.update(credit='T1X — hand-drawn artwork',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [A/'mothership2.gif',A/'explosions5.png']},
        note='GIF capture blocks 6x3; lower PNG wide pixels 2x1. Left border clips half of the first pixel in column-1 crops; its surviving half is duplicated. Frames otherwise round-trip exactly.')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__ == '__main__':
    export()
