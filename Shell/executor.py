import os
import functions as f
import signal
import sys
import shlex

cmd = "grep py < test.txt && echo Done"


def run_stage(cmd, redirects, stdin_fd=None, stdout_fd=None,):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if stdin_fd != None:
        os.dup2(stdin_fd,0)
        os.close(stdin_fd)

    if stdout_fd != None:
        os.dup2(stdout_fd,1)
        os.close(stdout_fd)

    for operator, filename in redirects:
        if operator == ">":
            try:
                file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
            except OSError as e:
                print(f"Error: {e.strerror}: '{filename}'", file=sys.stderr)
                os._exit(1)
            os.dup2(file_fd, 1)
            os.close(file_fd)
        elif operator == ">>":
            try:
                file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
            except OSError as e:
                print(f"Error: {e.strerror}: '{filename}'", file=sys.stderr)
                os._exit(1)
            os.dup2(file_fd, 1)
            os.close(file_fd)
        elif operator == "<":
            try:
                file_fd = os.open(filename, os.O_RDONLY)
            except OSError as e:
                print(f"Error: {e.strerror}: '{filename}'", file=sys.stderr)
                os._exit(1)
            os.dup2(file_fd, 0)
            os.close(file_fd)
    if not cmd:
        print("Error: Broken pipeline")
        os._exit(1)
    else:
        f.run(cmd)

def run_segment(segment):
    pipes = [os.pipe() for _ in range(len(segment)-1)]
    pids = []
    for i, stage in enumerate(segment):
        cmd, redirects = stage
        if i > 0:
            stdin_fd = pipes[i-1][0]
        else:
            stdin_fd = None

        if i < len(segment) - 1:
            stdout_fd = pipes[i][1]
        else:
            stdout_fd = None
        pid = os.fork()
        pids.append(pid)
        if pid == 0:
            try:
                for j, (r, w) in enumerate(pipes):
                    if j != i - 1:
                        os.close(r)
                    if j != i:
                        os.close(w)
                run_stage(cmd, redirects, stdin_fd, stdout_fd)
            except Exception as ex:
                print(f"Error: {ex}", file=sys.stderr)
                os._exit(1)
    for r, w in pipes:
        os.close(r)
        os.close(w)
    last_status = None
    for i, pid in enumerate(pids):
        status = os.waitpid(pid, 0)
        if i == len(pids) - 1:
            last_status = status
    return last_status

def run_parsed(cmd,operations):
    for i, segment in enumerate(cmd):
        status = run_segment(segment)
        if os.WIFEXITED(status[1]):
            exit_code = os.WEXITSTATUS(status[1])
            if len(operations) > 0:
                if i > len(operations) - 1:
                    i = i - 1
                if operations[i] == "||":
                    if exit_code != 0:
                        continue
                    else:
                        break
                elif operations[i] == "&&":
                    if exit_code == 0:
                        continue
                    else:
                        break
                elif operations[i] == ";":
                    continue
