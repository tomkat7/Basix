## Day 1 - 14/06/26
- Calling child processes, replacing with programs (Basic command running functionality)
- Made cd work
- Made pipes for 2 commands
- Error detection
- Cursor movement (import readline)
- Code cleanup with functions
- time command to measure ellapsed time
- pipe error handling

## Day 2 - 15/06/26
- Multiple pipes support
- Persistant history
- Redirections
- Time compatibility for Redirections

## Day 3 - 16/06/26
- Shell now interprets "" as one argument
- Correct error handling in redirect function

## Day 4 - 28/06/26
- time command doesn't get incorrectly called if the word time exists in command
- Code cleanup

## Day 5 - 02/07/26
- Shell now supports pipes and a redirection in the same command.
- Implemented && and || command chaining
- Fixed redirect() crashing on invalid input like >>>

## Day 6 - 06/07/26
- Multiple command chains are now supported.
- The history file is saved in the user's home directory instead of an absolute path that might not exist.
- Implemented input redirections.
- Chaining supports all operations, like pipes, redirections, input redirections etc.
- Implemented ctrl+c signal handling
- Fixed Incorrect calling of pipe() and redirect() functions 
- Added error handling for os.open() failures

## Day 7 - 07/07/26
- Implemented background jobs.

## Day 8 - 08/07/26
- Isolated background jobs from the main shell process group, so ctrl+c will not affect them.
- Added a `jobs` command, which shows all running background jobs.

## Day 9 - 15/07/26
- Improved the input UI and README

## Day 10 - 17/07/26
- Made a better parser (not added to the main loop yet)

## Day 11 - 20/07/26
- Started making an executor which will take the new command format from the new parser and execute it.

## Day 12 - 22/07/26
- Completed executor
- Implemented the new executor in the main `mysh.py` file. 
- Removed unused code in `functions.py`
- Added support for redirections inside pipes.

## Day 13 - 23/07/26
- Fixed a bug where commands that needed to hold the terminal (like `watch` or `sudo pacman -Syu`) froze the shell and executed in the background instead of foreground.

## Day 14 - 28/07/26
- Added support for scripts
- Moved the history file to `~/.mysh_config/`
- Added fg command

## Day 15 - 03/08/26
- Added support for wildcards (`*` and `?`)

## Day 16 - 10/08/26
- Changed name from MyShell to Basix
- Added aliases
- Added alias show command

## Day 17 - 11/08/26
- Added `;` operator for command chains
- Commands that include `~/` will now expand to the user's home folder.
- Organised github repo and README.md