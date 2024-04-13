import os, pathlib, shutil, subprocess, sys, functools

from lark import Lark, Transformer, v_args

grammar = """
    ?start: sum
          | NAME "=" sum    -> assign_var

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""
ROOT = ".."


@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):
    add = lambda x, left, right: right + left + ["call Int:plus"]
    sub = lambda x, left, right: right + left + ["call Int:minus"]
    mul = lambda x, left, right: right + left + ["call Int:multiply"]
    div = lambda x, left, right: right + left + ["call Int:divide"]
    # this is the worst code I have ever written
    neg = lambda x, val: val + ["const 0"] + ["call Int:minus"]
    var = lambda x, name: [f"load {name}"]
    number = lambda x, val: [f"const {val}"]

    def __init__(self, program_vars: set):
        super().__init__()
        self.vars = {}
        self.program_vars = program_vars

    def assign_var(self, name, value):
        # dumb hack to keep the value of stored var for future computation
        value += [f"store {name}", f"load {name}"]
        if not self.program_vars.__contains__(name):
            self.program_vars.add(str(name))
        self.vars[name] = value
        return value


def main():
    vars = set()
    calc = Lark(grammar, parser="lalr", transformer=CalculateTree(vars)).parse
    expressions = []

    with open("calc.txt", "r") as f:
        for line in f:
            expressions.append((line.strip(), calc(line.strip())))

    os.makedirs("src", exist_ok=True)
    os.makedirs("OBJ", exist_ok=True)
    with open("src/Calc.asm", "w") as f:
        # write file header
        f.write(f".class Calc:Obj\n.method $constructor\n.local {functools.reduce(lambda a, b: f'{a},{b}', vars)}\n")
        for expression in expressions:
            for asm in expression[1]:
                f.write(f"    {asm}\n")
            # generic print statements formatted as expression => result
            f.write(f'    const "{expression[0]} => "\n    call String:print\n    pop\n')
            f.write(f"    call Int:print\n")
            f.write(f'    const "\\n"\n    call String:print\n    pop\n    pop\n')
        f.write("    return 0")

    src = pathlib.Path("src/Calc.asm")
    obj = pathlib.Path(f"{'' if sys.argv.__contains__('--local') else '.'}./OBJ/Calc.json")
    for objfile in ["Bool.json", "Int.json", "Nothing.json", "Obj.json", "String.json"]:
        shutil.copyfile(pathlib.Path("../OBJ/" + objfile), pathlib.Path("./OBJ/" + objfile))
    for asmreq in ["asm.conf", "opdefs.txt"]:
        shutil.copyfile(pathlib.Path("../" + asmreq), pathlib.Path("./" + asmreq))
    try:
        proc = subprocess.run(["python3", "../assemble.py", src, obj], text=True)
        proc.check_returncode()
    except subprocess.CalledProcessError:
        sys.stderr.write("Assembler failed to produce object code")


if __name__ == '__main__':
    main()

