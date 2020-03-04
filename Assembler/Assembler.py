#!/usr/bin/env python3

import sys
import Code
import Parser
import SymbolTable


class Assembler:
    """
    Reads Progam.asm source file and creates a new file Program.hack which has the assembled machine code as a text file.

    The Assembly is implemented as two stages or two passes. The first pass scans the whole program and registers
    symbols in the symbol table. The second pass scans the whole program again substituting the symbols with their
    respective addresses in the symbol table, in addition to generating binary machine code and writing the resulting
    assembled machine code to a new file.

    Usage: python Assembler.py Program.asm
    """
    def __init__(self):
        self.symbol_address = 16
        self.symbols_table = SymbolTable.SymbolTable()
        self.wasError = False
        self.labelTable = SymbolTable.LabelTable()
        self.varTable = SymbolTable.VarTable()
        self.equTable = SymbolTable.EQUTable()


    @staticmethod
    def get_hack_file(asm_file):
        """
        Suggests a file name for the Hack Machine Code source file.
        :param asm_file: Program source code file written in Hack Assembly Language.
        :return: String.
        """
        if asm_file.endswith('.asm'):
            return asm_file.replace('.asm', '.hack')
        else:
            return asm_file + '.hack'

    @staticmethod
    def get_export_file(asm_file):
        if asm_file.endswith('.asm'):
            return asm_file.replace('.asm', 'export_table.txt')
        else:
            return asm_file + 'export_table.txt'

    def _get_address(self, symbol,line):
        """
        Helper method. Looks-up the address of a symbol (decimal value, label or variable).
        :param symbol: Symbol or Value.
        :return: Address.
        """
        if symbol.isdigit():
            return symbol
        else:
            if not self.symbols_table.contains(symbol):
                self.symbols_table.add_entry(symbol, self.symbol_address)
                self.varTable.add(symbol, line+1)
                self.symbol_address += 1
            else:
                self.varTable.add(symbol, line+1)
            return self.symbols_table.get_address(symbol)

    def pass_1(self, file):
        """
        First compilation pass: Determine memory locations of label definitions: (LABEL).
        :param file:
        :return:
        """
        parser = Parser.Parser(file)
        curr_address = 0
        while parser.has_more_instructions():
            parser.advance()
            inst_type = parser.instruction_type
            if inst_type in [parser.A_INSTRUCTION, parser.C_INSTRUCTION]:
                curr_address = curr_address + 1
            elif inst_type == parser.L_INSTRUCTION:
                if self.symbols_table.contains(parser.symbol):
                    print("Error at line:"+ str(parser.lineNumber)+"\nTheres already a label with name --->"+parser.symbol)
                    self.wasError = True
                else:
                    self.symbols_table.add_entry(parser.symbol, curr_address)
                    self.labelTable.add(parser.symbol, curr_address)
            elif inst_type == parser.EQU_INSTRUCTION:
                self.symbols_table.add_entry(parser.symbol, parser._value)
                self.equTable.add(parser.symbol, curr_address)
        
        self.wasError = parser.wasError
            
    def pass_2(self, asm_file, hack_file):
        """
        Second compilation pass: Generate hack machine code and write results to output file.
        :param asm_file: The program source code file, written in Hack Asembly Language.
        :param hack_file: Output file to write Hack Machine Code output to.
        :return: None.
        """
        lineNum = 0
        if(not self.wasError):
            parser = Parser.Parser(asm_file)
            with open(hack_file, 'w', encoding='utf-8') as hack_file:
                code = Code.Code()
                while parser.has_more_instructions():
                    parser.advance()
                    inst_type = parser.instruction_type
                    if inst_type == parser.A_INSTRUCTION:
                        hack_file.write(code.gen_a_instruction(self._get_address(parser.symbol,lineNum)) + '\n')
                    elif inst_type == parser.C_INSTRUCTION:
                        hack_file.write(code.gen_c_instruction(parser.dest, parser.comp, parser.jmp) + '\n')
                    elif inst_type == parser.L_INSTRUCTION:
                        pass
                    lineNum = lineNum + 1
            hack_file.close()

    def print_symbol_table(self, table,export_file):
        #prints symbol table
        if(table):
            with open(export_file, 'w', encoding='utf-8') as export_file:
                export_file.write("---Symbol Table (untouched)---\n")
                export_file.write("Symbol,Address\n")
                for i in self.symbols_table:
                    export_file.write(i + "," + str(self.symbols_table[i]) + '\n')
                
                export_file.write("---RAM---\n")        
                export_file.write("Symbol, Address, Last Line Changed (Starting at 1)\n")
                for i in self.symbols_table:
                    
                    if i in self.varTable:
                        line = self.varTable[i]
                    else:
                        line = ''

                    if i not in self.labelTable and i not in self.equTable:    
                        export_file.write(i + "," + str(self.symbols_table[i])+","+str(line) + '\n')
                    
                    
                        
                     #   for i in self.varTable:
                      #      export_file.write(i + ":" + str(self.varTable[i]) + '\n')
                export_file.write("---ROM---\n")
                export_file.write("Symbol, Address, Last Line Changed (Starting at 1)\n")
                for i in self.labelTable:
                    export_file.write(i + "," + str(self.symbols_table[i])+ "," +str(self.labelTable[i]) + '\n')
                     #   export_file.write("---EQU---\n")
                      #  for i in self.equTable:
                       #     export_file.write(i + ":" + str(self.equTable[i]) + '\n')
                export_file.write("---EQU---\n")
                export_file.write("Symbol, Address, Last Line Changed (Starting at 1)\n")
                for i in self.equTable:
                    export_file.write(i + "," + str(self.symbols_table[i])+ "," +str(self.equTable[i]) + '\n')


            export_file.close()
            print('Exported Symbol Table')
                


    def assemble(self, file):
        """
        The main method. Drives the assembly process.
        :param file: Program source code file, written in the Hack Assembly Language.
        :return: None.
        """
        self.pass_1(file)
        self.pass_2(file, self.get_hack_file(file))
        self.print_symbol_table(print_table,self.get_export_file(file))



if __name__ == '__main__':
    print("All credit to Copyright (c) 2016 Ahmad Alhour for the source code, extended functionality was implemented by me (Thomas McDonald)")
    if len(sys.argv) == 3:
        if sys.argv[2] == "-export":
            print("Export Symbol Table Enabeled")
            print_table = True
            asm_file = sys.argv[1]
        else:    
            print("Usage: python Assembler.py Program.asm -export(optional)")
    elif len(sys.argv) != 2:
        print("Usage: python Assembler.py Program.asm -export(optional)")
    else:
        asm_file = sys.argv[1]
        print_table = False
    print("Assembling...")
    hack_assembler = Assembler()
    hack_assembler.assemble(asm_file)
    if hack_assembler.wasError:
        print("Did Not Assemble Due to Errors")
    else:
        print("Assembled Successfully")

