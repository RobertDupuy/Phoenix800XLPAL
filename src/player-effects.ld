ENTRY(player_effects_entry)
SECTIONS {
 .player_effects 0x8000 : { *(.player_effects) }
 /DISCARD/ : { *(.comment) *(.llvm_addrsig) }
}
