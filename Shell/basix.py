#!/usr/bin/env python3
import atexit
import getpass
import os
import readline
import shlex
import socket
import signal
import functions as f
import parser as p
import executor as e
import sys

script_mode = len(sys.argv) > 1

if script_mode:
    script_file = open(sys.argv[1])

shell_pgid = os.getpgrp()

def get_next_cmd():
    username = getpass.getuser()
    hostname = socket.gethostname()
    purple = "\001\033[35m\002"
    green = "\001\033[32m\002"
    blue = "\001\033[34m\002"
    default = "\001\033[0m\002"
    
    if script_mode:
        while True:
            line = script_file.readline()
            if line == "":
                return None
            line = line.rstrip("\n")
            if line.strip() == "" or line.strip().startswith("#"):
                continue
            return line
    else:
        print(f"{purple}╭─ {green}{username}{purple}@{green}{hostname}{purple}:{blue}{os.getcwd()}")
        return input(f"{purple}╰─{default}$ ")



purple = "\001\033[35m\002"
green = "\001\033[32m\002"
blue = "\001\\e[0;96m\002"
default = "\001\033[0m\002"

background_finished=[]

config_dir = os.path.expanduser("~/.basix")
os.makedirs(config_dir, exist_ok=True)

signal.signal(signal.SIGINT, signal.SIG_IGN)
signal.signal(signal.SIGTTOU, signal.SIG_IGN)

if not script_mode:
    histfile = os.path.expanduser("~/.basix/basix_history.txt")
    try:
        readline.read_history_file(histfile)
    except FileNotFoundError:
        pass
    atexit.register(readline.write_history_file, histfile)

cmd = get_next_cmd()


while cmd != "exit" and cmd != None:
    if cmd == "":
        print()
    else:

        cmd_split = shlex.split(cmd)
        alias_result = f.find_alias(cmd_split[0])[0]

        if alias_result != 0:
            cmd = alias_result
            cmd_split = shlex.split(cmd)

        if cmd_split[-1] == "&":
            cmd_split.pop(-1)
            cmd=cmd.removesuffix("&")
            background=True

        else:
            background=False

        display_cmd = cmd 

        if cmd_split[0] == "time":
            f.mytime(cmd,background,display_cmd)

        elif cmd == "alias show":
                print("---=== Aliases ===---")
                cmd, operations = p.parser(f'cat {os.path.expanduser("~/.basix/alias")}')
                e.run_parsed(cmd, operations)    

        elif cmd_split[0] == "alias":
            f.add_alias(cmd_split)
    
        elif cmd == "jobs":
            if len(f.background_pids) == 0:
                print("No background jobs running.")
            else:
                print("-------======= Running Jobs ======= -------")
                for i in range(len(f.background_pids)):
                    print(f"[{f.background_pids[i]}]: {f.background_cmds[i]}")


        elif cmd_split[0] == "cd":
            f.cd(cmd_split)

        elif cmd_split[0] == "fg":
            if len(cmd_split) != 2:
                print("Please provide a PID after fg")
            else:
                try:
                    int(cmd_split[1])
                    is_int = True
                except ValueError:
                    print("Enter a valid PID")
                    is_int = False
                if is_int:    
                    if int(cmd_split[1]) in f.background_pids:
                        try:
                            os.tcsetpgrp(sys.stdin.fileno(), int(cmd_split[1]))
                            os.waitpid(int(cmd_split[1]),0)
                            os.tcsetpgrp(sys.stdin.fileno(),shell_pgid)
                            index = f.background_pids.index(int(cmd_split[1]))
                            f.background_cmds.pop(index)
                            f.background_pids.pop(index)
                        except OSError as e:
                            print(f"fg: no such job ({e})", file=sys.stderr)
                    else:
                        print("PID not found in background processes")
       
        elif cmd[:7] == "var del":
            if len(cmd_split) == 3:
                f.del_var(cmd_split[2])
            else:
                print("Error: Please provide one variable to delete.")                
       
        elif cmd_split[0] == "var":
            if len(cmd_split) <  4:
                print('Syntax Error: "var" requires a name, "=", and a value (e.g. var x = 5)')
            else:
                value, flag = f.evaluate(cmd_split)
                var_name = cmd_split[1]
                if value != None:
                    f.add_var(var_name,value,flag)
            
        else:
            cmd, operations = p.parser(cmd)
            if background:
                pid = os.fork()
                if pid == 0:
                    os.setpgid(pid,pid)
                    e.run_parsed(cmd, operations)
                    os._exit(0)
                else:
                    f.background_pids.append(pid)
                    f.background_cmds.append(display_cmd)
            else:
                e.run_parsed(cmd, operations)


    for pid in f.background_pids:
        if os.waitpid(pid, os.WNOHANG) != (0, 0):
            background_finished.append(pid)

    for pid in background_finished:
        index = f.background_pids.index(pid)
        print(f"[{pid}]+ Done {f.background_cmds[index]}")
        f.background_pids.pop(index)
        f.background_cmds.pop(index)

    background_finished=[]
    cmd = get_next_cmd()
