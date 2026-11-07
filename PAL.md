# Phoenix800XL PAL — 256 KB MegaCart

Load `Phoenix800XL-PAL.car` with the emulator set to PAL, or use it on a PAL
Atari XL/XE with a compatible MegaCart implementation. Stock 64 KB RAM is
enough. The CAR header selects type 30; the file contains a 262,144-byte ROM
and a 16-byte header. Joystick controls are unchanged: left/right to move,
fire to start/shoot, down for the shield.

This is a separate PAL cartridge. It retains the scrolling blue background,
seven large birds, five mothership escorts, T1X's hand-drawn artwork, and the
existing campaign and difficulty progression.

## PAL changes

- The fractional simulation and music schedulers compensate for PAL's
  approximately 49.86 Hz display, keeping the original arcade logic near
  61.035 Hz. Ship movement uses the same wall-clock speed as the NTSC version.
- Attract-screen timing is adjusted for the PAL display rate.
- POKEY frequencies and generated sound tables use the PAL clock. Music
  holds/rests remain intact, and no extra victory beeps are introduced.
- Compile-time GTIA color translation matches the existing NTSC colors more
  closely under the emulator's default PAL palette. The sprite pixels remain
  unchanged; translation adds no runtime instructions. Actual display color
  can vary with the television or emulator's palette settings.

## Build

Requires Python 3 and LLVM-MOS SDK. The tested toolchain is the same as the
original build: SDK v23.4.0, clang 24.0.0git, revision
`a40207a371b60ff787ece46817d9c0f62eada719`.

```sh
python3 -m pip install -r requirements.txt
LLVM_MOS=/path/to/llvm-mos python3 tools/build.py --video pal
```

Outputs are `Phoenix800XL-PAL.car`, `build/Phoenix800XL-PAL.car`, and
`build/Phoenix800XL-PAL.rom`. Run the original command without `--video pal`
to produce NTSC. That default build was verified byte-for-byte against the
existing NTSC release.

## Validation — 2026-11-07

Tested on AltirraBridge in PAL mode with stock 64 KB 800XL configuration,
no CPU acceleration, and no VBXE. Physical PAL hardware has not been tested.
The checked cartridge SHA-256 is:

```text
a3d8cb0ad3bc49f035b6c2d1601dd8712753703f390ab60a38b588c8d773bebd
```

The joystick-only automated player completed the mothership and reached
wave 6 after 10,972 video frames (about 220 seconds). RAM reads guided its
controls; it made no game-memory writes. That run reported no late VBI or
display-layout faults. See `evidence/xl/pal/playthrough/report.json`.

Separate stage fixtures exercised each full flock for 600 video frames.
These fixtures select stages and renew invulnerability; movement, rendering
and sound execute normally. All five waves reported zero audio underruns,
missing audio frames, late VBI, and layout faults. Cold boot, joystick
movement, shield input, warm reset and cold reset also passed.

| Wave | Enemies | Measured rendered frames/s |
| --- | ---: | ---: |
| Small birds 1 | 16 | 24.930 |
| Small birds 2 | 16 | 24.930 |
| Large birds 1 | 7 | 23.185 |
| Large birds 2 | 7 | 24.764 |
| Mothership | 5 escorts | 18.282 |

These are rendered frames, not simulation ticks; simulation and sound
continue near 61 Hz. See `evidence/xl/pal/integration/report.json`.

Executable CPU-model comparisons measured 1,220 simulation ticks and 1,220
ship pixels in approximately 20 seconds for both video standards. Across
96 note positions for each of the three tunes, PAL/NTSC note-onset differences
were below 0.019 seconds. The maximum pitch difference was 15.865 cents,
within POKEY's available divider resolution. The CPU model excludes ANTIC
and DMA; live timing is covered by the emulator tests above.
See `evidence/xl/pal/timing-and-music.json`.

To rerun the live checks after a PAL build:

```sh
ALTIRRA_BRIDGE_PACKAGE=/path/to/AltirraBridge python3 tests/xl_integration.py
ALTIRRA_BRIDGE_PACKAGE=/path/to/AltirraBridge python3 tests/xl_playthrough.py --frames 48000
```

Run emulator tests sequentially. For the comparative CPU-model test, retain
a separately built original NTSC source directory and run:

```sh
python3 tests/pal_timing.py --baseline /path/to/original/Phoenix800XL
```

Timing reference: [Atari800 video constants](https://github.com/atari800/atari800/blob/master/src/atari.h).
Palette reference: `src/arcade-assets/xl-video-palettes.json`, captured from
the emulator's default NTSC/PAL palettes. Earlier evidence elsewhere in this
archive describes its recorded cartridge hash; the `evidence/xl/pal` results
apply to this PAL build.
