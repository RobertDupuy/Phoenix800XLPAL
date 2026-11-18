"""Long PAL timing fixture: 6,000 video frames of the full seven-bird wave.
Run on each separately built baseline/current source tree; emulator tests are sequential.
"""
from xl_emulator import XL,ROOT
from xl_integration import stage,S
import json,hashlib
O=ROOT/'evidence/xl/explosions/long-timing';O.mkdir(parents=True,exist_ok=True)
with XL(O) as e:
 a=e.a;a.frame(500);a.joy(0,fire=True);a.frame(8);a.joy(0);a.frame(480)
 a.joy(0,'left');a.frame(20);a.joy(0,'right');a.frame(20);a.joy(0);a.frame(10);a.joy(0,'down');a.frame(8);a.joy(0)
 rows=[]
 for wave in (1,2,3):
  stage(a,wave)
  for _ in range(3):a.poke(S['invuln'],255);a.frame(100)
  before=a.memdump(0,16384)
  for _ in range(60 if wave==3 else 6):a.poke(S['invuln'],255);a.frame(100)
  after=a.memdump(0,16384)
  def delta(n,size=4):return (int.from_bytes(after[S[n]:S[n]+size],'little')-int.from_bytes(before[S[n]:S[n]+size],'little'))%(1<<(size*8))
  row=dict(wave=wave,frames=delta('frames'),renders=delta('fresh_commits'),fps=delta('fresh_commits')/delta('frames')*e.video_hz,late_vbi=delta('late_frames',2),audio_underruns=delta('audio_underruns',2),layout_faults=after[S['layout_faults']]);rows.append(row);print(row,flush=True)
 (O/'report.json').write_text(json.dumps(dict(car_sha256=hashlib.sha256(e.car_path.read_bytes()).hexdigest(),timing=rows),indent=2))
