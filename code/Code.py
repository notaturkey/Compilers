#!/usr/bin/env python3


class Code:
    """
    Code is responsible for generating the bits-strings that correspond to the parsed instructions parts: dest, comp and jmp.
    It generates A-Instructions and C-Instructions via the gen_a_instruction() and gen_c_instruction() methods as strings
    of binary characters of 1's and 0's.
    """
    # The JUMP part codes
    _jump_codes = ['', 'JGT', 'JEQ', 'JGE', 'JLT', 'JNE', 'JLE', 'JMP']

    # The DEST part codes
    _dest_codes = ['', 'M', 'D', 'MD', 'A', 'AM', 'AD', 'AMD']

    # The COMP part codes
    _comp_codes = {'0': '0101010', '1': '0111111', '-1':'0111010', 'D':'0001100', 'A': '0110000', '!D': '0001101',
                   '!A': '0110001', '-D': '0001111', '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111',
                   'D-1': '0001110', 'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D':'0000111',
                   'D&A': '0000000', 'D|A': '0010101', 'M': '1110000', '!M': '1110001', '-M': '1110011',
                   'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011', 'M-D': '1000111',
                   'D&M': '1000000', 'D|M': '1010101','!D&A' :'0010000','D&!A' :'0000100','!D&!A' :'0010100'
                    ,'!(D&A)' :'0000001','!(!D&A)' :'0010001' ,'!(D&!A)' :'0000101','!(!D&!A)' :'0010101'
                    ,'!D|A' :'0000101','D|!A' :'0010001','!D|!A' :'0000001','!(D|A)' :'0010100' ,'!(!D|A)' :'0000100' 
                    ,'!(D|!A)' :'0010000','!(!D|!A)' :'0000000','!D&M' :'1010000','D&!M' :'1000100' ,'!D&!M' :'1010100'
                    ,'!(D&M)' :'1000001','!(!D&M)' :'1010001','!(D&!M)' :'1000101','!(!D&!M)' :'1010101' 
                    ,'!D|M' :'1000101','D|!M' :'1010001','!D|!M' :'1000001','!(D|M)' :'1010100','!(!D|M)' :'1000100'
                    ,'!(D|!M)' :'1010000','!(!D|!M)' :'1000000',
                    "X00":"0000000","X01":"0000001","X02":"0000010","X03":"0000011","X04":"0000100","X05":"0000101",
                    "X06":"0000110","X07":"0000111","X08":"0001000","X09":"0001001","X0A":"0001010","X0B":"0001011",
                    "X0C":"0001100","X0D":"0001101","X0E":"0001110","X0F":"0001111","X10":"0010000","X11":"0010001",
                    "X12":"0010010","X13":"0010011","X14":"0010100","X15":"0010101","X16":"0010110","X17":"0010111",
                    "X18":"0011000","X19":"0011001","X1A":"0011010","X1B":"0011011","X1C":"0011100","X1D":"0011101",
                    "X1E":"0011110","X1F":"0011111","X20":"0100000","X21":"0100001","X22":"0100010","X23":"0100011",
                    "X24":"0100100","X25":"0100101","X26":"0100110","X27":"0100111","X28":"0101000","X29":"0101001",
                    "X2A":"0101010","X2B":"0101011","X2C":"0101100","X2D":"0101101","X2E":"0101110","X2F":"0101111",
                    "X30":"0110000","X31":"0110001","X32":"0110010","X33":"0110011","X34":"0110100","X35":"0110101",
                    "X36":"0110110","X37":"0110111","X38":"0111000","X39":"0111001","X3A":"0111010","X3B":"0111011",
                    "X3C":"0111100","X3D":"0111101","X3E":"0111110","X3F":"0111111","X40":"1000000","X41":"1000001",
                    "X42":"1000010","X43":"1000011","X44":"1000100","X45":"1000101","X46":"1000110","X47":"1000111",
                    "X48":"1001000","X49":"1001001","X4A":"1001010","X4B":"1001011","X4C":"1001100","X4D":"1001101",
                    "X4E":"1001110","X4F":"1001111","X50":"1010000","X51":"1010001","X52":"1010010","X53":"1010011",
                    "X54":"1010100","X55":"1010101","X56":"1010110","X57":"1010111","X58":"1011000","X59":"1011001",
                    "X5A":"1011010","X5B":"1011011","X5C":"1011100","X5D":"1011101","X5E":"1011110","X5F":"1011111",
                    "X60":"1100000","X61":"1100001","X62":"1100010","X63":"1100011","X64":"1100100","X65":"1100101",
                    "X66":"1100110","X67":"1100111","X68":"1101000","X69":"1101001","X6A":"1101010","X6B":"1101011",
                    "X6C":"1101100","X6D":"1101101","X6E":"1101110","X6F":"1101111","X70":"1110000","X71":"1110001",
                    "X72":"1110010","X73":"1110011","X74":"1110100","X75":"1110101","X76":"1110110","X77":"1110111",
                    "X78":"1111000","X79":"1111001","X7A":"1111010","X7B":"1111011","X7C":"1111100","X7D":"1111101",
                    "X7E":"1111110","X7F":"1111111"}

    def __init__(self):
        pass

    def _bits(self, n):
        """
        Convert an integer number to a binary string. Uses the built-in "bin()" method.
        :param n: Number.
        :return: Binary string
        """
        return bin(int(n))[2:]

    def gen_a_instruction(self, address_value):
        """
        Generates an A-Instruction from a specified address_value.
        :param address_value: Value of address in decimal.
        :return: A-Instruction in binary (String).
        """
        return '0' + self._bits(address_value).zfill(15)

    def gen_c_instruction(self, dest, comp, jump):
        """
        Generates an A-Instruction from a specified address_value.
        :param dest: 'dest' part of the instruction (string).
        :param comp: 'comp' part of the instruction (string).
        :param jump: 'jmp' part of the instruction (string).
        :return: C-Instruction in binary (string).
        """
        return '111' + self.comp(comp) + self.dest(dest) + self.jump(jump)

    def dest(self, d):
        """
        Generates the corresponding binary code for the given 'dest' instruction part.
        """
        return self._bits(self._dest_codes.index(d)).zfill(3)

    def comp(self, c):
        """
        Generates the corresponding binary code for the given 'comp' instruction part.
        """
        #print(c)
        return self._comp_codes[c]

    def jump(self, j):
        """
        Generates the corresponding binary code for the given 'jmp' instruction part.
        """
        return self._bits(self._jump_codes.index(j)).zfill(3)

