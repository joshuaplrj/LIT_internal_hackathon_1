"""
MiniRust Lexer - Tokenizes MiniRust source code
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
import re

class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    CHAR = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Keywords
    FN = auto()
    LET = auto()
    MUT = auto()
    CONST = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    RETURN = auto()
    STRUCT = auto()
    ENUM = auto()
    IMPL = auto()
    TRAIT = auto()
    PUB = auto()
    USE = auto()
    MOD = auto()
    SELF = auto()
    TRUE = auto()
    FALSE = auto()
    LOOP = auto()
    BREAK = auto()
    CONTINUE = auto()
    MATCH = auto()
    WHERE = auto()
    ASYNC = auto()
    AWAIT = auto()
    
    # Types
    I8 = auto()
    I16 = auto()
    I32 = auto()
    I64 = auto()
    U8 = auto()
    U16 = auto()
    U32 = auto()
    U64 = auto()
    F32 = auto()
    F64 = auto()
    BOOL_TYPE = auto()
    CHAR_TYPE = auto()
    STR = auto()
    STRING_TYPE = auto()
    VEC = auto()
    OPTION = auto()
    RESULT = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    AMPERSAND = auto()
    PIPE = auto()
    CARET = auto()
    TILDE = auto()
    NOT = auto()
    
    # Assignment
    EQUALS = auto()
    PLUS_EQUALS = auto()
    MINUS_EQUALS = auto()
    STAR_EQUALS = auto()
    SLASH_EQUALS = auto()
    
    # Comparison
    EQUAL_EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    
    # Logical
    AND = auto()
    OR = auto()
    
    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    COLON_COLON = auto()
    DOT = auto()
    DOT_DOT = auto()
    ARROW = auto()
    FAT_ARROW = auto()
    UNDERSCORE = auto()
    QUESTION = auto()
    
    # Special
    EOF = auto()
    NEWLINE = auto()
    COMMENT = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"

class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at {line}:{column}: {message}")

class Lexer:
    KEYWORDS = {
        'fn': TokenType.FN,
        'let': TokenType.LET,
        'mut': TokenType.MUT,
        'const': TokenType.CONST,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'return': TokenType.RETURN,
        'struct': TokenType.STRUCT,
        'enum': TokenType.ENUM,
        'impl': TokenType.IMPL,
        'trait': TokenType.TRAIT,
        'pub': TokenType.PUB,
        'use': TokenType.USE,
        'mod': TokenType.MOD,
        'self': TokenType.SELF,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'loop': TokenType.LOOP,
        'break': TokenType.BREAK,
        'continue': TokenType.CONTINUE,
        'match': TokenType.MATCH,
        'where': TokenType.WHERE,
        'async': TokenType.ASYNC,
        'await': TokenType.AWAIT,
        'i8': TokenType.I8,
        'i16': TokenType.I16,
        'i32': TokenType.I32,
        'i64': TokenType.I64,
        'u8': TokenType.U8,
        'u16': TokenType.U16,
        'u32': TokenType.U32,
        'u64': TokenType.U64,
        'f32': TokenType.F32,
        'f64': TokenType.F64,
        'bool': TokenType.BOOL_TYPE,
        'char': TokenType.CHAR_TYPE,
        'str': TokenType.STR,
        'String': TokenType.STRING_TYPE,
        'Vec': TokenType.VEC,
        'Option': TokenType.OPTION,
        'Result': TokenType.RESULT,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def peek(self, offset: int = 0) -> Optional[str]:
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def advance(self) -> str:
        char = self.source[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in ' \t\r':
            self.advance()
    
    def skip_line_comment(self):
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self.advance()
    
    def skip_block_comment(self):
        start_line, start_col = self.line, self.column
        self.advance()  # skip /
        self.advance()  # skip *
        depth = 1
        
        while self.pos < len(self.source) and depth > 0:
            if self.pos + 1 < len(self.source):
                if self.source[self.pos:self.pos+2] == '/*':
                    depth += 1
                    self.advance()
                    self.advance()
                elif self.source[self.pos:self.pos+2] == '*/':
                    depth -= 1
                    self.advance()
                    self.advance()
                else:
                    self.advance()
            else:
                self.advance()
        
        if depth > 0:
            raise LexerError("Unterminated block comment", start_line, start_col)
    
    def read_string(self, quote: str) -> Token:
        start_line, start_col = self.line, self.column
        self.advance()  # skip opening quote
        value = ""
        
        while self.pos < len(self.source) and self.source[self.pos] != quote:
            if self.source[self.pos] == '\\':
                self.advance()
                if self.pos >= len(self.source):
                    raise LexerError("Unterminated string", start_line, start_col)
                escape = self.advance()
                escape_map = {'n': '\n', 't': '\t', '\\': '\\', '"': '"', "'": "'", '0': '\0'}
                value += escape_map.get(escape, '\\' + escape)
            else:
                value += self.advance()
        
        if self.pos >= len(self.source):
            raise LexerError("Unterminated string", start_line, start_col)
        
        self.advance()  # skip closing quote
        return Token(TokenType.STRING, value, start_line, start_col)
    
    def read_number(self) -> Token:
        start_line, start_col = self.line, self.column
        value = ""
        is_float = False
        
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '_'):
            if self.source[self.pos] != '_':
                value += self.source[self.pos]
            self.advance()
        
        # Check for decimal point
        if self.pos < len(self.source) and self.source[self.pos] == '.':
            if self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit():
                is_float = True
                value += self.advance()  # add dot
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    value += self.advance()
        
        # Check for exponent
        if self.pos < len(self.source) and self.source[self.pos] in 'eE':
            is_float = True
            value += self.advance()
            if self.pos < len(self.source) and self.source[self.pos] in '+-':
                value += self.advance()
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                value += self.advance()
        
        # Check for type suffix
        if self.pos < len(self.source) and self.source[self.pos] in 'iuf':
            suffix = ""
            while self.pos < len(self.source) and self.source[self.pos].isalnum():
                suffix += self.advance()
            value += suffix
        
        token_type = TokenType.FLOAT if is_float else TokenType.INTEGER
        return Token(token_type, value, start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line, start_col = self.line, self.column
        value = ""
        
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            value += self.advance()
        
        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            if self.pos >= len(self.source):
                break
            
            char = self.source[self.pos]
            start_line, start_col = self.line, self.column
            
            # Newlines
            if char == '\n':
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\\n', start_line, start_col))
                continue
            
            # Comments
            if char == '/':
                if self.peek(1) == '/':
                    self.skip_line_comment()
                    continue
                elif self.peek(1) == '*':
                    self.skip_block_comment()
                    continue
            
            # Strings
            if char == '"':
                self.tokens.append(self.read_string('"'))
                continue
            
            if char == "'":
                if self.peek(1) and self.peek(2) == "'":
                    self.advance()
                    char_val = self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.CHAR, char_val, start_line, start_col))
                else:
                    self.tokens.append(self.read_string("'"))
                continue
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Operators and punctuation
            self.advance()
            
            two_char = char + (self.peek() or '')
            
            if two_char == '==':
                self.advance()
                self.tokens.append(Token(TokenType.EQUAL_EQUAL, '==', start_line, start_col))
            elif two_char == '!=':
                self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', start_line, start_col))
            elif two_char == '<=':
                self.advance()
                self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', start_line, start_col))
            elif two_char == '>=':
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', start_line, start_col))
            elif two_char == '&&':
                self.advance()
                self.tokens.append(Token(TokenType.AND, '&&', start_line, start_col))
            elif two_char == '||':
                self.advance()
                self.tokens.append(Token(TokenType.OR, '||', start_line, start_col))
            elif two_char == '::':
                self.advance()
                self.tokens.append(Token(TokenType.COLON_COLON, '::', start_line, start_col))
            elif two_char == '->':
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_col))
            elif two_char == '=>':
                self.advance()
                self.tokens.append(Token(TokenType.FAT_ARROW, '=>', start_line, start_col))
            elif two_char == '..':
                self.advance()
                self.tokens.append(Token(TokenType.DOT_DOT, '..', start_line, start_col))
            elif two_char == '+=':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS_EQUALS, '+=', start_line, start_col))
            elif two_char == '-=':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS_EQUALS, '-=', start_line, start_col))
            elif two_char == '*=':
                self.advance()
                self.tokens.append(Token(TokenType.STAR_EQUALS, '*=', start_line, start_col))
            elif two_char == '/=':
                self.advance()
                self.tokens.append(Token(TokenType.SLASH_EQUALS, '/=', start_line, start_col))
            else:
                single_tokens = {
                    '+': TokenType.PLUS,
                    '-': TokenType.MINUS,
                    '*': TokenType.STAR,
                    '/': TokenType.SLASH,
                    '%': TokenType.PERCENT,
                    '&': TokenType.AMPERSAND,
                    '|': TokenType.PIPE,
                    '^': TokenType.CARET,
                    '~': TokenType.TILDE,
                    '!': TokenType.NOT,
                    '=': TokenType.EQUALS,
                    '<': TokenType.LESS_THAN,
                    '>': TokenType.GREATER_THAN,
                    '(': TokenType.LPAREN,
                    ')': TokenType.RPAREN,
                    '{': TokenType.LBRACE,
                    '}': TokenType.RBRACE,
                    '[': TokenType.LBRACKET,
                    ']': TokenType.RBRACKET,
                    ',': TokenType.COMMA,
                    ';': TokenType.SEMICOLON,
                    ':': TokenType.COLON,
                    '.': TokenType.DOT,
                    '_': TokenType.UNDERSCORE,
                    '?': TokenType.QUESTION,
                }
                
                if char in single_tokens:
                    self.tokens.append(Token(single_tokens[char], char, start_line, start_col))
                else:
                    raise LexerError(f"Unexpected character: '{char}'", start_line, start_col)
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens

def tokenize(source: str) -> List[Token]:
    """Convenience function to tokenize source code"""
    lexer = Lexer(source)
    return lexer.tokenize()

if __name__ == '__main__':
    # Test the lexer
    test_code = '''
fn main() {
    let mut x: i32 = 42;
    let y = x + 10;
    if y > 50 {
        println!("Hello, MiniRust!");
    }
}
'''
    
    tokens = tokenize(test_code)
    for token in tokens:
        print(token)
