# Phoenix for PAL Atari 800XL/XE

**256 KB MegaCart — beta.** Runs on a stock 64 KB PAL Atari XL/XE with
standard ANTIC, GTIA and POKEY hardware.

Download **Phoenix800XL-PAL.car** from the [beta release](../../releases/tag/beta).
Use **CAR type 30 (256 KB MegaCart)** and configure your emulator for **PAL**.
The release also includes the complete source and test archive, with screenshots.

| Joystick port 1 control | Action |
| --- | --- |
| Left / right | Move |
| Fire | Start / shoot |
| Down | Activate shield |
| START key | Start a game |

The PAL build adjusts simulation timing, ship speed, sound pitch and colors
for the PAL display and POKEY clock. It retains the scrolling dark-blue
background, seven large birds, five mothership escorts, the five-wave cycle,
later difficulty changes, and mothership destruction with the victory tune.

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
PAL emulation. All five wave fixtures passed with no detected audio underruns,
missing audio frames, late VBI, or display-layout faults. Cold boot, joystick
controls, shield, warm reset and cold reset also passed.

Physical PAL hardware has not yet been tested. See [PAL.md](PAL.md) for
timing measurements, exact test scope, and instructions. Test reports and
inputs are in `evidence/xl/pal`; the release source archive includes screenshots
and the full historical evidence set. Earlier NTSC documents and reports
describe their recorded cartridge hashes.

The original NTSC project is [RobertDupuy/Phoenix800XL](https://github.com/RobertDupuy/Phoenix800XL).
