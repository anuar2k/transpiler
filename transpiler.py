from pathlib import Path
import wadze

ROOT_DIR = Path(__file__).parent

# Built-in WebAssembly instructions
impls = {
    # Arithmetic
    'i32.add', 'i32.sub', 'i32.mul', 'i32.div_s', 'i32.div_u', 'i32.rem_s', 'i32.rem_u',
    'i64.add', 'i64.sub', 'i64.mul', 'i64.div_s', 'i64.div_u', 'i64.rem_s', 'i64.rem_u',
    'f32.add', 'f32.sub', 'f32.mul', 'f32.div', 'f32.min', 'f32.max', 'f32.copysign',
    'f64.add', 'f64.sub', 'f64.mul', 'f64.div', 'f64.min', 'f64.max', 'f64.copysign',
    
    # Bitwise
    'i32.and', 'i32.or', 'i32.xor', 'i32.shl', 'i32.shr_s', 'i32.shr_u', 'i32.rotl', 'i32.rotr',
    'i32.clz', 'i32.ctz', 'i32.popcnt',
    'i64.and', 'i64.or', 'i64.xor', 'i64.shl', 'i64.shr_s', 'i64.shr_u', 'i64.rotl', 'i64.rotr',
    'i64.clz', 'i64.ctz', 'i64.popcnt',
    
    # Comparison
    'i32.eq', 'i32.ne', 'i32.lt_s', 'i32.lt_u', 'i32.gt_s', 'i32.gt_u', 'i32.le_s', 'i32.le_u', 'i32.ge_s', 'i32.ge_u', 'i32.eqz',
    'i64.eq', 'i64.ne', 'i64.lt_s', 'i64.lt_u', 'i64.gt_s', 'i64.gt_u', 'i64.le_s', 'i64.le_u', 'i64.ge_s', 'i64.ge_u', 'i64.eqz',
    'f32.eq', 'f32.ne', 'f32.lt', 'f32.gt', 'f32.le', 'f32.ge',
    'f64.eq', 'f64.ne', 'f64.lt', 'f64.gt', 'f64.le', 'f64.ge',
    
    # Math
    'f32.abs', 'f32.neg', 'f32.ceil', 'f32.floor', 'f32.trunc', 'f32.nearest', 'f32.sqrt',
    'f64.abs', 'f64.neg', 'f64.ceil', 'f64.floor', 'f64.trunc', 'f64.nearest', 'f64.sqrt',
    
    # Conversions
    'i32.wrap_i64', 'i32.trunc_f32_s', 'i32.trunc_f32_u', 'i32.trunc_f64_s', 'i32.trunc_f64_u',
    'i64.extend_i32_s', 'i64.extend_i32_u', 'i64.trunc_f32_s', 'i64.trunc_f32_u', 'i64.trunc_f64_s', 'i64.trunc_f64_u',
    'f32.convert_i32_s', 'f32.convert_i32_u', 'f32.convert_i64_s', 'f32.convert_i64_u', 'f32.demote_f64',
    'f64.convert_i32_s', 'f64.convert_i32_u', 'f64.convert_i64_s', 'f64.convert_i64_u', 'f64.promote_f32',
    'i32.reinterpret_f32', 'i64.reinterpret_f64', 'f32.reinterpret_i32', 'f64.reinterpret_i64',
    
    # Memory
    'i32.load', 'i32.load8_s', 'i32.load8_u', 'i32.load16_s', 'i32.load16_u',
    'i64.load', 'i64.load8_s', 'i64.load8_u', 'i64.load16_s', 'i64.load16_u', 'i64.load32_s', 'i64.load32_u',
    'f32.load', 'f64.load',
    'i32.store', 'i32.store8', 'i32.store16',
    'i64.store', 'i64.store8', 'i64.store16', 'i64.store32',
    'f32.store', 'f64.store',
    'memory.size', 'memory.grow',
}

def format_code(code, indent=0):
    '''
    Format parsed Code object into WAT-like string with proper indentation.
    indent: starting indentation level (each level is 2 spaces)
    Returns formatted string representation of the code.
    '''
    lines = []
    if code.locals:
        lines.append(' ' * (indent * 2) + f'(locals {" ".join(code.locals)})')

    for instruction in code.instructions:
        lines.extend(_format_instruction(instruction, indent))

    return '\n'.join(lines)

