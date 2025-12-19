#   (func $test (type 4) (param f64 f64 i32) (result i32)
#     (local f64 f64 f64)
#     f64.const 0x0p+0 (;=0;)
#     local.set 3
#     f64.const 0x0p+0 (;=0;)
#     local.set 4
#     block  ;; label = @1
#       loop  ;; label = @2
#         i32.const 1
#         local.get 2
#         i32.const 0
#         i32.gt_s
#         i32.sub
#         br_if 1 (;@1;)
#         local.get 3
#         local.get 3
#         f64.mul
#         local.get 4
#         local.get 4
#         f64.mul
#         f64.sub
#         local.get 0
#         f64.add
#         local.set 5
#         f64.const 0x1p+1 (;=2;)
#         local.get 3
#         f64.mul
#         local.get 4
#         f64.mul
#         local.get 1
#         f64.add
#         local.set 4
#         local.get 5
#         local.set 3
#         local.get 2
#         i32.const 1
#         i32.sub
#         local.set 2
#         local.get 3
#         local.get 3
#         f64.mul
#         local.get 4
#         local.get 4
#         f64.mul
#         f64.add
#         f64.const 0x1p+2 (;=4;)
#         f64.gt
#         if  ;; label = @3
#           i32.const 0
#           return
#         end
#         br 0 (;@2;)
#       end
#     end
#     i32.const 1
#     return)

ops = {
    'i32.gt_s': lambda x, y: 1 if x > y else 0,
    'i32.sub': lambda x, y: (x - y) & 0xFFFFFFFF,
    'f64.mul': lambda x, y: x * y,
    'f64.sub': lambda x, y: x - y,
    'f64.add': lambda x, y: x + y,
    'f64.gt': lambda x, y: 1 if x > y else 0,
}

def func4(a0, a1, a2):
    l0 = a0  # f64
    l1 = a1  # f64
    l2 = a2  # i32
    l3 = 0.0 # f64
    l4 = 0.0 # f64
    l5 = 0.0 # f64

    pc = 0
    while True:
        if pc == 0:
            x0 = 0.0
            # x0
            l3 = x0
            #
            x1 = 0.0
            # x1
            l4 = x1
            #
            pc = 1
            continue
        elif pc == 1:
            pc = 2
            continue
        elif pc == 2:
            x0 = 1
            # x0
            x1 = l2
            # x0, x1
            x2 = 0
            # x0, x1, x2
            x3 = ops['i32.gt_s'](x1, x2)
            # x0, x3
            x4 = ops['i32.sub'](x0, x3)
            # x4
            if x4 != 0:
                pc = 4 # after block
                continue
            #
            x5 = l3
            # x5
            x6 = l3
            # x5, x6
            x7 = ops['f64.mul'](x5, x6)
            # x7
            x8 = l4
            # x7, x8
            x9 = l4
            # x7, x8, x9
            x10 = ops['f64.mul'](x8, x9)
            # x7, x10
            x11 = ops['f64.sub'](x7, x10)
            # x11
            x12 = l0
            # x11, x12
            x13 = ops['f64.add'](x11, x12)
            # x13
            l5 = x13
            #
            x14 = 2.0
            # x14
            x15 = l3
            # x14, x15
            x16 = ops['f64.mul'](x14, x15)
            # x16
            x17 = l4
            # x16, x17
            x18 = ops['f64.mul'](x16, x17)
            # x18
            x19 = l1
            # x18, x19
            x20 = ops['f64.add'](x18, x19)
            # x20
            l4 = x20
            #
            x21 = l5
            # x21
            l3 = x21
            #
            x22 = l2
            # x22
            x23 = 1
            # x22, x23
            x24 = ops['i32.sub'](x22, x23)
            # x24
            l2 = x24
            #
            x25 = l3
            # x25
            x26 = l3
            # x25, x26
            x27 = ops['f64.mul'](x25, x26)
            # x27
            x28 = l4
            # x27, x28
            x29 = l4
            # x27, x28, x29
            x30 = ops['f64.mul'](x28, x29)
            # x27, x30
            x31 = ops['f64.add'](x27, x30)
            # x31
            x32 = 4.0
            # x31, x32
            x33 = ops['f64.gt'](x31, x32)
            # x33
            if x33 != 0:
                pc = 3
                continue
            #
            pc = 2
            continue
        elif pc == 3:
            x0 = 0
            # x0
            return x0
        elif pc == 4:
            x0 = 1
            # x0
            return x0


