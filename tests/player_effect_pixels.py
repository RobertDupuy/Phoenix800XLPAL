"""Compare the 800XL's rendered player blast with original executed arcade VRAM.
The reference trace comes from arcade_effect_reference.py, not a port renderer.
"""
import json,sys,hashlib
import numpy as np
from cpu_model import Model,R,S
sys.path.insert(0,str(R/'tools'))
from effect_art import artwork,EFFECT_COLORS
from prepare_native import tables
A=artwork();T=tables();D=json.loads((R/'build/player-effects.json').read_text())
traces=json.loads((R/'evidence/effects-r2/arcade-player-trace.json').read_text())
fg=json.loads((R/'src/arcade-assets/foreground-rgb.json').read_text())['fg']
fragments=dict(zip(A['particle_codes'],A['particles']))
for code in set(v for tr in traces for v in tr['foreground']):
 if code in fragments:continue
 p=np.asarray(fg[str(code)],int);colors=np.asarray(EFFECT_COLORS,int)
 pens=((p[:,:,None,:]-colors[None,None,:,:])**2).sum(3).argmin(2)
 out=np.zeros((8,4),np.uint8)
 for y in range(8):
  for x in range(4):
   pair=list(pens[y,x*2:x*2+2]);out[y,x]=1 if 1 in pair else next((v for v in pair if v),0)
 fragments[code]=out
cores={tuple(T['mothership_explosion_pointers'][o:o+16]):A['ship'][f] for o,f in [(0x20,1),(0x30,0),(0x40,3)]}
def reference(tr):
 out=np.zeros((128,64),np.uint8)
 if any(tr['core']):out[80:112,24:40]=cores[tuple(tr['core'])]
 for i,code in enumerate(tr['foreground']):
  x,y=divmod(i,16);p=fragments[code];tile=out[y*8:y*8+8,x*4:x*4+4];tile[p!=0]=p[p!=0]
 out[out==4]=3
 return out
def decode(m):
 b=m[S['back_buffer']];out=np.zeros((200,160),np.uint8)
 for row in range(25):
  font=(0x2000 if not m[S['large_mode']] else [0x1800,0x2000,0x3000][min(row//8,2)])+b*1024
  for col in range(32):
   ch=m[0x2800+b*1024+row*32+col]&127
   for y in range(8):
    v=m[font+ch*8+y]
    for x in range(4):out[row*8+y,(col+4)*4+x]=(v>>(6-2*x))&3
 return out
checks=0
for wave in (1,3,5):
 for left in (1,12,24):
  for index,tr in enumerate(traces):
   t=Model();t.init();m=t.m.b;m[S['wave']]=wave;t.call('wave_reset');m[S['state']]=3;m[S['death_timer']]=96;m[S['explosion_left']]=left
   m[S['enemy_on']:S['enemy_on']+16]=bytes(16);m[S['display_enemy_on']:S['display_enemy_on']+16]=bytes(16)
   if wave==5:m[S['boss_status']]=2;m[S['boss_scroll']]=248
   t.call('latch_aliens');t.call('render_scene');expected=decode(m)
   ref=reference(tr)
   for cx in range(16):
    for cy in range(16):
     tile=ref[cy*8:cy*8+8,cx*4:cx*4+4];x=cx+left;y=cy+S['player_explosion_row']
     if not tile.any() or not(7<=x<33 and 0<=y<25):continue
     dest=expected[y*8:y*8+8,x*4:x*4+4]
     if wave==5:dest[tile!=0]=tile[tile!=0]
     else:dest[:]=tile
   m[S['death_timer']]=tr['timer'];t.call('draw_explosion')
   got=decode(m);assert np.array_equal(got,expected),(wave,left,index,np.argwhere(got!=expected)[:8].tolist())
   assert not m[S['layout_faults']] and t.m.bank==0
   checks+=1
O=R/'evidence/effects-r2';report=dict(car_sha256=hashlib.sha256((R/'Phoenix800XL-PAL.car').read_bytes()).hexdigest(),cases=checks,original_arcade_ticks=63,pixel_errors=0,edge_positions=3,waves=[1,3,5],bank_restored=True,layout_faults=0,red_to_pink_palette_approximation=True)
(O/'player-explosion-pixels.json').write_text(json.dumps(report,indent=2));print(report)
