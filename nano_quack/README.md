##Nano Quack
___


Usage: 
1. Create a `.quack` file.
2. Write a sequence of assignments. 
3. Run `python3 nano_parse.py -src=<your_program_name>` to generate some assembly in `src/a.asm` and a runnable `a.json` 
   in `../OBJ`. Running with the `--local` flag will instead write the output to 
   `OBJ/a.json`. `a.json` is a default name, but a custom name can be specified with the `-out`
   argument (i.e. `-out=Program` will output to `Program.asm` and `Program.json`).


Note: The `nano_quack` directory contains a test program `test.quack` to be compiled. The expected output of this quack
program is "2 + 1 + 2 + 2 = 7".