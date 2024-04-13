import os
import pathlib
import shutil
import subprocess
import sys

from lark import Lark, Transformer, v_args, Tree

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
    number = int


def install_prereqs():
    for objfile in ["Bool.json", "Int.json", "Nothing.json", "Obj.json", "String.json"]:
        origin = pathlib.Path("../OBJ/" + objfile)
        copied = pathlib.Path("./OBJ/" + objfile)
        shutil.copyfile(origin, copied)
    for asmreq in ["asm.conf", "opdefs.txt"]:
        origin = pathlib.Path("../" + asmreq)
        copied = pathlib.Path("./" + asmreq)
        shutil.copyfile(origin, copied)


def main():
    parser = Lark(grammar, parser="lalr", transformer=CalculateTree())
    asm = []

    with open("calc.txt", "r") as f:
        for line in f:
            asm += parse_line(parser.parse, line.strip())

    asm.append("const nothing")
    asm.append("return 0")
    os.makedirs("src", exist_ok=True)
    os.makedirs("OBJ", exist_ok=True)
    with open("src/Calc.asm", "w") as f:
        f.write(".class Calc:Obj\n")
        f.write(".method $constructor\n")
        for line in asm:
            f.write(f"    {line}\n")
    src = pathlib.Path("src/Calc.asm")
    obj = pathlib.Path(f"{'' if sys.argv.__contains__('--local') else '.'}./OBJ/Calc.json")
    install_prereqs()
    try:
        proc = subprocess.run(["python3", "../assemble.py", src, obj], text=True)
        proc.check_returncode()
    except subprocess.CalledProcessError:
        sys.stderr.write("Assembler failed to produce object code")


def parse_line(calc, expression):
    asm = []
    traverse(calc(expression), {"add": "plus", "sub": "minus", "mul": "multiply", "div": "divide"}, asm)
    asm.append(f'const "{expression} = "')
    asm.append("call String:print")
    asm.append("pop")
    asm.append("call Int:print")
    asm.append('const "\\n"')
    asm.append("call String:print")
    asm.append("pop")
    asm.append("pop")
    return asm


def traverse(node, translate, asm):
    if isinstance(node.children[1], int):
        asm.append(f"const {node.children[1]}")
    if isinstance(node.children[0], Tree):
        traverse(node.children[0], translate, asm)
    else:
        asm.append(f"const {node.children[0]}")
    if isinstance(node.children[1], Tree):
        traverse(node.children[1], translate, asm)
    asm.append("call Int:" + translate[node.data])


if __name__ == '__main__':
    main()

