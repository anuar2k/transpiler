from pathlib import Path
from dataclasses import dataclass
from typing import Any, List, Optional
from pprint import pprint
import wadze

@dataclass
class IRProd:
    prod: str
    imm_args: Any
    invars: List[str]
    outvar: Optional[str]

prods_simple = {
    # stack_argc, stack_ret
    'i32.const': (0, True),
    'i64.const': (0, True),
    'f32.const': (0, True),
    'f64.const': (0, True),
    'i32.gt_s': (2, True),
    'i32.sub': (2, True),
    'br_if': (1, False),
    'f64.mul': (2, True),
    'f64.sub': (2, True),
    'f64.add': (2, True),
    'f64.gt': (2, True),
    'br': (0, False),
}

prods_call_like = {
    'i32.gt_s',
    'i32.sub',
    'f64.mul',
    'f64.sub',
    'f64.add',
    'f64.gt',
}

def parse_block(next_temp, stack, func_type, instrs):
    def push_temp():
        nonlocal stack
        name = f't{next_temp[0]}'
        next_temp[0] += 1
        stack.append(name)
        return name
    def pop_temps(n):
        nonlocal stack
        args = []
        for _ in range(n):
            args.insert(0, stack.pop())
        return args

    prods = []

    for instr in instrs:
        name = instr[0]
        args = instr[1:]
        prod = None
        terminal = False

        if name in prods_simple:
            stack_argc, stack_ret = prods_simple[name]
            imm_args = args

            invars = pop_temps(stack_argc)
            outvar = push_temp() if stack_ret else None
            prod = IRProd(name, imm_args, invars, outvar)
        elif name == 'local.set':
            local_idx, = args
            outvar = f'l{local_idx}'
            prod = IRProd(name, (), pop_temps(1), outvar)
        elif name == 'local.get':
            local_idx, = args
            outvar = push_temp()
            prod = IRProd(name, (), [f'l{local_idx}'], outvar)
        elif name == 'block':
            outtype, body = args
            body_prods = parse_block(next_temp, [], func_type, body)
            outvar = push_temp() if outtype is not None else None
            prod = IRProd(name, (body_prods,), [], outvar)
        elif name == 'loop':
            outtype, body = args
            body_prods = parse_block(next_temp, [], func_type, body)
            outvar = push_temp() if outtype is not None else None
            prod = IRProd(name, (body_prods,), [], outvar)
        elif name == 'if':
            outtype, (if_body, else_body) = args
            if_body_prods = parse_block(next_temp, [], func_type, if_body)
            else_body_prods = parse_block(next_temp, [], func_type, else_body)
            outvar = push_temp() if outtype is not None else None
            prod = IRProd(name, (if_body_prods, else_body_prods), pop_temps(1), outvar)
        elif name == 'return':
            ret_argc = len(func_type.returns)
            prod = IRProd(name, (), pop_temps(ret_argc), None)
            terminal = True
        elif name == 'unreachable':
            prod = IRProd(name, (), [], None)
            terminal = True
        else:
            raise NotImplementedError(f"Instruction '{name}' not implemented.")

        prods.append(prod)
        if terminal:
            break

    return prods

initializers = {
    'i32': 0,
    'i64': 0,
    'f32': 0.0,
    'f64': 0.0,
}

def parse_module_func(module, func_idx):
    func_code = wadze.parse_code(module['code'][func_idx])
    func_type = module['type'][module['func'][func_idx]]
    next_temp = [0] # mutable integer for temp variable naming
    stack = []
    prods = []
    argc = len(func_type.params)
    for local_idx, local_type in enumerate(func_code.locals):
        initializer = initializers[local_type]
        prods.append(IRProd('local', (initializer,), [], f'l{argc + local_idx}'))
    prods += parse_block(next_temp, stack, func_type, func_code.instructions)
    terminated = len(prods) > 0 and prods[-1].prod in ('return', 'unreachable')
    if not terminated:
        if len(func_type.returns) != len(stack):
            raise ValueError("Function does not end with proper return values on stack.")
        prods.append(IRProd('return', (), stack, None))
    return IRFunc(func_type, func_code.locals, prods)

@dataclass
class IRFunc:
    func_type: wadze.FunctionType
    localz: List[str]
    prods: List[IRProd]

def write_line(lines, indent, line):
    lines.append('\t' * indent + line)

def assign(lines, indent, outvar, expr):
    write_line(lines, indent, f'{outvar} = {expr}')

def void(lines, indent, expr):
    write_line(lines, indent, f'{expr}')

