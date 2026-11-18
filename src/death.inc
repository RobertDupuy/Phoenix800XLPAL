# Arcade death count: 96 logical ticks; particle/core writes occupy counts 95..33.
# The foreground clears at 32. Life deduction follows at zero. The next round
# waits 128 ticks, with separate setup/handoff ticks and score flashing.
.set death_timer,0x377
.set respawn_timer,0x378
.set explosion_left,0x379
.set effect_count,0xf8
.set effect_cursor,0xf9
.set effect_cell,0xfa
.set respawn_population,0x761
.set respawn_new_game,0x762
.set respawn_stage,0x765
.set gameover_timer,0x7ed
.set restart_blank,0x7ee
.set gameover_armed,0x7ef
.section .expanded_code,"ax",@progbits
.global death_tick,respawn_tick,draw_explosion
death_tick:
 lda death_timer
 and #1
 beq death_burst_done
 jsr burst_tick
death_burst_done:
 dec death_timer
 lda death_timer
 cmp #32
 bne death_keep_projectiles
 jsr clear_projectiles
death_keep_projectiles:
 lda death_timer
 bne death_tick_done
 dec lives
 lda #3
 sta life_dirty
 lda lives
 beq death_game_over
 lda #4
 sta state
 lda #0
 sta respawn_new_game
 lda #128
 sta respawn_timer
 lda #2
 sta respawn_stage
 rts
death_game_over:
 lda #2
 sta state
 lda #183
 sta gameover_timer
 lda #0
 sta gameover_armed
 sta fire_edge
death_tick_done:
 rts
respawn_tick:
 lda #3
 sta hud_dirty
 lda respawn_stage
 cmp #2
 bne respawn_flash
 dec respawn_stage
 rts
respawn_flash:
 lda respawn_timer
 beq respawn_initialize
 dec respawn_timer
 rts
respawn_initialize:
 lda #100
 sta raw_ship_x
 sta video_ship_x
 lda #126
 sta ship_x
 lda #0
 sta invuln
 sta fire_edge
 lda #1
 sta state
 lda respawn_new_game
 beq respawn_survivors
 lda #0
 sta respawn_new_game
 jsr begin_wave
 lda #0
 sta entrance_initial_wait
 rts
respawn_survivors:
 jsr shield_reset
 lda large_mode
 cmp #3
 bne 8f
 jsr clear_projectiles
 jmp arcade_reset
8: lda large_mode
 beq respawn_small
 jmp large_resume
respawn_small:
 jsr arcade_resume
 rts
.section .text,"ax",@progbits
draw_explosion:
 lda state
 cmp #3
 beq 1f
 rts
1:
 # XL MegaCart bank 9 holds the new player blast; all NMI code stays in RAM.
 lda #9
 sta 0xd500
 jsr 0x8000
 lda #2
 sta 0xd500
 rts
