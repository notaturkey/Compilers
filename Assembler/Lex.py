#!/usr/bin/env python3

import re
import copy

# Number constant i.e. '123'
NUMBER = 1

# Symbol constant i.e. 'LOOP', 'END'
SYMBOL = 2

# Operation constant i.e. = ; ( ) @ + - & | !
OPERATION = 3

# Error constant
ERROR = 4


class Lex(object):
    """
    A simple lexer that uses regular expressions to detect Numbers, Symbols (Labels) and Operations. It loads the whole
    program (source code text file .asm) into memory for scanning.
    TODO: Exception handling.
    TODO: Error checking on the tokens.
    """
    # Internal regular expression patterns
    _hex_re_comp = re.compile(r'0[xX][0-9a-fA-F]+')
    _binary_re_comp = re.compile(r'0[bB][01]+')
    _hex_re = r'0[xX][0-9a-fA-F]+'
    _binary_re = r'0[bB][01]+'
    _number_re = r'\d+' + '|'+ _hex_re+ '|' + _binary_re
    _symbol_start_re = r'\w_.$:'
    _symbol_re = '[' + _symbol_start_re + '][' + _symbol_start_re + r'\d]*'
    _operation_re = r'[=;()@+\-&|!]'
    _word = re.compile(_number_re + '|' + _symbol_re + '|' + _operation_re)
    _comment = re.compile('//.*$')

    def __init__(self, asm_file_name):
        file = open(asm_file_name, 'r')
        self.lineNum = 0
        self._lines = file.read()
        self._tokens = self._tokenize(self._lines.split('\n'))
        # List of tokens for current instruction
        self.curr_instr_tokens = []
        self.curr_instr_line = []
        # Current token of current instruction
        self.curr_token = (ERROR, 0)

    def _is_operation(self, word):
        return self._is_match(self._operation_re, word)

    def _is_number(self, word):
        return self._is_match(self._number_re, word) or self._is_match(self._hex_re, word) or self._is_match(self._binary_re, word)

    def _is_symbol(self, word):
        return self._is_match(self._symbol_re, word)

    def _is_match(self, re_str, word):
        return re.match(re_str, word) is not None

    def _tokenize(self, lines):
        this = [t for t in [self._tokenize_line(l) for l in lines]]
        count = 0
        for i in this:
            if not i:
                this[count] = ["BLANK LINE"]
            count = count +1
        #print(this)
        return this

    def _tokenize_line(self, line):
        this = [self._token(word) for word in self._split(self._remove_comment(line))]
        #print(this)
        return this

    def _remove_comment(self, line):
        return self._comment.sub('', line)

    def _split(self, line):
        #print(self._word.findall(line))
        #split_line = (self._word.findall(line))
        #if split_line:
        #    print(split_line[0])
        if len(line.split('@')) != 1:
            if self._binary_re_comp.match(line.split('@')[1]) is not None:
                return ['@',(self._binary_re_comp.findall(line.split('@')[1])[0])]
            if self._hex_re_comp.match(line.split('@')[1]) is not None:
                return ['@',(self._hex_re_comp.findall(line.split('@')[1])[0])]
        return self._word.findall(line)

    def _token(self, word):
        if self._is_number(word):
            if self._binary_re_comp.match(word):
                word = str(int( re.split(r'[bB]',word)[1] , 2))
                return NUMBER, word
            if self._hex_re_comp.match(word):
                word = str(int( re.split(r'[xX]',word)[1] , 16))
                return NUMBER, word
            return NUMBER, word
        elif self._is_symbol(word):
            return SYMBOL, word
        elif self._is_operation(word):
            return OPERATION, word
        else:
            return ERROR, word

    def has_more_instructions(self):
        return self._tokens != []

    def next_instruction(self):
        self.curr_instr_line = self._tokens.pop(0)
        self.lineNum = self.lineNum + 1
        #print(self.curr_instr_line)
        if self.curr_instr_line[0] == 'BLANK LINE':
            return self.next_instruction

        self.curr_instr_tokens = copy.copy(self.curr_instr_line)
        self.next_token()
        return self.curr_instr_tokens

    def has_next_token(self):
        return self.curr_instr_tokens != []

    def next_token(self):
        if self.has_next_token():
            self.curr_token = self.curr_instr_tokens.pop(0)
        else:
            self.curr_token = ERROR, 0
        return self.curr_token

    def peek_token(self):
        if self.has_next_token():
            return self.curr_instr_tokens[0]
        else:
            return ERROR, 0

