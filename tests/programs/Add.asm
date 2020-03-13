// Computes R0 = 2 + 3
// R0 refers to RAM[0]

@0x001F
D=A     // D = 2

@3
D=D+A   // D = D + 3

@0
M=D     // RAM[0] = D

