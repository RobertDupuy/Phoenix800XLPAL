T1X — hand-drawn Atari 5200 sprite artwork.

mothership2.gif: original supplied 96x96, five frames, 100 ms per frame.
A native Atari wide pixel is represented by a uniform 6x3 capture block.
Each frame contains a 16x16-pixel piston/shaft mechanism above an 8x16 alien.

explosions5.png: original supplied 161x276 sheet.
The lower half supplies the Atari redraws at 2x1 per wide pixel.
Upper arcade artwork is retained for reference, not substituted for the redraws.

The left divider obscures the left half of the first pixel in crops beginning
at x=1. The surviving half at x=2 is duplicated to recover that wide pixel.
Every other extracted pixel block must match exactly or the build fails.
No interpolated resizing or vertical stretching is used.

Run python3 tools/effect_art.py to write the separate frames and sprite atlas
into build/artwork-frames. Both native-grid and 2:1 display PNGs are included.
The native PNGs store one pixel per Atari wide pixel; they are not square-pixel
previews. The display PNGs show the intended 2:1 aspect without added detail.
