"""
MiniRust Code Generator - Generates C code from AST
Contains 5 bugs in memory management (BUG-MM-1 through BUG-MM-5)
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from .parser import ASTNode, ASTNodeType, Type, Function, StructDef, EnumDef
import threading
import queue

@dataclass
class CodeGenContext:
    """Context for code generation"""
    indent_level: int = 0
    current_function: Optional[str] = None
    local_vars: Dict[str, Type] = field(default_factory=dict)
    heap_allocations: Set[str] = field(default_factory=set)
    borrowed_refs: Set[str] = field(default_factory=set)
    
    def indent(self) -> str:
        return "    " * self.indent_level
    
    def add_indent(self):
        self.indent_level += 1
    
    def remove_indent(self):
        self.indent_level = max(0, self.indent_level - 1)

class CodeGenError(Exception):
    def __init__(self, message: str, node: Optional[ASTNode] = None):
        self.message = message
        self.node = node
        super().__init__(f"Code generation error: {message}")

class CodeGenerator:
    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.output: List[str] = []
        self.context = CodeGenContext()
        self.structs: Dict[str, StructDef] = {}
        self.enums: Dict[str, EnumDef] = {}
        self.functions: Dict[str, Function] = {}
        self.allocated_vars: Set[str] = set()  # Track heap allocations
        self.freed_vars: Set[str] = set()  # Track freed memory
        
        # BUG-MM-1: Thread safety issue - shared state without locks
        self.parallel_compilation = True
        self.compilation_queue = queue.Queue()
        self.results = []
    
    def emit(self, code: str):
        """Emit a line of code"""
        self.output.append(self.context.indent() + code)
    
    def emit_raw(self, code: str):
        """Emit code without indentation"""
        self.output.append(code)
    
    def generate(self) -> str:
        """Generate C code from AST"""
        # Emit headers
        self.emit_raw("#include <stdio.h>")
        self.emit_raw("#include <stdlib.h>")
        self.emit_raw("#include <string.h>")
        self.emit_raw("#include <stdbool.h>")
        self.emit_raw("")
        
        # Generate forward declarations
        self.emit_raw("// Forward declarations")
        for child in self.ast.children:
            if isinstance(child, StructDef):
                self.generate_struct_forward(child)
            elif isinstance(child, EnumDef):
                self.generate_enum_forward(child)
        
        self.emit_raw("")
        
        # Generate type definitions
        self.emit_raw("// Type definitions")
        for child in self.ast.children:
            if isinstance(child, StructDef):
                self.generate_struct(child)
            elif isinstance(child, EnumDef):
                self.generate_enum(child)
        
        self.emit_raw("")
        
        # Generate functions
        self.emit_raw("// Functions")
        for child in self.ast.children:
            if isinstance(child, Function):
                self.generate_function(child)
        
        return "\n".join(self.output)
    
    def generate_struct_forward(self, struct: StructDef):
        """Generate forward declaration for struct"""
        self.structs[struct.name] = struct
        self.emit_raw(f"typedef struct {struct.name} {struct.name};")
    
    def generate_struct(self, struct: StructDef):
        """Generate struct definition"""
        self.emit_raw(f"struct {struct.name} {{")
        self.context.add_indent()
        
        for field_name, field_type in struct.fields.items():
            c_type = self.type_to_c(field_type)
            self.emit(f"{c_type} {field_name};")
        
        self.context.remove_indent()
        self.emit_raw("};")
        self.emit_raw("")
    
    def generate_enum_forward(self, enum: EnumDef):
        """Generate forward declaration for enum"""
        self.enums[enum.name] = enum
        self.emit_raw(f"typedef enum {enum.name}Variant {enum.name}Variant;")
    
    def generate_enum(self, enum: EnumDef):
        """Generate enum definition"""
        # Variant enum
        self.emit_raw(f"enum {enum.name}Variant {{")
        self.context.add_indent()
        
        for variant_name in enum.variants:
            self.emit(f"{enum.name}_{variant_name},")
        
        self.context.remove_indent()
        self.emit_raw("};")
        self.emit_raw("")
        
        # Union struct
        self.emit_raw(f"typedef struct {enum.name} {{")
        self.context.add_indent()
        self.emit(f"enum {enum.name}Variant variant;")
        
        # Check if any variant has data
        has_data = any(v is not None for v in enum.variants.values())
        if has_data:
            self.emit("union {")
            self.context.add_indent()
            
            for variant_name, variant_type in enum.variants.items():
                if variant_type:
                    c_type = self.type_to_c(variant_type)
                    self.emit(f"{c_type} {variant_name.lower()};")
            
            self.context.remove_indent()
            self.emit("} data;")
        
        self.context.remove_indent()
        self.emit_raw(f"}} {enum.name};")
        self.emit_raw("")
    
    def generate_function(self, func: Function):
        """Generate function definition"""
        self.functions[func.name] = func
        self.context.current_function = func.name
        self.context.local_vars.clear()
        
        # Return type
        if func.return_type:
            ret_type = self.type_to_c(func.return_type)
        else:
            ret_type = "void"
        
        # Parameters
        params = []
        for param in func.params:
            param_type = self.type_to_c(param["type"])
            params.append(f"{param_type} {param['name']}")
            self.context.local_vars[param["name"]] = param["type"]
        
        self.emit_raw(f"{ret_type} {func.name}({', '.join(params)}) {{")
        self.context.add_indent()
        
        # Generate body
        if func.body:
            self.generate_block(func.body)
        
        # BUG-MM-2: Missing cleanup for heap-allocated local variables
        # Should generate free() calls for allocated variables but doesn't
        
        self.context.remove_indent()
        self.emit_raw("}")
        self.emit_raw("")
        
        self.context.current_function = None
    
    def generate_block(self, block: ASTNode):
        """Generate code for a block"""
        for stmt in block.children:
            self.generate_statement(stmt)
    
    def generate_statement(self, node: ASTNode):
        """Generate code for a statement"""
        if node.node_type == ASTNodeType.LET_BINDING:
            self.generate_let_binding(node)
        elif node.node_type == ASTNodeType.RETURN_EXPR:
            self.generate_return(node)
        elif node.node_type == ASTNodeType.IF_EXPR:
            self.generate_if(node)
        elif node.node_type == ASTNodeType.WHILE_EXPR:
            self.generate_while(node)
        elif node.node_type == ASTNodeType.FOR_EXPR:
            self.generate_for(node)
        elif node.node_type == ASTNodeType.LOOP_EXPR:
            self.generate_loop(node)
        elif node.node_type == ASTNodeType.BREAK_EXPR:
            self.emit("break;")
        elif node.node_type == ASTNodeType.CONTINUE_EXPR:
            self.emit("continue;")
        elif node.node_type == ASTNodeType.BINARY_EXPR:
            expr = self.generate_expression(node)
            self.emit(f"{expr};")
        elif node.node_type == ASTNodeType.CALL_EXPR:
            expr = self.generate_expression(node)
            self.emit(f"{expr};")
        else:
            expr = self.generate_expression(node)
            if expr:
                self.emit(f"{expr};")
    
    def generate_let_binding(self, node: ASTNode):
        """Generate let binding"""
        name = node.attributes["name"]
        is_mut = node.attributes.get("is_mut", False)
        type_annotation = node.attributes.get("type")
        
        # Determine type
        if type_annotation:
            var_type = type_annotation
        elif node.children:
            # BUG-MM-3: Type inference for let bindings doesn't propagate
            # mutability correctly
            var_type = Type("auto")  # Placeholder
        else:
            var_type = Type("void")
        
        self.context.local_vars[name] = var_type
        
        c_type = self.type_to_c(var_type)
        
        if node.children:
            value = self.generate_expression(node.children[0])
            
            # BUG-MM-4: Heap allocation tracking is incomplete
            # Should track allocations for proper cleanup but misses some cases
            if self.is_heap_allocation(node.children[0]):
                self.allocated_vars.add(name)
                self.emit(f"{c_type} {name} = {value};")
            else:
                self.emit(f"{c_type} {name} = {value};")
        else:
            self.emit(f"{c_type} {name};")
    
    def generate_return(self, node: ASTNode):
        """Generate return statement"""
        if node.children:
            value = self.generate_expression(node.children[0])
            self.emit(f"return {value};")
        else:
            self.emit("return;")
    
    def generate_if(self, node: ASTNode):
        """Generate if statement"""
        condition = self.generate_expression(node.children[0])
        self.emit(f"if ({condition}) {{")
        self.context.add_indent()
        self.generate_block(node.children[1])
        self.context.remove_indent()
        
        if len(node.children) > 2:
            else_node = node.children[2]
            if else_node.node_type == ASTNodeType.IF_EXPR:
                self.emit("} else ")
                self.generate_if(else_node)
            else:
                self.emit("} else {")
                self.context.add_indent()
                self.generate_block(else_node)
                self.context.remove_indent()
                self.emit("}")
        else:
            self.emit("}")
    
    def generate_while(self, node: ASTNode):
        """Generate while loop"""
        condition = self.generate_expression(node.children[0])
        self.emit(f"while ({condition}) {{")
        self.context.add_indent()
        self.generate_block(node.children[1])
        self.context.remove_indent()
        self.emit("}")
    
    def generate_for(self, node: ASTNode):
        """Generate for loop"""
        var_name = node.attributes["var_name"]
        iterable = self.generate_expression(node.children[0])
        
        # Simplified: convert to while loop with iterator
        self.emit(f"// for {var_name} in {iterable}")
        self.emit(f"for (int _i = 0; _i < {iterable}_len; _i++) {{")
        self.context.add_indent()
        self.emit(f"auto {var_name} = {iterable}[_i];")
        self.generate_block(node.children[1])
        self.context.remove_indent()
        self.emit("}")
    
    def generate_loop(self, node: ASTNode):
        """Generate infinite loop"""
        self.emit("while (true) {")
        self.context.add_indent()
        self.generate_block(node.children[0])
        self.context.remove_indent()
        self.emit("}")
    
    def generate_expression(self, node: ASTNode) -> str:
        """Generate expression code"""
        if node.node_type == ASTNodeType.LITERAL:
            return self.generate_literal(node)
        elif node.node_type == ASTNodeType.PATH_EXPR:
            return node.attributes["path"]
        elif node.node_type == ASTNodeType.BINARY_EXPR:
            return self.generate_binary_expr(node)
        elif node.node_type == ASTNodeType.UNARY_EXPR:
            return self.generate_unary_expr(node)
        elif node.node_type == ASTNodeType.CALL_EXPR:
            return self.generate_call_expr(node)
        elif node.node_type == ASTNodeType.INDEX_EXPR:
            return self.generate_index_expr(node)
        elif node.node_type == ASTNodeType.FIELD_EXPR:
            return self.generate_field_expr(node)
        elif node.node_type == ASTNodeType.METHOD_CALL:
            return self.generate_method_call(node)
        elif node.node_type == ASTNodeType.STRUCT_LITERAL:
            return self.generate_struct_literal(node)
        elif node.node_type == ASTNodeType.ARRAY_LITERAL:
            return self.generate_array_literal(node)
        elif node.node_type == ASTNodeType.TUPLE_LITERAL:
            return self.generate_tuple_literal(node)
        else:
            return "/* unknown expression */"
    
    def generate_literal(self, node: ASTNode) -> str:
        """Generate literal value"""
        value = node.attributes["value"]
        lit_type = node.attributes["type"]
        
        if lit_type == "int":
            return str(value)
        elif lit_type == "float":
            return f"{value}f"
        elif lit_type == "string":
            return f'"{value}"'
        elif lit_type == "bool":
            return "true" if value else "false"
        else:
            return str(value)
    
    def generate_binary_expr(self, node: ASTNode) -> str:
        """Generate binary expression"""
        left = self.generate_expression(node.children[0])
        right = self.generate_expression(node.children[1])
        op = node.attributes["operator"]
        
        # Map Rust operators to C
        op_map = {
            "&&": "&&",
            "||": "||",
            "==": "==",
            "!=": "!=",
            "<": "<",
            ">": ">",
            "<=": "<=",
            ">=": ">=",
        }
        
        c_op = op_map.get(op, op)
        return f"({left} {c_op} {right})"
    
    def generate_unary_expr(self, node: ASTNode) -> str:
        """Generate unary expression"""
        operand = self.generate_expression(node.children[0])
        op = node.attributes.get("operator", "")
        
        if op == "!":
            return f"(!{operand})"
        elif op == "-":
            return f"(-{operand})"
        elif op == "&":
            return f"(&{operand})"
        elif op == "*":
            return f"(*{operand})"
        elif op == "?":
            # Error propagation - simplified
            return f"({operand}) /* ? operator */"
        else:
            return operand
    
    def generate_call_expr(self, node: ASTNode) -> str:
        """Generate function call"""
        func_expr = self.generate_expression(node.children[0])
        args = [self.generate_expression(arg) for arg in node.children[1:]]
        
        return f"{func_expr}({', '.join(args)})"
    
    def generate_index_expr(self, node: ASTNode) -> str:
        """Generate array indexing"""
        container = self.generate_expression(node.children[0])
        index = self.generate_expression(node.children[1])
        
        # BUG-MM-5: Array bounds checking is not implemented
        # Should generate bounds check but doesn't
        return f"{container}[{index}]"
    
    def generate_field_expr(self, node: ASTNode) -> str:
        """Generate field access"""
        obj = self.generate_expression(node.children[0])
        field = node.attributes["field"]
        
        # Check if it's a pointer (needs ->) or value (needs .)
        # Simplified: always use ->
        return f"{obj}->{field}"
    
    def generate_method_call(self, node: ASTNode) -> str:
        """Generate method call"""
        obj = self.generate_expression(node.children[0])
        method = node.attributes["method"]
        args = [self.generate_expression(arg) for arg in node.children[1:]]
        
        # Convert to function call with self as first arg
        all_args = [obj] + args
        return f"{method}({', '.join(all_args)})"
    
    def generate_struct_literal(self, node: ASTNode) -> str:
        """Generate struct literal"""
        struct_name = node.attributes["struct_name"]
        fields = node.attributes["fields"]
        
        # Allocate struct
        var_name = f"_tmp_{len(self.allocated_vars)}"
        self.emit(f"{struct_name}* {var_name} = malloc(sizeof({struct_name}));")
        self.allocated_vars.add(var_name)
        
        for field_name, field_value in fields.items():
            value = self.generate_expression(field_value)
            self.emit(f"{var_name}->{field_name} = {value};")
        
        return var_name
    
    def generate_array_literal(self, node: ASTNode) -> str:
        """Generate array literal"""
        elements = [self.generate_expression(e) for e in node.children]
        
        if node.attributes.get("is_repeat"):
            # [value; count] syntax
            value = elements[0]
            count = elements[1]
            var_name = f"_arr_{len(self.allocated_vars)}"
            self.emit(f"/* Array repeat: [{value}; {count}] */")
            return var_name
        
        return f"{{{', '.join(elements)}}}"
    
    def generate_tuple_literal(self, node: ASTNode) -> str:
        """Generate tuple literal"""
        if not node.children:
            return "/* empty tuple */"
        
        elements = [self.generate_expression(e) for e in node.children]
        return f"{{{', '.join(elements)}}}"
    
    def type_to_c(self, rust_type: Type) -> str:
        """Convert Rust type to C type"""
        type_map = {
            "i8": "int8_t",
            "i16": "int16_t",
            "i32": "int32_t",
            "i64": "int64_t",
            "u8": "uint8_t",
            "u16": "uint16_t",
            "u32": "uint32_t",
            "u64": "uint64_t",
            "f32": "float",
            "f64": "double",
            "bool": "bool",
            "char": "char",
            "str": "char*",
            "String": "char*",
            "usize": "size_t",
            "isize": "ptrdiff_t",
        }
        
        base_type = type_map.get(rust_type.name, rust_type.name)
        
        if rust_type.is_reference:
            base_type += "*"
        
        return base_type
    
    def is_heap_allocation(self, node: ASTNode) -> bool:
        """Check if expression involves heap allocation"""
        if node.node_type == ASTNodeType.CALL_EXPR:
            func_name = node.children[0].attributes.get("path", "")
            # Common allocation functions
            return func_name in ("Box::new", "Vec::new", "String::from", "malloc")
        elif node.node_type == ASTNodeType.STRUCT_LITERAL:
            return True
        return False
    
    def parallel_compile_functions(self):
        """BUG-MM-1 manifestation: Race condition in parallel compilation"""
        if not self.parallel_compilation:
            return
        
        def compile_worker():
            while True:
                try:
                    func = self.compilation_queue.get_nowait()
                    # Generate code for function
                    # This has a race condition when accessing shared state
                    self.generate_function(func)
                    self.results.append(func.name)
                    self.compilation_queue.task_done()
                except queue.Empty:
                    break
        
        # Start threads without proper synchronization
        threads = []
        for func in self.functions.values():
            self.compilation_queue.put(func)
        
        for _ in range(4):  # 4 worker threads
            t = threading.Thread(target=compile_worker)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()

def generate_c_code(ast: ASTNode) -> str:
    """Convenience function to generate C code"""
    generator = CodeGenerator(ast)
    return generator.generate()

if __name__ == '__main__':
    from .lexer import tokenize
    from .parser import parse
    
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
    printf("Result: %d\\n", result);
}
'''
    
    tokens = tokenize(test_code)
    ast = parse(tokens)
    c_code = generate_c_code(ast)
    print(c_code)
