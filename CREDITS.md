# Credits

**T1X — hand-drawn Atari 5200 sprite artwork**, used in this Atari 800XL port.
The supplied source GIFs, extracted frames, native packed pixels and extraction
manifest are retained in `src/supplied-5200`. They are not redrawn or stretched
for this port. Four directional small-bird poses retain the approved horizontal
reflections from Phoenix5200.

The updated explosion cores, bird-hit bursts, wing fragments and 20 debris
tiles also use **T1X's hand-drawn artwork** in `src/supplied-effects`.
`explosions5.png` is extracted at its native 2:1 wide-pixel scale; shapes are
not interpolated or stretched vertically. Arcade data supplies animation
cadence and fragment placement. See that directory's README for provenance.

Phoenix800XL is based on RobertDupuy/Phoenix5200 v0.31. The original Phoenix
arcade game's identity, graphics, tunes and recovered data retain their original
ownership. Preserved provenance and notices apply to their respective files:

- `src/arcade-assets/ASSET-PROVENANCE.txt`
- `src/arcade-assets/ORIGINAL-NOTICES.md`
- `reference/notices/upstream-LICENSE`
- `reference/notices/upstream-THIRD_PARTY_NOTICES.md`
- `reference/notices/MAME-BSD-3-Clause.txt`

MAME sound reference source retains the original authors' file headers and
BSD notices. LLVM-MOS and Altirra are external build/test tools; their binaries
and original Atari OS ROMs are not included. Historical notices describe the
earlier project's dependencies and do not imply those dependencies are bundled
with this cartridge.
