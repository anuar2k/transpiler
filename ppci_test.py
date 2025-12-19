code = """
(module
(type $t0 (func (param f64 f64 i32) (result i32)))
(func $test (type $t0) (param f64 f64 i32) (result i32)
  (local f64 f64 f64)
  f64.const 0x0p+0 (;=0;)
  local.set 3
  f64.const 0x0p+0 (;=0;)
  local.set 4
  block  ;; label = @1
    loop  ;; label = @2
      i32.const 1
      local.get 2
      i32.const 0
      i32.gt_s
      i32.sub
      br_if 1 (;@1;)
      local.get 3
      local.get 3
      f64.mul
      local.get 4
      local.get 4
      f64.mul
      f64.sub
      local.get 0
      f64.add
      local.set 5
      f64.const 0x1p+1 (;=2;)
      local.get 3
      f64.mul
      local.get 4
      f64.mul
      local.get 1
      f64.add
      local.set 4
      local.get 5
      local.set 3
      local.get 2
      i32.const 1
      i32.sub
      local.set 2
      local.get 3
      local.get 3
      f64.mul
      local.get 4
      local.get 4
      f64.mul
      f64.add
      f64.const 0x1p+2 (;=4;)
      f64.gt
      if  ;; label = @3
        i32.const 0
        return
      end
      br 0 (;@2;)
    end
  end
  i32.const 1
  return
)
(export "test" (func $test)
))
"""

from ppci import wasm
from ppci.wasm.arch import WasmArchitecture
from ppci.lang import python
import io

module = wasm.Module(code)
module.show()

arch = WasmArchitecture()
ir = wasm.wasm_to_ir(module, arch.info.get_type_info('ptr'))

output = io.StringIO()
x = python.ir_to_python(ir, output)

print("Generated Python code:")
print(output.getvalue())
