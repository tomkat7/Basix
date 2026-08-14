import os
import sys
import signal
import time
import executor as e
import parser as p
import glob
import shlex
import random

variables = {}
background_pids=[]
background_cmds=[]


def run(cmd):
    try:
        os.execvp(cmd[0], cmd)
    except FileNotFoundError:
        print(f'Error: Command "{cmd[0]}" was not found.', file=sys.stderr)
        os._exit(1)
    except PermissionError:
        print(f'Error: Permission denied: "{cmd[0]}"', file=sys.stderr)
        os._exit(1)


def cd(cmd):
    if len(cmd) == 2:
        try:
            os.chdir(os.path.expanduser(cmd[1]))
            return ("fake error", 0)
        except FileNotFoundError:
            print(f'Error: The directory "{cmd[1]}" does not exist.')
            return ("fake error", 256)
    else:
        os.chdir(os.path.expanduser("~"))
        return ("fake error", 0)


def execute(cmd,background=False):
    pid = os.fork()
    if pid == 0:
        if background:
                os.setpgid(pid, pid)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        run(cmd)
    else:
        if background:
            os.setpgid(pid, pid)
            cmd_normal=" ".join(cmd)
            background_pids.append(pid)
            background_cmds.append(cmd_normal)
        else:
            return os.waitpid(pid, 0)

def mytime(cmd,background,display_cmd):
    start = time.perf_counter()
    if cmd == "time":
        print("Error: Nothing to measure the time of.")
        return ("stupidity", 1)
    else:
        cmd = cmd.removeprefix("time ")
        cmd, operations = p.parser(cmd)
        if background:
            print("Error: Can't measure background tasks.")
            return ("even bigger stupidity", 1)
        else:
            e.run_parsed(cmd, operations)
        end = time.perf_counter()
        print(f"Elapsed time = {end - start:.3f}")
        return ("success", 0)

def expand_globs(cmd):
    cmd_part = ""
    cmd_globed = ""
    start = None
    quotes = False
    i = 0
    while i < len(cmd):
        if cmd[i] == '"':
            if not quotes:
                start = i          
                quotes = True
                i += 1
                continue
            else:
                end = i + 1       
                cmd_globed = cmd_globed + cmd[start:end]
                start = None
                quotes = False
                i = end
                continue
        if not quotes:
            if cmd[i] == " ":
                cmd_globed = cmd_globed + cmd_part + ""
                cmd_part = ""
            elif cmd[i] == "*" or cmd[i] == "?":
                w_start = cmd.rfind(' ', 0, i) + 1
                w_end = cmd.find(' ', i)
                if w_end == -1:
                    w_end = len(cmd)
                cmd_part = cmd[w_start:w_end]
                matches = glob.glob(cmd_part)
                if matches:
                    cmd_part = " ".join(matches)
                else:
                    pass 
                cmd_globed = cmd_globed + " " + cmd_part
                cmd_part = " "
                i = w_end
                continue
            else:
                cmd_part = " " + cmd_part + cmd[i]
        i += 1
    cmd_globed = cmd_globed + cmd_part
    cmd_globed = shlex.split(cmd_globed)
    return cmd_globed

def find_alias(alias):
    try:
        with open(os.path.expanduser("~/.basix/alias"),"r") as f:
            lines = f.readlines()
            for num, line in enumerate(lines):
                if line[0:line.index("=")-1] == alias:
                    return line[line.index("=")+1:].strip(), num
            return 0, -1
    except FileNotFoundError:
        return 0, -1
    

def add_alias(cmd):
    if len(cmd) != 3:
        print('Error: Command: "alias" must have 2 arguments.')
    else:
        if len(cmd[2].split()) != 1:
            print("Error: alias must only be 1 word")
        else:
            command = cmd[1]
            alias = cmd[2]
            path = os.path.expanduser("~/.basix/alias")

            result, line_num = find_alias(alias)

            try:
                with open(path, "r") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []

            if result != 0:
                print("Alias already exists. Replacing old one.")
                lines[line_num] = f"{alias} = {command} \n"
            else:
                lines.append(f"{alias} = {command} \n")

            with open(path, "w") as f:
                f.writelines(lines)


def expand_token(cmd):
    cmd_expanded = []
    for token in cmd:
        if token[:2] == "~/":
            token = os.path.expanduser(token)
            cmd_expanded.append(token)
        else:
            cmd_expanded.append(token)
    return cmd_expanded
            
def add_var(var_name,value,type="-s"):
    if type == "-i":
        try:
            variables[var_name] = int(value) 
        except ValueError:
            print(f'Error: "{value}" is not a number.')
    elif type == "-f":
        try:
            variables[var_name] = float(value) 
        except ValueError:
            print(f'Error: "{value}" is not a number.')
    else:
        variables[var_name] = value
        if type != "-s":
            print(f"Warning: Unknown flag '{type}'. Defaulting to string.")


def replace_var(cmd):
    cmd_str = []
    cmd_og = []
    for token in cmd:
        if token[0] == "$":
            token = token.removeprefix("$")
            if token == "RANDOM":
                cmd_str.append(str(random.randint(0, 99999)))
                cmd_og.append(random.randint(0, 99999))
            elif token == "?":
                cmd_str.append(str(e.exit_code))
                cmd_og.append(e.exit_code)
            else:
                try:
                    cmd_str.append(str(variables[token]))
                    cmd_og.append(variables[token])
                except KeyError:
                    print(f'Error: Undefined variable: "${token}"')
        else:
            cmd_str.append(token)
            cmd_og.append(token)
    return cmd_str, cmd_og

def del_var(var):
    var = var.removeprefix("&")
    if var in variables:
        variables.pop(var)
    else:
        print("Error: This variable doesn't exist.")

def evaluate(cmd):
    if "=" in cmd:
        eq_index = cmd.index("=")
        if cmd[-1].startswith("-"):
            expression = cmd[eq_index+1:-1]
            flag = cmd[-1]
        else:
            expression = cmd[eq_index+1:]
            flag = "-s"

        expression = replace_var(expression)[1]
        i = 0
        result = expression[0]
        while i < len(expression)-2:
            try:
                if expression[i+1] == "+":
                    result = result + expression[i+2]
                    i = i + 2
                elif expression[i+1] == "-":
                    result = result - expression[i+2]
                    i = i + 2
                elif expression[i+1] == "*":
                    result = result * expression[i+2]
                    i = i + 2
                elif expression[i+1] == "/":
                    result = result / expression[i+2]
                    i = i + 2                    
            except TypeError:
                expr_str = []
                for value in expression[i:i+3]:
                    expr_str.append(str(value))
                print(f'Error: Cannot evaluate operation: {" ".join(expr_str)}')
                return None, None
        return result, flag
    else:
        print("Error: No '=' sign was found.")
        return None, None
    