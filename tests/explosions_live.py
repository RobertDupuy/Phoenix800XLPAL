"""Actual PAL XL output during staged player deaths and mothership victory.

The fixture sets death/victory state once, then the unmodified cartridge runs
its normal rendering, sound, timers and respawn. Invulnerability prevents a
new accidental death after the measured respawn. Captures are emulator pixels.
"""
from xl_emulator import XL, ROOT as R
from xl_integration import stage, set_values
import json, hashlib

S=json.loads((R/'build/symbols.json').read_text())
O=R/'evidence/xl/explosions/live'

def counter(m,name,n=2):
    return int.from_bytes(m[S[name]:S[name]+n],'little')

with XL(O) as e:
    a=e.a; a.frame(500); a.joy(0,fire=True); a.frame(8); a.joy(0); a.frame(480)
    reports=[]
    for wave in (1,3,5,5):
        victory=len(reports)==3
        stage(a,wave)
        a.bp_set(S['simulation_update']); a.cycles(240000); a.bp_clear_all()
        if victory:
            set_values(a,dict(boss_status=3,boss_timer=96,boss_scroll=248,
                shot_on=0,second_on=0,bomb_on=[0]*5,audio_death_pending=64))
        else:
            set_values(a,dict(state=3,death_timer=96,explosion_left=12,
                raw_ship_x=100,video_ship_x=100,audio_death_pending=16,
                shot_on=0,second_on=0,bomb_on=[0]*5))
        name='mothership' if victory else f'player-wave{wave}'
        folder=O/name; folder.mkdir(exist_ok=True)
        before=a.memdump(0,16384); a.pokey_trace_start(16000); samples=[]
        for frame in range(270):
            a.poke(S['invuln'],255); a.frame(1)
            a.bp_set(S['nmi_handler']); a.cycles(40000); a.bp_clear_all()
            m=a.memdump(0,16384)
            samples.append(dict(frame=frame,state=m[S['state']],wave=m[S['wave']],
                death=m[S['death_timer']],boss=m[S['boss_status']],
                boss_timer=m[S['boss_timer']],lives=m[S['lives']],
                layout_faults=m[S['layout_faults']]))
            if frame<170:
                a.screenshot(path=str(folder/f'frame-{frame:03}.png'))
        after=m; a.pokey_trace_stop(); events=[]
        while True:
            tr=a.pokey_trace_read(4096)
            assert tr['valid'] and not tr['dropped']
            events.extend(tr['events'])
            if not tr['queued']:break
        ticks=[v['tick'] for v in events if v['reg']==1]
        gaps=[y-x for x,y in zip(ticks,ticks[1:])]
        row=dict(name=name,late_vbi=(counter(after,'late_frames')-counter(before,'late_frames'))&65535,
            audio_underruns=(counter(after,'audio_underruns')-counter(before,'audio_underruns'))&65535,
            layout_faults=after[S['layout_faults']],
            missing_audio_frames=sum(max(0,round(g/(e.scanlines*114))-1) for g in gaps),
            max_audio_gap_clocks=max(gaps),samples=samples)
        assert row['late_vbi']==row['audio_underruns']==row['layout_faults']==row['missing_audio_frames']==0,row
        if victory:
            assert any(s['boss']==4 for s in samples) and after[S['wave']]==6
        else:
            assert any(s['state']==4 for s in samples) and after[S['state']]==1
            assert after[S['lives']]==before[S['lives']]-1
        reports.append(row)
        print({k:v for k,v in row.items() if k!='samples'},flush=True)
    report=dict(method=__doc__,car_sha256=hashlib.sha256((R/'Phoenix800XL-PAL.car').read_bytes()).hexdigest(),
        config=e.config,scenes=reports)
    (O/'report.json').write_text(json.dumps(report,indent=2))
