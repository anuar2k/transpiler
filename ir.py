from pathlib import Path
from dataclasses import dataclass
from typing import Any, List, Optional
from pprint import pprint
import wadze

@dataclass
class Prod:
    prod: str
    imm_args: Any
    invars: List[str]
    outvar: Optional[str]

simple_prods = {
    # stack_argc, stack_ret
    'unreachable': (0, False),
    'nop': (0, False),
    'drop': (1, False),
    'select': (3, True),
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

def parse_block(func_type, instrs):
    stack = []
    next_temp = 0

    def push_temp():
        nonlocal stack
        nonlocal next_temp
        name = f't{next_temp}'
        next_temp += 1
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

        if name in simple_prods:
            stack_argc, stack_ret = simple_prods[name]
            imm_args = args

            invars = pop_temps(stack_argc)
            outvar = push_temp() if stack_ret else None
            prod = Prod(name, imm_args, invars, outvar)
        elif name == 'local.set':
            local_idx, = args
            outvar = f'l{local_idx}'
            prod = Prod(name, (), pop_temps(1), outvar)
        elif name == 'local.get':
            local_idx, = args
            outvar = push_temp()
            prod = Prod(name, (), [], outvar)
        elif name == 'block':
            outtype, body = args
            body_prods = parse_block(func_type, body)
            outvar = push_temp() if outtype is not None else None
            prod = Prod(name, (body_prods), [], outvar)
        elif name == 'loop':
            outtype, body = args
            body_prods = parse_block(func_type, body)
            outvar = push_temp() if outtype is not None else None
            prod = Prod(name, (body_prods), [], outvar)
        elif name == 'if':
            outtype, (if_body, else_body) = args
            if_body_prods = parse_block(func_type, if_body)
            else_body_prods = parse_block(func_type, else_body)
            outvar = push_temp() if outtype is not None else None
            prod = Prod(name, (if_body_prods, else_body_prods), pop_temps(1), outvar)
        elif name == 'return':
            ret_argc = len(func_type.returns)
            prod = Prod(name, (), pop_temps(ret_argc), None)
        else:
            raise NotImplementedError(f"Instruction '{name}' not implemented.")

        prods.append(prod)

    return prods

def parse_module_func(module, func_idx):
    func_code = wadze.parse_code(module['code'][func_idx])
    func_type = module['type'][module['func'][func_idx]]
    parsed = parse_block(func_type, func_code.instructions)
    return parsed

root = Path(__file__).parent

with open(root / "input.wasm", "rb") as f:
    module = wadze.parse_module(f.read())
func_code = wadze.parse_code(module['code'][1])

# with open(root / "test3.wasm", "rb") as f:
#     module = wadze.parse_module(f.read())
# func_code = wadze.parse_code(module['code'][0])

# print(module)

parsed = parse_module_func(module, 1)
pprint(parsed)
