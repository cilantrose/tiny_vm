import os, pathlib, shutil, subprocess, sys, functools

from lark import Lark, Transformer, v_args

grammar = """
    ?start: expr ";"
          | SH_COMMENT  -> comment
          
    ?expr: NAME "=" op                  -> assign_var
          | NAME ":" NAME "=" op        -> typed_var
          | NAME "." NAME "(" ")"       -> method
          | NAME "." NAME "(" STR ")"   -> method_args
          
    ?printable: NAME
          | STR

    ?op: atom
          | op "+" op   -> add
          | op "-" op   -> sub
          | op "*" op   -> mul
          | op "/" op   -> div

    ?atom: NUMBER       -> const
          | STR         -> const
          | NAME        -> var
          | "-" atom    -> neg
          | "(" op ")"
    
    %import common.ESCAPED_STRING -> STR
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    %import common.SH_COMMENT
    
    %ignore WS_INLINE
"""
ROOT = ".."


@v_args(inline=True)  # Affects the signatures of the methods
class CalculateTree(Transformer):
    type_context = "Int"
    add     = lambda self, left, right: right + left + [f"call {self.type_context}:plus"]
    sub     = lambda self, left, right: right + left + [f"call {self.type_context}:minus"]
    mul     = lambda self, left, right: right + left + [f"call {self.type_context}:multiply"]
    div     = lambda self, left, right: right + left + [f"call {self.type_context}:divide"]
    neg     = lambda self, val: val + ["const 0"] + ["call Int:minus"]
    print   = lambda self, val: [f"load {val}", f"call {self.program_vars[val]}:print", "pop"] if val in \
              self.program_vars else [f"const {val}", f"call String:print", "pop"]
    const   = lambda self, val: [f"const {val}"]
    comment = lambda self, val: None

    def __init__(self, program_vars: dict):
        super().__init__()
        self.program_vars = program_vars

    def method(self, name, method):
        if name in self.program_vars:
            return [f"load {name}", f"call {self.program_vars[name]}:{method}", "pop"]
        else:
            print(f"Error on line {current[0]}: variable {name} not declared")
            cleanup()

    def var(self, name):
        if self.program_vars.__contains__(name):
            self.type_context = self.program_vars[name]
        else:
            print(f"Error on line {current[0]}: variable {name} not declared")
            cleanup()
        return [f"load {name}"]

    def assign_var(self, name, value):
        # no type inference, just assume integer if no explicit type specified
        return self.typed_var(name, "Int", value)

    def typed_var(self, name, t, value):
        value += [f"store {name}"]
        # keep track of var type
        if not self.program_vars.__contains__(name):
            self.program_vars[str(name)] = t
        return value


def main():
    global current
    vars, expressions, src, name, current= {}, [], None, None, (0, None)
    parse = Lark(grammar, parser="lalr", transformer=CalculateTree(vars)).parse

    for arg in sys.argv:
        if arg.startswith("-src="):
            src = arg.removeprefix("-src=") + ".quack"
        elif arg.startswith("-out="):
            name = arg.removeprefix("-out=")

    if src is None:
        print("No source path provided")
        return
    if name is None:
        name = "a"
        print("No output name provided, using default")
    with open(src, "r") as f:
        for line in f:
            current = (current[0] + 1, line.strip())
            expressions.append((current[1], parse(current[1])))

    os.makedirs("src", exist_ok=True)
    os.makedirs("OBJ", exist_ok=True)
    with open(f"src/{name}.asm", "w") as f:
        # write file header
        f.write(f".class {name}:Obj\n.method $constructor\n.local {functools.reduce(lambda a, b: f'{a},{b}', vars)}\n")
        for expression in expressions:
            if expression[1] is not None:
                for asm in expression[1]:
                    f.write(f"    {asm}\n")
            # generic print statements formatted as expression => result
        f.write("    return 0")

    src = pathlib.Path(f"src/{name}.asm")
    obj = pathlib.Path(f"{'' if sys.argv.__contains__('--local') else '.'}./OBJ/{name}.json")
    for objfile in ["Bool.json", "Int.json", "Nothing.json", "Obj.json", "String.json"]:
        shutil.copyfile(pathlib.Path("../OBJ/" + objfile), pathlib.Path("./OBJ/" + objfile))
    for asmreq in ["asm.conf", "opdefs.txt"]:
        shutil.copyfile(pathlib.Path("../" + asmreq), pathlib.Path("./" + asmreq))
    try:
        proc = subprocess.run(["python3", "../assemble.py", src, obj], text=True)
        proc.check_returncode()
    except subprocess.CalledProcessError:
        sys.stderr.write("Assembler failed to produce object code")


def cleanup():
    exit(1)


if __name__ == '__main__':
    main()
