.include "build/main-symbols.inc"
.include "src/campaign-defs.inc"
.section .player_effects,"ax",@progbits
.global player_effects_entry
player_effects_entry:
 lda state
 cmp #3
 beq 1f
 rts
1:
 lda death_timer
 cmp #33
 bcs 1f
 rts
1:
 cmp #96
 bcc 1f
 rts
1:
 lda #95
 sec
 sbc death_timer
 and #254
 tax
 lda death_frames,x
 sta record_ptr
 lda death_frames+1,x
 sta record_ptr+1
 ldy #0
 lda (record_ptr),y
 bne 1f
 rts
1:
 sta effect_count
 lda #1
 sta effect_cursor
death_cell:
 ldy effect_cursor
 lda (record_ptr),y
 sta effect_cell
 iny
 lda (record_ptr),y
 sta draw_template
 iny
 sty effect_cursor
 lda effect_cell
 and #15
 clc
 adc #player_explosion_row
 cmp #25
 bcs death_next
 sta draw_row
 lda effect_cell
 lsr
 lsr
 lsr
 lsr
 clc
 adc explosion_left
 cmp #7
 bcc death_next
 cmp #33
 bcs death_next
 sta draw_col
 jsr row_pointer
 lda #0
 sta tile_offset
 sta draw_palette
 lda large_mode
 beq death_small
 jsr death_large_destination
 jmp death_copy
death_small:
 jsr allocate_glyph
 bcs death_next
death_copy:
 lda draw_template
 asl
 tax
 lda death_tiles,x
 sta src_data
 lda death_tiles+1,x
 sta src_data+1
 ldy #7
death_copy_row:
 lda large_mode
 cmp #3
 beq death_over_ship
 lda (src_data),y
 sta (dst_ptr),y
 jmp death_row_done
death_over_ship:
 tya
 ora #8
 tay
 lda (src_data),y
 tax
 tya
 and #7
 tay
 txa
 and (boss_bgptr),y
 ora (src_data),y
 sta (dst_ptr),y
death_row_done:
 dey
 bpl death_copy_row
death_next:
 dec effect_count
 beq death_done
 jmp death_cell
death_done:
 rts
death_large_destination:
 lda draw_row
 lsr
 lsr
 lsr
 cmp #3
 bcc 1f
 lda #2
1: tax
 lda lg_font_bases,x
 sta font_hi
 lda back_buffer
 asl
 asl
 clc
 adc font_hi
 sta font_hi
 ldy #0
 lda (map_ptr),y
 and #127
 tax
 lda glyph_lo,x
 sta boss_bgptr
 lda glyph_hi,x
 ora font_hi
 sta boss_bgptr+1
 lda #0
 sta (map_ptr),y
 jmp large_cell_glyph
.include "build/player-effects.inc"
