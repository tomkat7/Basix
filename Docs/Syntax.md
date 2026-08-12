#### Features & Syntax

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
cmd1 ; cmd2           # run cmd2 regardless of whether cmd1 failed or succeded
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
#!/home/user/basix.py
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
 
### Variables
To add a new vaiable, use the `var` command.
**`var` command use:**

`var` takes 2 arguments.
- The variable name and the value
- A flag to specify the value's data type.
  Possible flags are: `-i` (integer), `-f` (float), `-s` (string)
  _Note: The flag is optional. If no flag is provided, the default will be string._

**Command template:**

```
var [Variable_name] = [Value] -flag
```

#### Rules:
- The variable name, the equals sign ("=") and the variable value must all be seperated by spaces.
- If a non-existent flag is provided, the default (string) will be used instead.

To view the value of a variable, use `echo $variable_name`.

**Built-in variables:**
- `$RANDOM`: Returns a random number between 0 and 99999.
- `$?`: Returns the error code from the last command executed (0: Success, 1: Failure) 