def call_like(lines, indent, prod: IRProd):
    args_repr = []
    args_repr += [repr(arg) for arg in prod.imm_args]
    args_repr += prod.invars

    args = ', '.join(args_repr)
    name = prod.prod
    rhs = f'ops[{repr(name)}]({args})'
    if prod.outvar is not None:
        assign(lines, indent, prod.outvar, rhs)
    else:
        void(lines, indent, rhs)

def translate_prods(lines, indent, prods: List[IRProd]):
    if len(prods) == 0:
        write_line(lines, indent, 'pass')
        return

    for prod in prods:
        name = prod.prod
        if name in prods_call_like:
            call_like(lines, indent, prod)
        elif name == 'local':
            assign(lines, indent, prod.outvar, repr(prod.imm_args[0]))
        elif name == 'local.set':
            assign(lines, indent, prod.outvar, prod.invars[0])
        elif name == 'local.get':
            assign(lines, indent, prod.outvar, prod.invars[0])
        elif name == 'i32.const':
            assign(lines, indent, prod.outvar, repr(prod.imm_args[0]))
        elif name == 'i64.const':
            assign(lines, indent, prod.outvar, repr(prod.imm_args[0]))
        elif name == 'f32.const':
            assign(lines, indent, prod.outvar, repr(prod.imm_args[0]))
        elif name == 'f64.const':
            assign(lines, indent, prod.outvar, repr(prod.imm_args[0]))
        elif name == 'block':
            write_line(lines, indent, f'# begin block')
            write_line(lines, indent, 'while True:')
            translate_prods(lines, indent + 1, prod.imm_args[0])
            write_line(lines, indent, f'# end block')
        elif name == 'loop':
            write_line(lines, indent, f'# begin loop')
            write_line(lines, indent, 'while True:')
            translate_prods(lines, indent + 1, prod.imm_args[0])
            write_line(lines, indent, f'# end loop')
        elif name == 'if':
            write_line(lines, indent, f'# begin if/else')
            write_line(lines, indent, 'while True:')
            write_line(lines, indent + 1, f'if {prod.invars[0]}:')
            translate_prods(lines, indent + 2, prod.imm_args[0])
            if prod.imm_args[1]:
                write_line(lines, indent + 1, f'else:')
                translate_prods(lines, indent + 2, prod.imm_args[1])
            write_line(lines, indent, f'# end if')
        elif name == 'br_if':
            label_idx, = prod.imm_args
            args = ', '.join(prod.invars)
            write_line(lines, indent, f'if {args}:')
            write_line(lines, indent + 1, f'# br to label {label_idx} (not implemented)')
            write_line(lines, indent + 1, 'break')
        elif name == 'br':
            label_idx, = prod.imm_args
            write_line(lines, indent, f'# br to label {label_idx} (not implemented)')
            write_line(lines, indent + 1, 'break')
        elif name == 'return':
            args = ', '.join(prod.invars)
            write_line(lines, indent, f'return {args}')
        elif name == 'unreachable':
            write_line(lines, indent, f'raise Exception("unreachable")')
        else:
            raise NotImplementedError(f"Translation for '{prod.prod}' not implemented.")

def translate_simple(irfunc: IRFunc):
    lines = []
    argc = len(irfunc.func_type.params)
    func_args = ', '.join(f'l{i}' for i in range(argc))
    write_line(lines, 0, f'def translated({func_args}):')
    translate_prods(lines, 1, irfunc.prods)
    return '\n'.join(lines) + '\n'

root = Path(__file__).parent

with open(root / "input.wasm", "rb") as f:
    module = wadze.parse_module(f.read())
func_code = wadze.parse_code(module['code'][1])

# with open(root / "test3.wasm", "rb") as f:
#     module = wadze.parse_module(f.read())
# func_code = wadze.parse_code(module['code'][0])

print(module)

parsed = parse_module_func(module, 1)
pprint(parsed)
translated_code = translate_simple(parsed)
print(translated_code)

code_obj = compile(translated_code, '<string>', 'exec')
# TODO: get int wrapping right, to ensure that comparisons work correctly
ops = {
    'i32.gt_s': lambda x, y: 1 if x > y else 0,
    'i32.sub': lambda x, y: (x - y) & 0xFFFFFFFF,
    'f64.mul': lambda x, y: x * y,
    'f64.sub': lambda x, y: x - y,
    'f64.add': lambda x, y: x + y,
    'f64.gt': lambda x, y: 1 if x > y else 0,
    'i32.gt_u': lambda x, y: 1 if (x & 0xFFFFFFFF) > (y & 0xFFFFFFFF) else 0,
}
globs = {
    'ops': ops,
}
ns = {}
exec(code_obj, globs, ns)
translated_func = ns['translated']
translated_func(0.0, 0.0, 10)
