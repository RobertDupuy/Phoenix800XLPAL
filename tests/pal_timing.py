"""Compare executable PAL/NTSC clocks, ship speed, and all three music sequences.

The CPU harness excludes ANTIC/DMA. Live PAL timing and playback are checked
separately in xl_integration.py and the joystick-only playthrough.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);args=p.parse_args()
R=Path(__file__).resolve().parents[1]
def load(root,name):
 spec=importlib.util.spec_from_file_location(name,root/'tests/cpu_model.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
mods=[load(args.baseline,'ntsc_cpu'),load(R,'pal_cpu')]
fps=[1789772.5/(262*114),1773447/(312*114)];clock=[1789772.5,1773447.0]
rate=[];tunes=[[],[]]
for ix,mod in enumerate(mods):
 s=mod.S;t=mod.Model();t.init();m=t.m.b
 m[s['state']]=0;m[s['simulation_frame']]=0;m[s['arcade_fraction']:s['arcade_fraction']+2]=bytes(2)
 m[s['sim_steps']:s['sim_steps']+4]=bytes(4)
 frames=round(fps[ix]*20)
 for f in range(1,frames+1):
  m[s['frames']]=f&255;t.call('simulation_update')
 ticks=int.from_bytes(m[s['sim_steps']:s['sim_steps']+4],'little');seconds=frames/fps[ix]
 assert abs(ticks-seconds*61.03515625)<1.1,(ix,ticks,seconds)
 # Reset position after each real update to avoid the screen-edge clamp.
 m[s['state']]=1
 for k in ['boss_status','boss_entrance_shown','entrance_timer','entrance_handoff','shield_locked']:m[s[k]]=0
 m[s['stick_x']]=228;m[s['ship_video_fraction']:s['ship_video_fraction']+2]=bytes(2)
 moved=0
 for f in range(frames):
  m[s['video_ship_x']]=100;m[s['video_phase']]=f&1;t.call('video_player_update');moved+=m[s['video_ship_x']]-100
 assert abs(moved-seconds*61.03515625)<1.1,(ix,moved,seconds)
 rate.append(dict(video='pal' if ix else 'ntsc',frames=frames,seconds=seconds,simulation_ticks=ticks,ship_pixels=moved,simulation_hz=ticks/seconds,ship_pixels_per_second=moved/seconds))
 for tune in (1,2,3):
  t=mod.Model();t.init();m=t.m.b;m[0x3e00:0x3e50]=bytes(80)
  m[s['music_pending']]=0;m[s['music_fraction']:s['music_fraction']+2]=bytes(2)
  m[s['state']]=0;m[s['boss_status']]=0;m[s['large_mode']]=0
  m[s['arcade_clock']:s['arcade_clock']+2]=bytes(2)
  m[s['g_sound_a']]=15;m[s['g_sound_b']]=(tune<<6)|15
  notes=[];last=0
  for frame in range(round(23*fps[ix])):
   t.call('music_compute');pos=m[s['tune_pos']]
   if pos!=last:
    notes.append(dict(position=pos,time=(frame+1)/fps[ix],pitch=[m[s['fr0']],m[s['fr1']]]));last=pos
   if pos==96:break
  assert len(notes)==96,(ix,tune,len(notes))
  tunes[ix].append(notes)
comparisons=[]
for n in range(3):
 a,b=tunes[0][n],tunes[1][n]
 delta=max(abs(x['time']-y['time']) for x,y in zip(a,b));assert delta<1/fps[0]+1/fps[1]
 cents=[];untuned=[]
 for x,y in zip(a,b):
  for v,w in zip(x['pitch'],y['pitch']):
   if not v:continue
   expected=clock[0]/(56*(v+1));actual=clock[1]/(56*(w+1))
   cents.append(abs(1200*math.log2(actual/expected)))
   untuned.append(abs(1200*math.log2(clock[1]/clock[0])))
 assert sum(cents)<sum(untuned),(n,sum(cents),sum(untuned))
 comparisons.append(dict(tune=n+1,notes=96,max_note_time_difference_seconds=delta,pal_last_note_seconds=b[-1]['time'],ntsc_last_note_seconds=a[-1]['time'],mean_pitch_difference_cents=sum(cents)/len(cents),max_pitch_difference_cents=max(cents)))
report=dict(method=__doc__,car_sha256=hashlib.sha256((R/'Phoenix800XL-PAL.car').read_bytes()).hexdigest(),rates=rate,tunes=comparisons)
o=R/'evidence/xl/pal';o.mkdir(parents=True,exist_ok=True);(o/'timing-and-music.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