def _format_instruction(instruction, indent):
    '''
    Format a single instruction with proper nesting indentation.
    Returns list of lines.
    '''
    lines = []
    name = instruction[0]
    args = instruction[1:]
    indent_str = ' ' * (indent * 2)

    if name == 'block':
        result_type, body = args
        type_str = f' {result_type}' if result_type else ''
        lines.append(f'{indent_str}(block{type_str}')
        for instr in body:
            lines.extend(_format_instruction(instr, indent + 1))
        lines.append(f'{indent_str})')
    elif name == 'loop':
        result_type, body = args
        type_str = f' {result_type}' if result_type else ''
        lines.append(f'{indent_str}(loop{type_str}')
        for instr in body:
            lines.extend(_format_instruction(instr, indent + 1))
        lines.append(f'{indent_str})')
    elif name == 'if':
        result_type, (then_body, else_body) = args
        type_str = f' {result_type}' if result_type else ''
        lines.append(f'{indent_str}(if{type_str}')
        lines.append(f'{indent_str}  (then')
        for instr in then_body:
            lines.extend(_format_instruction(instr, indent + 2))
        lines.append(f'{indent_str}  )')
        if else_body:
            lines.append(f'{indent_str}  (else')
            for instr in else_body:
                lines.extend(_format_instruction(instr, indent + 2))
            lines.append(f'{indent_str}  )')
        lines.append(f'{indent_str})')
    else:
        # Simple instruction with optional arguments
        if args:
            args_str = ' ' + ' '.join(str(arg) for arg in args)
        else:
            args_str = ''
        lines.append(f'{indent_str}({name}{args_str})')

    return lines

def generate_ssa(code, func_idx, module, functions=None):
    '''
    Generate SSA-like Python code from parsed WASM code.
    
    code: Code namedtuple with (locals, instructions)
    func_idx: index of this function in module
    module: parsed WASM module dict
    functions: dict mapping function index to function name (for user-defined function calls)
    
    Returns: string of generated Python code
    '''
    if functions is None:
        functions = {}
    
    # Get function signature
    func_type_idx = module.get('func', [])[func_idx] if func_idx < len(module.get('func', [])) else 0
    func_type = module.get('type', [])[func_type_idx] if func_type_idx < len(module.get('type', [])) else None
    
    if not func_type:
        return "# Could not determine function signature\npass"
    
    lines = []
    var_counter = [0]  # mutable counter
    stack = []  # stack of variable indices
    
    # Initialize parameters
    for i, param_type in enumerate(func_type.params):
        var_idx = var_counter[0]
        var_counter[0] += 1
        lines.append(f"_{var_idx} = arg{i}")
        stack.append(var_idx)
    
    # Declare locals
    local_start = var_counter[0]
    for i, local_type in enumerate(code.locals):
        var_idx = var_counter[0]
        var_counter[0] += 1
        lines.append(f"_{var_idx} = None  # {local_type}")
    
    # Generate instructions
    for instr in code.instructions:
        instr_lines = _generate_ssa_instruction(instr, stack, var_counter, func_type, functions, module)
        lines.extend(instr_lines)
    
    # If function returns but no explicit return was encountered, add implicit return
    if func_type.returns and not any('return' in line for line in lines[-3:]):
        if stack:
            ret_var = stack[-1]
            lines.append(f"return _{ret_var}")
        else:
            lines.append("return None  # Error: expected return value")
    elif not func_type.returns and not any('return' in line for line in lines[-3:]):
        lines.append("return")
    
    return '\n'.join(lines)

