#!/usr/bin/env python3

import Lex
import Code 

class Parser:
    """
    Parses the assembly program by looking ahead one or two tokens to determine the type of instruction. This is very
    naive and dead simple, it assumes there are no errors in the program source code and no invalid instructions are used.
    TODO: Exception handling.
    TODO: Validate the program rules for invalid instructions.
    TODO: A descent parsing algorithm, i.e. recursive-descent parsing.
    """
    ###
    # Types of Instructions as integer constants
    A_INSTRUCTION = 0   # Addressing Instruction.
    C_INSTRUCTION = 1   # Computation Instruction.
    L_INSTRUCTION = 2   # Label-Declaration pseudo-Instruction.

    def __init__(self, file):
        self.lexer = Lex.Lex(file)
        self._init_instruction_info()
        self.lineNumber = 0
        self.wasError = False

    def _init_instruction_info(self):
        """
        Helper method. Initializes the instruction data stores.
        """
        self._instruction_type = -1
        self._symbol = ''
        self._dest = ''
        self._comp = ''
        self._jmp = ''

    def _a_instruction(self):
        """
        Addressing Instruction. Possible structures:
          * @number, examples: @21, @256
          * @symbol, examples: @i, @n, @LOOP, @END; where i, n could be variables, where LOOP and END could be labels
                               previously declared with an L-Instruction.
        """
        self._instruction_type = Parser.A_INSTRUCTION
        tok_type, self._symbol = self.lexer.next_token()

    def _l_instruction(self):
        """
        Symbol Declaration instruction. Symbolic syntax: (LABEL_NAME), where LABEL_NAME is any desired name for the
        label. Example: (LOOP), (END).
        """
        self._instruction_type = Parser.L_INSTRUCTION
        tok_type, self._symbol = self.lexer.next_token()

    def _c_instruction(self, token, value):
        """
        Computation instruction. Possible structures:
          * dest=comp;jump      the full c-instruction case
          * dest=comp           c-instruction with no JUMP part
          * comp;jump           c-instruction with no DEST part
          * comp                c-instruction with only a COMP part
        """
        self._instruction_type = Parser.C_INSTRUCTION
        comp_tok, comp_val = self._get_dest(token, value)
        self._get_comp(comp_tok, comp_val)
        self._get_jump()

    def _get_dest(self, token, value):
        """
        Gets the 'dest' part of the instruction, if any.
        :return: First token of the 'comp' part.
        """
        tok2, val2 = self.lexer.peek_token()
        if tok2 == Lex.OPERATION and val2 == '=':
            self.lexer.next_token()
            self._dest = value
            comp_tok, comp_val = self.lexer.next_token()
        else:
            comp_tok, comp_val = token, value
        return comp_tok, comp_val

    def _get_comp(self, token, value):
        """
        Gets the 'comp' part of the instruction (mandatory).
        """
        if token == Lex.OPERATION and (value == '-' or value == '!'):
            tok2, val2 = self.lexer.next_token()
            self._comp = value + val2
        elif token == Lex.NUMBER or token == Lex.SYMBOL:
            self._comp = value
            tok2, val2 = self.lexer.peek_token()
            if tok2 == Lex.OPERATION and val2 != ';':
                self.lexer.next_token()
                tok3, val3 = self.lexer.next_token()
                self._comp += val2+val3

    def _get_jump(self):
        """
        Gets the 'jump' part of the instruction, if exists.
        """
        token, value = self.lexer.next_token()
        if token == Lex.OPERATION and value == ';':
            jump_tok, jump_val = self.lexer.next_token()
            self._jmp = jump_val

    @property
    def instruction_type(self):
        """
        The extracted instruction type.
        """
        return self._instruction_type

    @property
    def symbol(self):
        """
        The extracted Symbol from instruction.
        """
        return self._symbol

    @property
    def dest(self):
        """
        The extracted 'dest' part of instruction.
        """
        return self._dest

    @property
    def comp(self):
        """
        The extracted 'comp' part of instruction.
        """
        return self._comp

    @property
    def jmp(self):
        """
        The extracted 'jmp' part of instruction.
        """
        return self._jmp

    def has_more_instructions(self):
        return self.lexer.has_more_instructions()

    def printLinePretty(self, errorLine):
        returnLine = ''
        for i in errorLine:
            returnLine = returnLine + i[1]

        return returnLine


    def advance(self):
        """
        Gets the next instruction (entire line). Each instruction reside on a physical line.

        Error Checking added for first pass through
        """
        self._init_instruction_info()
        self.lineNumber = self.lineNumber+1
        self.lexer.next_instruction()
        line = self.lexer.curr_instr_line
        token, val = self.lexer.curr_token
    
        ##debug
        print(line)

        #Check if A type is valid
        if line[0][1] == '@':
            if len(line) == 1:
                print("Error at line number: " + str(self.lineNumber) +"\nExpected something after \'@\' --->" +self.printLinePretty(line))
                self.wasError = True
            
            if len(line) > 2:
                print("Error at line number: " + str(self.lineNumber) +"\nToo Many Arguments after \'@\' --->" +self.printLinePretty(line))
                self.wasError = True    

            if line[1][0] == 1:
                if int(line[1][1]) < 0 or int(line[1][1]) >= 32767:
                    print("Error at line number: " + str(self.lineNumber) +"\nNumber is not supported --->" +self.printLinePretty(line))
                    self.wasError = True

            if line[1][0] != 1 and line[1][0] != 2: 
                print("Error at line number: " + str(self.lineNumber) +"\nInvalid Symbol --->" +self.printLinePretty(line))
                self.wasError = True

        #Check if L Type is Valid
        elif line[0][1] == '(':
            if len(line) != 3:
                print("Error at line number: " + str(self.lineNumber) +"\nInvalid Number of Arguments for Label --->" +self.printLinePretty(line))
                self.wasError = True

            if line[1][0] != 2:
                print("Error at line number: " + str(self.lineNumber) +"\nInvalid Label Name --->" +self.printLinePretty(line))
                self.wasError = True
      
            if line[2][1] != ')':
                print("Error at line number: " + str(self.lineNumber) +"\nInvalid Label, Are you missing \')\'? --->" +self.printLinePretty(line))
                self.wasError = True
        


        #Check if C Type is Valid 
        #starts with symbol
        elif line[0][0] == Lex.SYMBOL and line[0][1] not in Code.Code._dest_codes or line[0][0] == Lex.NUMBER and line[0][1] != '0':
            print("Error at line number: " + str(self.lineNumber) +"\nInvalid Destination --->" +self.printLinePretty(line))
            self.wasError = True
        elif line[0][0] == Lex.SYMBOL and line[0][1] in Code.Code._dest_codes:
            if line[1][0] == Lex.OPERATION and line[1][1] == '=':
                eqPassed = False
                destPassed = False
                checkComp = ''
                checkDest = ''
                for temp in line:
                    if eqPassed:
                        if destPassed:
                            checkDest = checkDest + temp[1]
                        else:
                            if temp[1] != ';':
                                checkComp = checkComp + temp[1]
                            else:
                                destPassed = True
                    elif temp[1] == '=':
                        eqPassed = True
                    else:
                        pass

                if checkComp not in Code.Code._comp_codes:
                    print("Error at line number: " + str(self.lineNumber) +"\nInvalid Computation --->" +self.printLinePretty(line))
                    self.wasError = True
                
                elif checkDest not in Code.Code._dest_codes:
                    print("Error at line number: " + str(self.lineNumber) +"\nInvalid Destination after ; --->" +self.printLinePretty(line))
                    self.wasError = True
            elif line[1][1] != ';':
                print("Error at line number: " + str(self.lineNumber) +"\nInvalid operation after destination --->" +self.printLinePretty(line))
                self.wasError = True

        #starts with number
        elif line[0][1] == '0':
            if(line[1][1] != ';'):
                print("Error at line number: " + str(self.lineNumber) +"\nInvalid Command, expected ; --->" +self.printLinePretty(line))
                self.wasError = True
            else:
                if line[2][1] not in Code.Code._jump_codes:
                    print("Error at line number: " + str(self.lineNumber) +"\nInvalid Command, expected ; --->" +self.printLinePretty(line))
                    self.wasError = True
        elif line[0][0] == Lex.OPERATION:
            if line[0][1] != ';':
                print("Error at line number: " + str(self.lineNumber) +"\nInvalid statement --->" +self.printLinePretty(line))
                self.wasError = True
            elif line[1][1] not in Code.Code._jump_codes:
                print("Error at line number: " + str(self.lineNumber) +"\nInvalid Command, expected ; --->" +self.printLinePretty(line))
                self.wasError = True
            elif len(line) > 2:
                print("Error at line number: " + str(self.lineNumber) +"\nToo many arguments after ; --->" +self.printLinePretty(line))
                self.wasError = True


        #line is good
        if token == Lex.OPERATION and val == '@':
            self._a_instruction()
        elif token == Lex.OPERATION and val == '(':
            self._l_instruction()
        else:
            self._c_instruction(token, val)
        #else:
            ##line was not good for some unfound reaseon
            #print("Error at line number: " + str(self.lineNumber) +"Unchecked Reason --->" +self.printLinePretty(line))
            #self.wasError = True

