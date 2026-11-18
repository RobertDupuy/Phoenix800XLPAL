# PAL beta 2 — explosions and scattered debris

Tested cartridge SHA-256: `02af08c21f15e8994ad2d20f84d830a7070fb1b72af8806eda572035442d8bfb`.

This update brings the NTSC 800XL explosion/debris artwork to the existing
PAL MegaCart build. Player death now has the arcade-pattern central flash
and spreading debris instead of four isolated solid bursts. Bird hits and
wing fragments use T1X's supplied artwork. Mothership destruction retains
its 63-tick sequence with the supplied core and 20 debris tiles.

The extraction uses the lower, wide-pixel half of `explosions5.png`.
There is no vertical stretching or interpolated detail. Where the player's
three-color character budget requires it, red particles share the pink pen.
The supplied mechanism GIF is retained by the shared extractor; this update
does not change the PAL mothership mechanism or cockpit animation.

## Scope and regression checks

The base is PAL beta commit `e2362266915a13242277d408016480f7b3c788b2`,
cartridge SHA-256 `a3d8cb0ad3bc49f035b6c2d1601dd8712753703f390ab60a38b588c8d773bebd`.
It rebuilds byte-for-byte before applying these changes. The only modified
existing assembly file is the drawing portion of `src/death.inc`; its death
and respawn state machine is unchanged. The added player renderer occupies
MegaCart bank 9. All interrupt code remains resident in RAM.

PAL clock configuration, color conversion, generated audio data, ordinary
bird sprites, title, ship/shield/cockpit planes and scrolling scenery compare
byte-for-byte with that baseline. Population assertions require seven large
birds and five escorts. Cartridge type and size remain 30 / 256 KB.

| Check | Result |
| --- | --- |
| Player explosion vs executed arcade VRAM reference | 567 cases, zero pixel errors |
| Mothership destruction at three heights | 189 cases, zero pixel errors |
| Source sprite and PMG checks | 352 checks, 59 normal source frames preserved |
| Ordinary large birds vs PAL beta | 640 frames, exact pixels |
| Ordinary mothership vs PAL beta | 280 frames, exact pixels |
| Scrolling/death scenes | 544 scenes, 256 entrance offsets, no blank bands |
| Crowded shields | 64 cases, zero pixel errors/layout faults |
| Campaign | 411 checks across 16 rounds |
| Respawn | 800 death/respawn cases; 5,536 immediate-collision checks |
| Victory tune | 720 ticks, no bonus-beep register mismatches |
| PAL timing and tunes | Arcade-rate logic/ship movement; all 96 positions in each tune |
| Live death/destruction | Waves 1, 3, 5 and mothership victory; normal respawn/next wave |
| Joystick-only playthrough | Reached wave 6 at frame 10,972; same events as PAL beta |

Live checks used stock 64 KB PAL 800XL emulation, the built-in Altirra XL OS,
normal CPU and no accelerated hardware. The five 600-frame stage fixtures
and four death/destruction runs had no late VBI, audio underruns, missing
audio updates or layout faults. The automated player used RAM observations
and joystick input; it made no game-memory writes. The stage/death fixtures
explicitly set stage/state and invulnerability and are not ordinary play.
Physical PAL hardware has not been tested.

The short wave-3 fixture measured 23.019 vs 23.185 rendered frames/s.
To distinguish scheduling phase from a sustained slowdown, the same full
flock was measured for 6,000 video frames: 23.119 vs 23.036 rendered frames/s,
with no audio or display faults. Other 600-frame wave rates matched the
baseline: 24.930, 24.930, 24.764 and 18.282 frames/s for waves 1, 2, 4 and 5.
CPU-only ordinary renderer checks used 0.11% fewer large-bird cycles and
0.07% fewer mothership cycles. These sampled results do not guarantee every
possible overlap or physical hardware configuration.

## Reproduce

Build with `LLVM_MOS=/path/to/llvm-mos python3 tools/build.py --video pal`.
Then run:

```sh
python3 tests/player_effect_pixels.py
python3 tests/mothership_effect_pixels.py
python3 tests/explosion_artwork.py
python3 tests/xl_scroll.py
python3 tests/xl_scenery_shield.py
python3 tests/campaign_acceptance.py
python3 tests/respawn_v019.py
python3 tests/small_respawn_v020.py
python3 tests/return_facing_v030.py
python3 tests/victory_beeps.py
python3 tests/xl_large_oracle.py --baseline /path/to/built-original-PAL-beta
python3 tests/xl_mothership_oracle.py --baseline /path/to/built-original-PAL-beta
python3 tests/pal_timing.py --baseline /path/to/built-NTSC-Phoenix800XL
export ALTIRRA_BRIDGE_PACKAGE=/path/to/AltirraBridge-nightly-linux-x86_64
python3 tests/xl_integration.py
python3 tests/explosions_live.py
python3 tests/xl_playthrough.py
python3 tests/explosions_timing.py
```

Run emulator tests sequentially. Original arcade traces are in
`evidence/effects-r2`; current explosion reports are in `evidence/xl/explosions`.
Other current reports are identified by the hash above. Historical reports
retain their original hashes. The release ZIP includes screenshot evidence;
emulator binaries, OS ROMs and authentication logs are excluded.
