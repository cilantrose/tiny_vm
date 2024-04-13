.class Calc:Obj
.method $constructor
    const 2
    const 2
    const 4
    call Int:divide
    call Int:plus
    const "4 / 2 + 2 = "
    call String:print
    pop
    call Int:print
    const "\n"
    call String:print
    pop
    pop
    const 4
    const 8
    const 8
    call Int:multiply
    const 9
    const 3
    const 12
    call Int:multiply
    call Int:multiply
    call Int:plus
    call Int:divide
    const "(8 * 8 + (12 * 3) * 9) / 4 = "
    call String:print
    pop
    call Int:print
    const "\n"
    call String:print
    pop
    pop
    const nothing
    return 0