# const inlining, inlining direct reads from locals
def func4_alt1(l0, l1, l2):
    l3 = 0.0 # f64
    l4 = 0.0 # f64
    l5 = 0.0 # f64

    pc = 0
    while True:
        if pc == 0:
            l3 = 0.0
            l4 = 0.0
            pc = 1
            continue
        elif pc == 1:
            pc = 2
            continue
        elif pc == 2:
            x3 = ops['i32.gt_s'](l2, 1)
            x4 = ops['i32.sub'](1, x3)
            if x4 != 0:
                pc = 4 # after block
                continue
            x7 = ops['f64.mul'](l3, l3)
            x10 = ops['f64.mul'](l4, l4)
            x11 = ops['f64.sub'](x7, x10)
            x13 = ops['f64.add'](x11, l0)
            l5 = x13
            x16 = ops['f64.mul'](2.0, l3)
            x18 = ops['f64.mul'](x16, l4)
            x20 = ops['f64.add'](x18, l1)
            l4 = x20
            l3 = l5
            x24 = ops['i32.sub'](l2, 1)
            l2 = x24
            x27 = ops['f64.mul'](l3, l3)
            x30 = ops['f64.mul'](l4, l4)
            x31 = ops['f64.add'](x27, x30)
            x33 = ops['f64.gt'](x31, 4.0)
            if x33 != 0:
                pc = 3
                continue
            pc = 2
            continue
        elif pc == 3:
            return 0
        elif pc == 4:
            return 1

# inlining of single-use temporaries that are result of op call that have
# no side effects
# TODO: can i somehow benefit just off the wat's tree-like form? or generate
# tree-based IR?
def func4_alt2(l0, l1, l2):
    l3 = 0.0 # f64
    l4 = 0.0 # f64
    l5 = 0.0 # f64

    pc = 0
    while True:
        if pc == 0:
            l3 = 0.0
            l4 = 0.0
            pc = 1
            continue
        elif pc == 1:
            pc = 2
            continue
        elif pc == 2:
            if ops['i32.sub'](1, ops['i32.gt_s'](l2, 1)) != 0:
                pc = 4 # after block
                continue
            l5 = ops['f64.add'](ops['f64.sub'](ops['f64.mul'](l3, l3), ops['f64.mul'](l4, l4)), l0)
            l4 = ops['f64.add'](ops['f64.mul'](ops['f64.mul'](2.0, l3), l4), l1)
            l3 = l5
            l2 = ops['i32.sub'](l2, 1)
            if ops['f64.gt'](ops['f64.add'](ops['f64.mul'](l3, l3), ops['f64.mul'](l4, l4)), 4.0) != 0:
                pc = 3
                continue
            pc = 2
            continue
        elif pc == 3:
            return 0
        elif pc == 4:
            return 1



# inlining functions from dict into code
def func4_alt3(l0, l1, l2):
    l3 = 0.0 # f64
    l4 = 0.0 # f64
    l5 = 0.0 # f64

    pc = 0
    while True:
        if pc == 0:
            l3 = 0.0
            l4 = 0.0
            pc = 1
            continue
        elif pc == 1:
            pc = 2
            continue
        elif pc == 2:
            if (1 - (1 if l2 > 1 else 0) & 0xFFFFFFFF) != 0:
                pc = 4 # after block
                continue
            l5 = (((l3 * l3) - (l4 * l4)) + l0)
            l4 = (((2.0 * l3) * l4) + l1)
            l3 = l5
            l2 = (l2 - 1) & 0xFFFFFFFF
            if ((l3 * l3) + (l4 * l4)) > 4.0:
                pc = 3
                continue
            pc = 2
            continue
        elif pc == 3:
            return 0
        elif pc == 4:
            return 1



# automatic structured generation based on wasm structure - naive, local,
# without analysis of whole function surroundings of blocks, besides knowing
# that we don't want to generate subblock handler if there's no subblocks
def func4_alt3(l0, l1, l2):
    l3 = 0.0 # f64
    l4 = 0.0 # f64
    l5 = 0.0 # f64
    br_target = None

    l3 = 0.0
    l4 = 0.0
    # block
    while True:
        # loop outer
        while True:
            # loop inner
            while True:
                if ((1 - (1 if l2 > 0 else 0)) & 0xFFFFFFFF) != 0:
                    br_target = 1
                    break

                l5 = (((l3 * l3) - (l4 * l4)) + l0)

                l4 = (((2.0 * l3) * l4) + l1)

                l3 = l5

                l2 = ((l2 - 1) & 0xFFFFFFFF)

                # if/else
                while True:
                    if ((l3 * l3) + (l4 * l4)) > 4.0:
                        return 0
                    # generic inner exit
                    break
                # generic subblock handler
                if br_target is not None:
                    if br_target == 0:
                        br_target = None
                    else:
                        br_target -= 1
                        break

                # generic block end
                break
            # loop inner handler
            if br_target is None:
                break
            elif br_target == 0:
                br_target = None
                continue
            else:
                br_target -= 1
                break
        # generic subblock handler
        if br_target is not None:
            if br_target == 0:
                br_target = None
            else:
                br_target -= 1
                break
        # generic block end
        break
    # no subblock handler in outermost scope, just the br_target reset
    br_target = None

    return 1


print(func4(1.0, 1.0, 0))
print(func4_alt1(1.0, 1.0, 0))
print(func4_alt2(1.0, 1.0, 0))
print(func4_alt3(1.0, 1.0, 0))

import dis
print(dis.dis(func4_alt3))
