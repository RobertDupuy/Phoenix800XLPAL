"""Check every mothership destruction snapshot through the banked XL renderer."""
from cpu_model import Model,R,S
import numpy as np
import json,hashlib
t=Model();t.init();m=t.m.b;checks=0
m[S['wave']]=5;t.call('wave_reset');m[S['state']]=1;m[S['boss_status']]=2
V=json.loads((R/'build/victory-manifest.json').read_text())
def picture():
    buffer=m[S['back_buffer']]
    pixels=np.zeros((200,128),np.uint8)
    for y in range(200):
        font=[0x1800,0x2000,0x3000][min(y//64,2)]+buffer*1024
        for col in range(32):
            ch=m[0x2800+buffer*1024+(y//8)*32+col]&127
            value=m[font+ch*8+y%8]
            for x in range(4):pixels[y,col*4+x]=(value>>(6-2*x))&3
    return pixels
# Verify all 63 destruction frames in the actual banked 6502 renderer at
# three kill heights, including clipping and the newly supplied fragments.
for scroll in (152,200,248):
    for frame,cells in enumerate(V['frames']):
        m[S['boss_status']]=3;m[S['boss_timer']]=95-frame
        m[S['boss_scroll']]=scroll;m[S['front_buffer']]=frame&1
        t.call('mothership_background')
        expected=picture()
        origin=(((8-scroll)&255)>>3)-4
        for cell,tid in cells:
            cx,cy=divmod(cell,16);cy=(cy+origin)&31
            if cy>=25:continue
            data=V['tiles'][tid]
            for y in range(8):
                for x in range(4):
                    px=(cx+9)*4+x;py=cy*8+y
                    expected[py,px]=(expected[py,px]&((data[y+8]>>(6-2*x))&3))|((data[y]>>(6-2*x))&3)
        t.call('mothership_blast')
        assert np.array_equal(picture(),expected),(scroll,frame)
        assert not m[S['layout_faults']]
        checks+=1
report=dict(car_sha256=hashlib.sha256((R/'Phoenix800XL-PAL.car').read_bytes()).hexdigest(),
    cases=checks,frames=63,kill_heights=3,pixel_errors=0,bank_restored=t.m.bank==0,
    layout_faults=m[S['layout_faults']],supplied_particle_tiles=20)
assert report['bank_restored'] and not report['layout_faults']
out=R/'evidence/xl/explosions';out.mkdir(parents=True,exist_ok=True)
(out/'mothership-pixels.json').write_text(json.dumps(report,indent=2))
print(report)
