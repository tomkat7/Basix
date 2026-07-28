import os
import sys
import signal
import time
import executor as e
import parser as p


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

