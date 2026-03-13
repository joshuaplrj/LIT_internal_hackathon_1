"""
MiniRust Parser - Parses tokens into AST
Contains 5 bugs in type inference (BUG-TI-1 through BUG-TI-5)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum, auto
from .lexer import Token, TokenType, Lexer

# AST Node Types

class ASTNodeType(Enum):
    PROGRAM = auto()
    FUNCTION = auto()
    STRUCT = auto()
    ENUM = auto()
    IMPL = auto()
    TRAIT = auto()
    BLOCK = auto()
    LET_BINDING = auto()
    IF_EXPR = auto()
    WHILE_EXPR = auto()
    FOR_EXPR = auto()
    LOOP_EXPR = auto()
    MATCH_EXPR = auto()
    RETURN_EXPR = auto()
    BREAK_EXPR = auto()
    CONTINUE_EXPR = auto()
    BINARY_EXPR = auto()
    UNARY_EXPR = auto()
    CALL_EXPR = auto()
    INDEX_EXPR = auto()
    FIELD_EXPR = auto()
    METHOD_CALL = auto()
    STRUCT_LITERAL = auto()
    ARRAY_LITERAL = auto()
    TUPLE_LITERAL = auto()
    CLOSURE = auto()
    PATH_EXPR = auto()
    LITERAL = auto()
    TYPE = auto()

@dataclass
class ASTNode:
    node_type: ASTNodeType
    children: List['ASTNode'] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    line: int = 0
    column: int = 0

@dataclass
class Type:
    name: str
    is_mutable: bool = False
    is_reference: bool = False
    lifetime: Optional[str] = None
    generic_args: List['Type'] = field(default_factory=list)
    
    def __str__(self):
        result = ""
        if self.is_reference:
            result += "&"
            if self.is_mutable:
                result += "mut "
        result += self.name
        if self.generic_args:
            result += "<" + ", ".join(str(t) for t in self.generic_args) + ">"
        return result

@dataclass
class Function:
    name: str
    params: List[Dict[str, Type]]
    return_type: Optional[Type]
    body: Optional[ASTNode]
    is_pub: bool = False
    is_async: bool = False
    generics: List[str] = field(default_factory=list)
    where_clause: Optional[List[str]] = None

@dataclass
class StructDef:
    name: str
    fields: Dict[str, Type]
    is_pub: bool = False
    generics: List[str] = field(default_factory=list)

@dataclass
class EnumDef:
    name: str
    variants: Dict[str, Optional[Type]]
    is_pub: bool = False
    generics: List[str] = field(default_factory=list)

class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at {token.line}:{token.column}: {message}")

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.functions: Dict[str, Function] = {}
        self.structs: Dict[str, StructDef] = {}
        self.enums: Dict[str, EnumDef] = {}
        self.type_inference_cache: Dict[str, Type] = {}
    
    def peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # EOF
    
    def advance(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        token = self.peek()
        if token.type != token_type:
            raise ParseError(f"Expected {token_type.name}, got {token.type.name}", token)
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        return self.peek().type in token_types
    
    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse_type(self) -> Type:
        """Parse a type annotation"""
        is_ref = False
        is_mut = False
        lifetime = None
        
        # Handle references
        if self.match(TokenType.AMPERSAND):
            self.advance()
            is_ref = True
            
            # Check for lifetime
            if self.match(TokenType.IDENTIFIER) and self.peek().value.startswith("'"):
                lifetime = self.advance().value
            
            if self.match(TokenType.MUT):
                self.advance()
                is_mut = True
        
        # Parse base type
        token = self.peek()
        
        type_tokens = {
            TokenType.I8: "i8", TokenType.I16: "i16", TokenType.I32: "i32", TokenType.I64: "i64",
            TokenType.U8: "u8", TokenType.U16: "u16", TokenType.U32: "u32", TokenType.U64: "u64",
            TokenType.F32: "f32", TokenType.F64: "f64",
            TokenType.BOOL_TYPE: "bool", TokenType.CHAR_TYPE: "char",
            TokenType.STR: "str", TokenType.STRING_TYPE: "String",
        }
        
        if token.type in type_tokens:
            self.advance()
            type_name = type_tokens[token.type]
        elif token.type == TokenType.IDENTIFIER:
            type_name = self.advance().value
        elif token.type == TokenType.SELF:
            self.advance()
            type_name = "Self"
        else:
            raise ParseError(f"Expected type, got {token.type.name}", token)
        
        # BUG-TI-1: Generic arguments not properly parsed for nested types
        # Should recursively parse generic args but doesn't
        generic_args = []
        if self.match(TokenType.LESS_THAN):
            self.advance()
            generic_args.append(self.parse_type())
            while self.match(TokenType.COMMA):
                self.advance()
                generic_args.append(self.parse_type())
            self.expect(TokenType.GREATER_THAN)
        
        return Type(type_name, is_mut, is_ref, lifetime, generic_args)
    
    def parse_function(self) -> Function:
        """Parse a function definition"""
        is_pub = False
        is_async = False
        
        if self.match(TokenType.PUB):
            self.advance()
            is_pub = True
        
        if self.match(TokenType.ASYNC):
            self.advance()
            is_async = True
        
        self.expect(TokenType.FN)
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Parse generics
        generics = []
        if self.match(TokenType.LESS_THAN):
            self.advance()
            generics.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()
                generics.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.GREATER_THAN)
        
        # Parse parameters
        self.expect(TokenType.LPAREN)
        params = []
        
        if not self.match(TokenType.RPAREN):
            param_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            param_type = self.parse_type()
            params.append({"name": param_name, "type": param_type})
            
            while self.match(TokenType.COMMA):
                self.advance()
                if self.match(TokenType.RPAREN):
                    break
                param_name = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.COLON)
                param_type = self.parse_type()
                params.append({"name": param_name, "type": param_type})
        
        self.expect(TokenType.RPAREN)
        
        # Parse return type
        return_type = None
        if self.match(TokenType.ARROW):
            self.advance()
            return_type = self.parse_type()
        
        # Parse body
        body = self.parse_block()
        
        func = Function(name, params, return_type, body, is_pub, is_async, generics)
        self.functions[name] = func
        return func
    
    def parse_struct(self) -> StructDef:
        """Parse a struct definition"""
        is_pub = False
        if self.match(TokenType.PUB):
            self.advance()
            is_pub = True
        
        self.expect(TokenType.STRUCT)
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Parse generics
        generics = []
        if self.match(TokenType.LESS_THAN):
            self.advance()
            generics.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()
                generics.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.GREATER_THAN)
        
        self.expect(TokenType.LBRACE)
        fields = {}
        
        while not self.match(TokenType.RBRACE):
            self.skip_newlines()
            if self.match(TokenType.RBRACE):
                break
            
            field_pub = False
            if self.match(TokenType.PUB):
                self.advance()
                field_pub = True
            
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            field_type = self.parse_type()
            fields[field_name] = field_type
            
            if not self.match(TokenType.RBRACE):
                self.expect(TokenType.COMMA)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        struct_def = StructDef(name, fields, is_pub, generics)
        self.structs[name] = struct_def
        return struct_def
    
    def parse_enum(self) -> EnumDef:
        """Parse an enum definition"""
        is_pub = False
        if self.match(TokenType.PUB):
            self.advance()
            is_pub = True
        
        self.expect(TokenType.ENUM)
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Parse generics
        generics = []
        if self.match(TokenType.LESS_THAN):
            self.advance()
            generics.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()
                generics.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.GREATER_THAN)
        
        self.expect(TokenType.LBRACE)
        variants = {}
        
        while not self.match(TokenType.RBRACE):
            self.skip_newlines()
            if self.match(TokenType.RBRACE):
                break
            
            variant_name = self.expect(TokenType.IDENTIFIER).value
            variant_type = None
            
            if self.match(TokenType.LPAREN):
                self.advance()
                variant_type = self.parse_type()
                self.expect(TokenType.RPAREN)
            elif self.match(TokenType.LBRACE):
                self.advance()
                # Parse struct-like variant
                while not self.match(TokenType.RBRACE):
                    self.advance()  # Skip field names for now
                self.expect(TokenType.RBRACE)
            
            variants[variant_name] = variant_type
            
            if not self.match(TokenType.RBRACE):
                self.expect(TokenType.COMMA)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        enum_def = EnumDef(name, variants, is_pub, generics)
        self.enums[name] = enum_def
        return enum_def
    
    def parse_block(self) -> ASTNode:
        """Parse a block of statements"""
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        statements = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return ASTNode(ASTNodeType.BLOCK, statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a statement"""
        self.skip_newlines()
        
        if self.match(TokenType.RBRACE, TokenType.EOF):
            return None
        
        if self.match(TokenType.LET):
            return self.parse_let_binding()
        elif self.match(TokenType.RETURN):
            return self.parse_return()
        elif self.match(TokenType.IF):
            return self.parse_if()
        elif self.match(TokenType.WHILE):
            return self.parse_while()
        elif self.match(TokenType.FOR):
            return self.parse_for()
        elif self.match(TokenType.LOOP):
            return self.parse_loop()
        elif self.match(TokenType.MATCH):
            return self.parse_match()
        elif self.match(TokenType.BREAK):
            self.advance()
            return ASTNode(ASTNodeType.BREAK_EXPR)
        elif self.match(TokenType.CONTINUE):
            self.advance()
            return ASTNode(ASTNodeType.CONTINUE_EXPR)
        else:
            return self.parse_expression()
    
    def parse_let_binding(self) -> ASTNode:
        """Parse a let binding"""
        self.expect(TokenType.LET)
        
        is_mut = False
        if self.match(TokenType.MUT):
            self.advance()
            is_mut = True
        
        name = self.expect(TokenType.IDENTIFIER).value
        
        type_annotation = None
        if self.match(TokenType.COLON):
            self.advance()
            type_annotation = self.parse_type()
        
        value = None
        if self.match(TokenType.EQUALS):
            self.advance()
            value = self.parse_expression()
        
        node = ASTNode(ASTNodeType.LET_BINDING, [value] if value else [])
        node.attributes = {"name": name, "is_mut": is_mut, "type": type_annotation}
        return node
    
    def parse_return(self) -> ASTNode:
        """Parse a return statement"""
        self.expect(TokenType.RETURN)
        value = None
        if not self.match(TokenType.SEMICOLON, TokenType.NEWLINE, TokenType.RBRACE):
            value = self.parse_expression()
        
        node = ASTNode(ASTNodeType.RETURN_EXPR, [value] if value else [])
        return node
    
    def parse_if(self) -> ASTNode:
        """Parse an if expression"""
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        then_block = self.parse_block()
        
        else_block = None
        if self.match(TokenType.ELSE):
            self.advance()
            if self.match(TokenType.IF):
                else_block = self.parse_if()
            else:
                else_block = self.parse_block()
        
        node = ASTNode(ASTNodeType.IF_EXPR, [condition, then_block])
        if else_block:
            node.children.append(else_block)
        return node
    
    def parse_while(self) -> ASTNode:
        """Parse a while loop"""
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        body = self.parse_block()
        
        return ASTNode(ASTNodeType.WHILE_EXPR, [condition, body])
    
    def parse_for(self) -> ASTNode:
        """Parse a for loop"""
        self.expect(TokenType.FOR)
        var_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        body = self.parse_block()
        
        node = ASTNode(ASTNodeType.FOR_EXPR, [iterable, body])
        node.attributes = {"var_name": var_name}
        return node
    
    def parse_loop(self) -> ASTNode:
        """Parse a loop expression"""
        self.expect(TokenType.LOOP)
        body = self.parse_block()
        return ASTNode(ASTNodeType.LOOP_EXPR, [body])
    
    def parse_match(self) -> ASTNode:
        """Parse a match expression"""
        self.expect(TokenType.MATCH)
        expr = self.parse_expression()
        self.expect(TokenType.LBRACE)
        
        arms = []
        while not self.match(TokenType.RBRACE):
            self.skip_newlines()
            if self.match(TokenType.RBRACE):
                break
            
            pattern = self.parse_expression()
            self.expect(TokenType.FAT_ARROW)
            body = self.parse_expression()
            
            arms.append(ASTNode(ASTNodeType.MATCH_EXPR, [pattern, body]))
            
            if not self.match(TokenType.RBRACE):
                self.expect(TokenType.COMMA)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        node = ASTNode(ASTNodeType.MATCH_EXPR, [expr] + arms)
        return node
    
    def parse_expression(self) -> ASTNode:
        """Parse an expression"""
        return self.parse_binary_expr()
    
    def parse_binary_expr(self, min_prec: int = 0) -> ASTNode:
        """Parse binary expression with precedence"""
        left = self.parse_unary_expr()
        
        while True:
            token = self.peek()
            prec = self.get_precedence(token.type)
            
            if prec < min_prec:
                break
            
            op = self.advance()
            right = self.parse_binary_expr(prec + 1)
            
            node = ASTNode(ASTNodeType.BINARY_EXPR, [left, right])
            node.attributes = {"operator": op.value}
            left = node
        
        return left
    
    def get_precedence(self, token_type: TokenType) -> int:
        """Get operator precedence"""
        precedences = {
            TokenType.OR: 1,
            TokenType.AND: 2,
            TokenType.EQUAL_EQUAL: 3,
            TokenType.NOT_EQUAL: 3,
            TokenType.LESS_THAN: 4,
            TokenType.GREATER_THAN: 4,
            TokenType.LESS_EQUAL: 4,
            TokenType.GREATER_EQUAL: 4,
            TokenType.PLUS: 5,
            TokenType.MINUS: 5,
            TokenType.STAR: 6,
            TokenType.SLASH: 6,
            TokenType.PERCENT: 6,
        }
        return precedences.get(token_type, 0)
    
    def parse_unary_expr(self) -> ASTNode:
        """Parse unary expression"""
        if self.match(TokenType.NOT, TokenType.MINUS, TokenType.AMPERSAND, TokenType.STAR):
            op = self.advance()
            expr = self.parse_unary_expr()
            node = ASTNode(ASTNodeType.UNARY_EXPR, [expr])
            node.attributes = {"operator": op.value}
            return node
        
        return self.parse_postfix_expr()
    
    def parse_postfix_expr(self) -> ASTNode:
        """Parse postfix expressions (calls, indexing, field access)"""
        expr = self.parse_primary_expr()
        
        while True:
            if self.match(TokenType.LPAREN):
                # Function call
                self.advance()
                args = []
                if not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        if self.match(TokenType.RPAREN):
                            break
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                
                node = ASTNode(ASTNodeType.CALL_EXPR, [expr] + args)
                expr = node
                
            elif self.match(TokenType.LBRACKET):
                # Index expression
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                
                node = ASTNode(ASTNodeType.INDEX_EXPR, [expr, index])
                expr = node
                
            elif self.match(TokenType.DOT):
                # Field access or method call
                self.advance()
                field = self.expect(TokenType.IDENTIFIER).value
                
                if self.match(TokenType.LPAREN):
                    # Method call
                    self.advance()
                    args = []
                    if not self.match(TokenType.RPAREN):
                        args.append(self.parse_expression())
                        while self.match(TokenType.COMMA):
                            self.advance()
                            if self.match(TokenType.RPAREN):
                                break
                            args.append(self.parse_expression())
                    self.expect(TokenType.RPAREN)
                    
                    node = ASTNode(ASTNodeType.METHOD_CALL, [expr] + args)
                    node.attributes = {"method": field}
                    expr = node
                else:
                    # Field access
                    node = ASTNode(ASTNodeType.FIELD_EXPR, [expr])
                    node.attributes = {"field": field}
                    expr = node
                    
            elif self.match(TokenType.QUESTION):
                # Error propagation
                self.advance()
                node = ASTNode(ASTNodeType.UNARY_EXPR, [expr])
                node.attributes = {"operator": "?"}
                expr = node
                
            else:
                break
        
        return expr
    
    def parse_primary_expr(self) -> ASTNode:
        """Parse primary expression"""
        token = self.peek()
        
        # Literals
        if token.type == TokenType.INTEGER:
            self.advance()
            node = ASTNode(ASTNodeType.LITERAL)
            node.attributes = {"value": int(token.value), "type": "int"}
            return node
        
        if token.type == TokenType.FLOAT:
            self.advance()
            node = ASTNode(ASTNodeType.LITERAL)
            node.attributes = {"value": float(token.value), "type": "float"}
            return node
        
        if token.type == TokenType.STRING:
            self.advance()
            node = ASTNode(ASTNodeType.LITERAL)
            node.attributes = {"value": token.value, "type": "string"}
            return node
        
        if token.type in (TokenType.TRUE, TokenType.FALSE):
            self.advance()
            node = ASTNode(ASTNodeType.LITERAL)
            node.attributes = {"value": token.type == TokenType.TRUE, "type": "bool"}
            return node
        
        # Identifiers and paths
        if token.type == TokenType.IDENTIFIER:
            name = self.advance().value
            
            # Check for path (e.g., std::io)
            while self.match(TokenType.COLON_COLON):
                self.advance()
                name += "::" + self.expect(TokenType.IDENTIFIER).value
            
            # Check for struct literal
            if self.match(TokenType.LBRACE):
                self.advance()
                fields = {}
                while not self.match(TokenType.RBRACE):
                    self.skip_newlines()
                    if self.match(TokenType.RBRACE):
                        break
                    
                    field_name = self.expect(TokenType.IDENTIFIER).value
                    self.expect(TokenType.COLON)
                    field_value = self.parse_expression()
                    fields[field_name] = field_value
                    
                    if not self.match(TokenType.RBRACE):
                        self.expect(TokenType.COMMA)
                    self.skip_newlines()
                
                self.expect(TokenType.RBRACE)
                
                node = ASTNode(ASTNodeType.STRUCT_LITERAL)
                node.attributes = {"struct_name": name, "fields": fields}
                return node
            
            node = ASTNode(ASTNodeType.PATH_EXPR)
            node.attributes = {"path": name}
            return node
        
        # Parenthesized expression or tuple
        if token.type == TokenType.LPAREN:
            self.advance()
            if self.match(TokenType.RPAREN):
                self.advance()
                return ASTNode(ASTNodeType.TUPLE_LITERAL)
            
            expr = self.parse_expression()
            
            if self.match(TokenType.COMMA):
                # Tuple
                elements = [expr]
                while self.match(TokenType.COMMA):
                    self.advance()
                    if self.match(TokenType.RPAREN):
                        break
                    elements.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                
                node = ASTNode(ASTNodeType.TUPLE_LITERAL, elements)
                return node
            
            self.expect(TokenType.RPAREN)
            return expr
        
        # Array literal
        if token.type == TokenType.LBRACKET:
            self.advance()
            elements = []
            
            if not self.match(TokenType.RBRACKET):
                elements.append(self.parse_expression())
                
                # Check for repeat syntax [expr; count]
                if self.match(TokenType.SEMICOLON):
                    self.advance()
                    count = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    node = ASTNode(ASTNodeType.ARRAY_LITERAL, elements + [count])
                    node.attributes = {"is_repeat": True}
                    return node
                
                while self.match(TokenType.COMMA):
                    self.advance()
                    if self.match(TokenType.RBRACKET):
                        break
                    elements.append(self.parse_expression())
            
            self.expect(TokenType.RBRACKET)
            return ASTNode(ASTNodeType.ARRAY_LITERAL, elements)
        
        # Closure
        if token.type == TokenType.PIPE:
            self.advance()
            params = []
            if not self.match(TokenType.PIPE):
                params.append(self.expect(TokenType.IDENTIFIER).value)
                while self.match(TokenType.COMMA):
                    self.advance()
                    params.append(self.expect(TokenType.IDENTIFIER).value)
            self.expect(TokenType.PIPE)
            
            body = self.parse_expression()
            
            node = ASTNode(ASTNodeType.CLOSURE, [body])
            node.attributes = {"params": params}
            return node
        
        raise ParseError(f"Unexpected token: {token.type.name}", token)
    
    def infer_type(self, node: ASTNode) -> Optional[Type]:
        """Infer the type of an expression"""
        if node.node_type == ASTNodeType.LITERAL:
            type_map = {
                "int": Type("i32"),
                "float": Type("f64"),
                "string": Type("String"),
                "bool": Type("bool"),
            }
            return type_map.get(node.attributes.get("type"))
        
        # BUG-TI-2: Type inference for binary expressions doesn't handle
        # type promotion correctly (e.g., i32 + f64 should be f64)
        if node.node_type == ASTNodeType.BINARY_EXPR:
            left_type = self.infer_type(node.children[0])
            right_type = self.infer_type(node.children[1])
            if left_type and right_type:
                # Simply returns left type without checking compatibility
                return left_type
        
        # BUG-TI-3: Function call return type inference ignores generic parameters
        if node.node_type == ASTNodeType.CALL_EXPR:
            func_name = node.children[0].attributes.get("path")
            if func_name in self.functions:
                return self.functions[func_name].return_type
        
        # BUG-TI-4: Field access type inference doesn't check if field exists
        if node.node_type == ASTNodeType.FIELD_EXPR:
            # Returns a placeholder without validating
            return Type("unknown")
        
        # BUG-TI-5: Array indexing doesn't verify the index is integer type
        if node.node_type == ASTNodeType.INDEX_EXPR:
            container_type = self.infer_type(node.children[0])
            if container_type and container_type.name in ("Vec", "Array"):
                return container_type.generic_args[0] if container_type.generic_args else Type("unknown")
        
        return None
    
    def parse(self) -> ASTNode:
        """Parse the entire program"""
        self.skip_newlines()
        
        items = []
        while not self.match(TokenType.EOF):
            if self.match(TokenType.FN):
                items.append(self.parse_function())
            elif self.match(TokenType.STRUCT):
                items.append(self.parse_struct())
            elif self.match(TokenType.ENUM):
                items.append(self.parse_enum())
            elif self.match(TokenType.PUB):
                # Could be pub fn, pub struct, etc.
                if self.peek(1).type == TokenType.FN:
                    items.append(self.parse_function())
                elif self.peek(1).type == TokenType.STRUCT:
                    items.append(self.parse_struct())
                elif self.peek(1).type == TokenType.ENUM:
                    items.append(self.parse_enum())
                else:
                    raise ParseError("Unexpected pub", self.peek())
            else:
                raise ParseError(f"Unexpected token: {self.peek().type.name}", self.peek())
            
            self.skip_newlines()
        
        return ASTNode(ASTNodeType.PROGRAM, items)

def parse(tokens: List[Token]) -> ASTNode:
    """Convenience function to parse tokens"""
    parser = Parser(tokens)
    return parser.parse()

if __name__ == '__main__':
    from .lexer import tokenize
    
    test_code = '''
fn add(x: i32, y: i32) -> i32 {
    x + y
}

struct Point {
    x: f64,
    y: f64,
}

fn main() {
    let p = Point { x: 1.0, y: 2.0 };
    let result = add(1, 2);
}
'''
    
    tokens = tokenize(test_code)
    ast = parse(tokens)
    print("Parsed successfully!")
