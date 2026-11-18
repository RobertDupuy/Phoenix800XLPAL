"""Compile the arcade particle/core timeline into the dedicated death bank."""
from pathlib import Path
import json
from arcade_effects import player_frames
from prepare_native import tables

R=Path(__file__).resolve().parents[1]
B=R/'build'

def prepare():
    images,timeline=player_frames(tables())
    tiles=[];frames=[]
    for image in images[::2]:
        cells=[]
        for cx in range(16):
            for cy in range(16):
                raw=image[cy*8:cy*8+8,cx*4:cx*4+4]
                data=bytes(sum((3 if v==4 else int(v))<<(6-2*x) for x,v in enumerate(row))for row in raw)
                if not any(data):continue
                mask=bytes(sum((0 if v else 3)<<(6-2*x)for x,v in enumerate(row))for row in raw)
                tile=data+mask
                if tile not in tiles:tiles.append(tile)
                cells.append([cx*16+cy,tiles.index(tile)])
        frames.append(cells)
    assert len(tiles)<128 and max(map(len,frames))<64
    inc=['death_frames: .word '+','.join('death_frame_'+str(i)for i in range(len(frames))),
         'death_tiles: .word '+','.join('death_tile_'+str(i)for i in range(len(tiles)))]
    for i,frame in enumerate(frames):
        inc.append('death_frame_'+str(i)+': .byte '+','.join(map(str,[len(frame)]+[v for c in frame for v in c])))
    for i,tile in enumerate(tiles):inc.append('death_tile_'+str(i)+': .byte '+','.join(map(str,tile)))
    (B/'player-effects.inc').write_text('\n'.join(inc)+'\n')
    (B/'player-effects.json').write_text(json.dumps(dict(frames=frames,tiles=[list(t)for t in tiles],timeline=timeline,
        source='Original arcade $0BBA/$2070/$20E8/$2800/$2900/$1B90; T1X supplied Atari pixels',
        red_mapped_to_pink=True),separators=(',',':')))
    print('Player explosion:',len(frames),'snapshots,',len(tiles),'tiles; max',max(map(len,frames)),'cells')
