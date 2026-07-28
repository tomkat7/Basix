# MyShell

A Unix shell built from scratch in Python — using raw `fork`, `exec`, and `dup2` syscalls directly, with **no `subprocess` module**. The goal was to actually understand how a shell works under the hood: process creation, file descriptor inheritance, pipes, signal handling, and job control — not just call a library that does it for you.

## Installation

```bash
git clone https://github.com/tomkat7/MyShell.git (or download MyShell.zip from releases)
cd MyShell
chmod +x mysh.py
./mysh.py
```

Requires Python 3 and a Linux (or other POSIX-compliant) system — this shell relies on `os.fork()`, `os.execvp()`, and Unix signal handling, which are not available on Windows.

To exit the shell, type `exit`.

## Features & Syntax

### Running commands
```
ls -la
```
Standard command execution via `fork` + `execvp`.

### Built-ins
```
cd [directory]      # bare `cd` goes to home directory, supports ~ expansion
jobs                 # list currently running background jobs
```

### Piping
```
ls | grep .py
cmd1 | cmd2 | cmd3   # any number of commands
```

### Redirection
```
ls > out.txt         # truncate/overwrite
ls >> out.txt        # append
sort < names.txt     # input redirection
```

### Command chaining
```
cmd1 && cmd2          # run cmd2 only if cmd1 succeeds
cmd1 || cmd2          # run cmd2 only if cmd1 fails
cmd1 && cmd2 && cmd3  # chains of arbitrary length are supported
```

### Timing
```
time ls
time ls | grep .py    # times the whole pipeline/chain, not just the first command
```

### Background jobs
```
sleep 30 &
```
Runs the command without blocking the shell. Background jobs run in their own process group, so they are not killed by Ctrl+C at the prompt. Completion is reported the next time the prompt refreshes:

```
[12345]+ Done sleep 30
```
### Combined operators
Pipes, redirects, and chains can now be freely combined in a single command:

```cat < in.txt | grep foo > out.txt && echo done
```
### Backgrounding chains
Adding `&` to the end of a full chain backgrounds the *entire* chain as one job,
not just the last command:

```
sleep 2 && echo done1 || echo done2 &
```

### Scripts
Scripts are supported. To run a script with MyShell, add the shebang with the path of where `mysh.py` is on top of the script file, for example:

```
#!/home/user/mysh.py
```

Then, run the script with `./mysh.py script.sh`

### Ctrl+C
Cancels the currently running foreground command without killing the shell itself.

## Known Limitations

These are documented, intentional gaps — not oversights:

- **No wildcard/glob expansion**: `ls *.txt` will not expand `*.txt` — the literal string is passed to the command. Deliberately left unimplemented rather than shipping a version that mishandles filenames with spaces.
- **Background jobs cannot be combined with `time`, or `cd`**: `&` is only supported as the terminator of a single, non-chained command.
- **No environment variable support**: no `export`, no `$VAR` expansion.
- **No `fg`/`bg`**: background jobs can be listed with `jobs` but not brought back to the foreground once started.
- **`cd` cannot be used inside a pipe or chain** (e.g. `cd dir && ls` is not supported)
  It must run standalone, since changing directory only makes sense in the shell's
  own process, not a forked child.


## Project Structure

- `mysh.py` — main loop, prompt, input dispatch
- `functions.py` — built-ins (cd, time)
- `executor.py` — executes the parsed command (chains, pipes, and plain command are all processed here)
- `parser.py` — parses the raw command string into a nested lists for the executor to execute.  

## Why no `subprocess`?

Using `subprocess` would have solved everything in a few lines, but that defeats the point. This project is about understanding `fork`, `exec`, file descriptor inheritance, and signal handling at the syscall level, not wrapping them.