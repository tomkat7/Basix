# Basix
A Linux shell built from scratch in Python — using raw `fork`, `exec`, and `dup2` syscalls directly, with **no `subprocess` module**. The goal was to actually understand how a shell works under the hood: process creation, file descriptor inheritance, pipes, signal handling, and job control.

## Installation

### Method 1: Using git

```bash
git clone https://github.com/tomkat7/Basix.git 
cd Basix/Shell
chmod +x basix.py
./basix
```
### Method 2: Download from releases

1. Download the latest `basix.zip` from the releases.
2. Extract the zip
3. Give execition permissions with `chmod +x basix.py`
4. Run with `./basix.py`  

Requires Python 3 and a Linux (or other POSIX-compliant) system — this shell relies on `os.fork()`, `os.execvp()`, and Unix signal handling, which are not available on Windows.

To exit the shell, type `exit`.

## Syntax and Features

- Fork/exec-based execution (no subprocess)
- Pipes, redirection (>, >>, <), chaining (&&, ||, ;) — freely combinable
- Background jobs, fg, jobs — full job control with terminal handoff
- Built-in cd, time, alias
- Wildcard and tilde expansion
- Script mode with #! support
- Persistent history
- Variables creation - deletion
- Mathematical operations between variables

For the full list of features and the detailed syntax, view [Syntax.md](Docs/Syntax.md)

## Project Structure

<pre>
Basix
┃
┣ .gitignore
┣ README.md
┣ <a href="Shell/">Shell</a>
┃   ┣ <a href="Shell/basix.py">basix.py</a>      # main shell loop
┃   ┣ <a href="Shell/functions.py">functions.py</a>  # Built-ins (cd, time, find_alias, add_alias, expand_globs, etc.)
┃   ┣ <a href="Shell/parser.py">parser.py</a>     # Processes the raw command into nested lists
┃   ┗ <a href="Shell/executor.py">executor.py</a>   # Takes the nested lists and executes the commands
┗ <a href="Docs/">Docs</a>
    ┣ <a href="Docs/Progress.md">Progress.md</a>   # Progress log
    ┗ <a href="Docs/Syntax.md">Syntax.md</a>     # Detailed syntax and feature list
</pre>


## Configuration
Basix's history and aliases files live inside `~/.basix/`.
- The history file is named `basix_history`
- The file holding aliases is named `alias`

If a config file is introduced in a future update, it will also be placed in that folder.

## Why no `subprocess`?

Using `subprocess` would have solved everything in a few lines, but that defeats the point. This project is about understanding `fork`, `exec`, file descriptor inheritance, and signal handling at the syscall level, not wrapping them.
