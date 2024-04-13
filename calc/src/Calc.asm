.class Calc:Obj
.method $constructor
.local x,b,a
    const 3
    const 2
    const 4
    call Int:divide
    call Int:plus
    store a
    load a
    const "a = 4 / 2 + 3 => "
    call String:print
    pop
    call Int:print
    const "\n"
    call String:print
    pop
    pop
    const 2
    const 2
    load a
    call Int:divide
    call Int:plus
    store b
    load b
    const "b = a / 2 + 2 => "
    call String:print
    pop
    call Int:print
    const "\n"
    call String:print
    pop
    pop
    const 90
    const 0
    call Int:minus
    load a
    load b
    load b
    call Int:multiply
    call Int:multiply
    call Int:plus
    store x
    load x
    const "x = b * b * a + -90 => "
    call String:print
    pop
    call Int:print
    const "\n"
    call String:print
    pop
    pop
    load b
    load a
    load x
    call Int:multiply
    call Int:multiply
    const "x * a * b => "
    call String:print
    pop
    call Int:print
    const "\n"
    call String:print
    pop
    pop
    const nothing
    return 0