from pathlib import Path
import wadze

ROOT_DIR = Path(__file__).parent

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

with open(ROOT_DIR / "input.wasm", "rb") as f:
    module = wadze.parse_module(f.read())
    module['code'] = [wadze.parse_code(c) for c in module['code']]

print(module)

# Print code sections with WAT-like formatting
for i, code in enumerate(module.get('code', [])):
    print(f"\n=== Function {i} ===")
    print(format_code(code))
