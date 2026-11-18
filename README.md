# Phoenix for PAL Atari 800XL/XE

**256 KB MegaCart — beta 2.** Runs on a stock 64 KB PAL Atari XL/XE with
standard ANTIC, GTIA and POKEY hardware.

Download **Phoenix800XL-PAL.car** from the [beta 2 release](../../releases/tag/beta-2).
Use **CAR type 30 (256 KB MegaCart)** and configure your emulator for **PAL**.
The release includes the complete source and test archive, with screenshots.

This update adds the new player and bird explosions, wing fragments, and
scattered debris during player death and mothership destruction. Artwork is
extracted from T1X's supplied Atari sheet; the arcade's explosion timing and
fragment placement are retained. See [EXPLOSIONS.md](EXPLOSIONS.md).

| Joystick port 1 control | Action |
| --- | --- |
| Left / right | Move |
| Fire | Start / shoot |
| Down | Activate shield |
| START key | Start a game |

The PAL build retains its simulation timing, ship speed, sound tuning and
palette conversion. It keeps the scrolling dark-blue background, seven large
birds, five mothership escorts, the five-wave cycle, later difficulty changes,
respawn protections, and the victory tune without repeating bonus beeps.

Hand-drawn sprite artwork is by **T1X**. See [CREDITS.md](CREDITS.md) for
asset provenance and notices.

## Build

Requires Python 3 and LLVM-MOS SDK:

```sh
python3 -m pip install -r requirements.txt
LLVM_MOS=/path/to/llvm-mos python3 tools/build.py --video pal
```

This produces `Phoenix800XL-PAL.car`, containing a 262,144-byte ROM and
16-byte CAR header. The published checksum is in [SHA256SUMS-PAL.txt](SHA256SUMS-PAL.txt).

## Testing

The automated joystick player cleared the mothership and reached wave 6 in
PAL emulation. All five wave fixtures and four death/destruction sequences
passed without detected audio underruns, missing audio frames, late VBI, or
display-layout faults. Cold boot, controls, shield, warm reset and cold reset
also passed. Explosion pixels, ordinary bird rendering, scrolling, campaign,
respawn behavior and PAL timing have separate automated checks.

Physical PAL hardware has not yet been tested. See [PAL.md](PAL.md) and
[EXPLOSIONS.md](EXPLOSIONS.md) for measurements, test scope and instructions.
Current reports identify their cartridge hash. Older evidence and NTSC
documents describe their own recorded hashes.

The original NTSC project is [RobertDupuy/Phoenix800XL](https://github.com/RobertDupuy/Phoenix800XL).