def _generate_ssa_instruction(instr, stack, var_counter, func_type, functions, module):
    '''
    Generate SSA code for a single instruction.
    stack: list of variable indices on the stack
    var_counter: [current_var_count]
    Returns: list of code lines
    '''
    name = instr[0]
    args = instr[1:]
    lines = []
    
    # Constants
    if name == 'i32.const':
        var_idx = var_counter[0]
        var_counter[0] += 1
        lines.append(f"_{var_idx} = {args[0]}")
        stack.append(var_idx)
    elif name == 'i64.const':
        var_idx = var_counter[0]
        var_counter[0] += 1
        lines.append(f"_{var_idx} = {args[0]}")
        stack.append(var_idx)
    elif name == 'f32.const':
        var_idx = var_counter[0]
        var_counter[0] += 1
        lines.append(f"_{var_idx} = {args[0]}")
        stack.append(var_idx)
    elif name == 'f64.const':
        var_idx = var_counter[0]
        var_counter[0] += 1
        lines.append(f"_{var_idx} = {args[0]}")
        stack.append(var_idx)
    
    # Stack manipulation
    elif name == 'drop':
        if stack:
            stack.pop()
    
    elif name == 'select':
        # select: takes 3 values, pops condition (top), then false_val, then true_val
        # result = true_val if condition else false_val
        if len(stack) >= 3:
            cond_idx = stack.pop()
            false_idx = stack.pop()
            true_idx = stack.pop()
            var_idx = var_counter[0]
            var_counter[0] += 1
            lines.append(f"_{var_idx} = _{true_idx} if _{cond_idx} else _{false_idx}")
            stack.append(var_idx)
    
    # Variables
    elif name == 'local.get':
        local_idx = args[0]
        var_idx = var_counter[0]
        var_counter[0] += 1
        lines.append(f"_{var_idx} = _{local_idx}")
        stack.append(var_idx)
    
    elif name == 'local.set':
        local_idx = args[0]
        if stack:
            val_idx = stack.pop()
            lines.append(f"_{local_idx} = _{val_idx}")
    
    elif name == 'local.tee':
        local_idx = args[0]
        if stack:
            val_idx = stack[-1]
            lines.append(f"_{local_idx} = _{val_idx}")
    
    elif name == 'global.get':
        global_idx = args[0]
        var_idx = var_counter[0]
        var_counter[0] += 1
        lines.append(f"_{var_idx} = globals[{global_idx}]")
        stack.append(var_idx)
    
    elif name == 'global.set':
        if stack:
            val_idx = stack.pop()
            global_idx = args[0]
            lines.append(f"globals[{global_idx}] = _{val_idx}")
    
    # Calls
    elif name == 'call':
        func_idx = args[0]
        num_imports = len(module.get('import', []))
        
        # Determine if it's an imported function or local function
        if func_idx < num_imports:
            # Imported function
            imported_func = module.get('import', [])[func_idx]
            called_func_type = module.get('type', [])[imported_func.typeidx]
        else:
            # Local function
            local_func_idx = func_idx - num_imports
            if local_func_idx < len(module.get('func', [])):
                type_idx = module.get('func', [])[local_func_idx]
                called_func_type = module.get('type', [])[type_idx]
            else:
                called_func_type = None
        
        if called_func_type:
            # Pop arguments (in reverse order - they were pushed left to right)
            call_args = []
            for _ in range(len(called_func_type.params)):
                if stack:
                    call_args.insert(0, f"_{stack.pop()}")
            
            # Generate call
            if func_idx < num_imports:
                func_name = functions.get(func_idx, f"import_{func_idx}")
            else:
                func_name = functions.get(func_idx, f"func_{func_idx - num_imports}")
            
            if called_func_type.returns:
                var_idx = var_counter[0]
                var_counter[0] += 1
                lines.append(f"_{var_idx} = {func_name}({', '.join(call_args)})")
                stack.append(var_idx)
            else:
                lines.append(f"{func_name}({', '.join(call_args)})")
    
    # Control flow
    elif name == 'return':
        if stack:
            ret_var = stack.pop()
            lines.append(f"return _{ret_var}")
        else:
            lines.append("return")
    
    elif name == 'unreachable':
        lines.append("raise Exception('unreachable')")
    
    elif name == 'nop':
        lines.append("pass")
    
    # Binary operations
    elif name in impls:
        # Most binary operations
        if name.endswith(('eqz',)):  # unary
            if stack:
                arg = stack.pop()
                var_idx = var_counter[0]
                var_counter[0] += 1
                lines.append(f"_{var_idx} = impls['{name}'](_{arg})")
                stack.append(var_idx)
        else:  # binary or multi-arg
            # Most WebAssembly binary ops
            if len(stack) >= 2:
                right = stack.pop()
                left = stack.pop()
                var_idx = var_counter[0]
                var_counter[0] += 1
                lines.append(f"_{var_idx} = impls['{name}'](_{left}, _{right})")
                stack.append(var_idx)
    
    return lines

with open(ROOT_DIR / "input.wasm", "rb") as f:
    module = wadze.parse_module(f.read())
    module['code'] = [wadze.parse_code(c) for c in module['code']]

print(module)

# Print code sections with WAT-like formatting
for i, code in enumerate(module.get('code', [])):
    print(f"\n=== Function {i} (WAT) ===")
    print(format_code(code))

# Generate SSA form for function 0 (which has no blocks)
print("\n=== Function 0 (SSA) ===")
if module.get('code'):
    ssa_code = generate_ssa(module['code'][0], 0, module)
    print(ssa_code)
