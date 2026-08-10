# Basix
A Linux shell built from scratch in Python — using raw `fork`, `exec`, and `dup2` syscalls directly, with **no `subprocess` module**. The goal was to actually understand how a shell works under the hood: process creation, file descriptor inheritance, pipes, signal handling, and job control.

## Installation

```bash
git clone https://github.com/tomkat7/Basix.git (or download Basix.zip from releases)
cd Basix
chmod +x basix
./basix
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
cd [directory]            # bare `cd` goes to home directory, supports ~ expansion
jobs                      # list currently running background jobs
time [command]            # measure the time a command takes to complete
alias "command" "alias"   # add an alias
alias show                # Show all aliases.
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

```
cat < in.txt | grep foo > out.txt && echo done
```
### Backgrounding chains
Adding `&` to the end of a full chain backgrounds the *entire* chain as one job,
not just the last command:

```
sleep 2 && echo done1 || echo done2 &
```

### Foregrounding a background process
You can use `fg {pid}` to foreground a background process.
For example if `sudo dnf upgrade` is running in the background with PID = 24134, you can bring it to foreground with 
```
fg 24134
``` 
*Hint: To see all background processes with their PIDs, run `jobs`* 

### Scripts
Scripts are supported. To run a script with Basix, add the shebang with the path of where `basix` is on top of the script file, for example:

```
#!/home/user/basix
```

Then, run the script with `./basix script.sh`

### Ctrl+C
Cancels the currently running foreground command without killing the shell itself.

### Glob / Wildcard expansion
Globs and wildcards get expanded to matching files. If no matches are found, they are left as a string.

### Aliases
To add an alias, type `alias "command" "alias command"`.
For example, to make an alias for `sudo dnf upgrade && flatpak update`, you can use

```
alias "sudo dnf upgrade && flatpak update" "upd"
```

To view all aliases, run `alias show`

Note:
- The `alias` command always needs 2 arguments, the command and the alias. 
- The command needs to be wrapped in quotes. 
- If you try to add an already existing alias, the new one will replace the old one.
 
## Known Limitations

These are documented, intentional gaps — not oversights:

- **No environment variable support**: no `export`, no `$VAR` expansion.
- **`cd` cannot be used inside a pipe or chain** (e.g. `cd dir && ls` is not supported)
  It must run standalone, since changing directory only makes sense in the shell's
  own process, not a forked child.


## Project Structure

- `basix.py` — main loop, prompt, input dispatch
- `functions.py` — built-ins (cd, time, add_alias, find_alias, expand_globs etc)
- `executor.py` — executes the parsed command (chains, pipes, and plain command are all processed here)
- `parser.py` — parses the raw command string into a nested lists for the executor to execute.  

## Configuration
Basix's history and aliases files live inside `~/.basix/`.
- The history file is named `basix_history`
- The file holding aliases is named `alias`
If a config file is introduced in a future update, it will also be placed in that folder.

## Why no `subprocess`?

Using `subprocess` would have solved everything in a few lines, but that defeats the point. This project is about understanding `fork`, `exec`, file descriptor inheritance, and signal handling at the syscall level, not wrapping them.
