#  .jit - Version Control System

`.jit` is a custom command-line version control system built in Python, designed to manage and track file changes within a specified directory. With functionality inspired by Git, `.jit` offers a lightweight and easy-to-use alternative, perfect for learning how version control works under the hood or for small-scale versioning needs in local environments.

---

##  Overview

`.jit` allows users to initialize repositories, track and commit changes, rollback to previous versions, and manage user settings — all from the command line. It’s an educational, minimal VCS that teaches you the internal logic of tools like Git.

---

##  Features

-  **Easy Initialization**: Quickly start version tracking in any directory.
-  **File Tracking**: Add, commit, and manage file changes.
-  **User Management**: Set and display the author name for commits.
-  **Commit History**: View logs with commit metadata and file snapshots.
-  **Rollback**: Remove last commit or checkout a specific version.
-  **Status Check**: See modified, staged, and untracked files.
-  **File Integrity**: MD5 hashing ensures accurate file tracking.
-  **Base64 Storage**: File contents are stored in encoded format.
-  **Cross-Platform**: Works on Windows, macOS, and Linux.
-  **Robust Error Handling**: Graceful fallbacks for invalid inputs or missing files.

---

##  Installation

1. **Run** or use `python main.py` from terminal.
2. **Specify** the directory where you want to use `.jit`.

No external dependencies required for basic usage.

---

##  Usage Guide

###  Initial Setup

When you launch `.jit`, it prompts you to enter a directory path. This is the working directory where all version control operations will be performed. A hidden folder `.jit` is created to manage internal data.

---

##  Command List

| Command                         | Description                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| `help`                           | Displays a list of all available commands.                                 |
| `location`                       | Shows the current working directory path.                                  |
| `init`                           | Initializes `.jit` in the current directory.                              |
| `status`                         | Displays changes: staged, modified, or untracked files.                    |
| `add <filename>`                 | Adds a file to the staging area.                                           |
| `rmadd`                          | Removes all files from the staging area.                                   |
| `commit -m "<message>"`          | Commits staged files with a message and generates a unique hash.          |
| `rmcommit`                       | Removes the latest commit and restores the previous commit's state.       |
| `checkout <commit_hash>`         | Reverts the system to a specific commit using its unique hash.            |
| `log`                            | Displays a history of commits with timestamp and details.                  |
| `user set <name>`                | Sets the username for future commits.                                      |
| `user show`                      | Displays the current username.                                             |
| `push "<destination>"`           | Pushes committed files to a specified directory (basic sync mechanism).   |
| `clear`                          | Clears the terminal screen.                                               |
| `ls`                             | Lists all files and folders in the current working directory.             |


---

##  Internal Architecture

- **`.jit/objects/commits.json`** – Stores a list of all commit data (hash, message, time, files).
- **`.jit/objects/staged_files.json`** – Stores metadata of added but uncommitted files.
- **`.jit/objects/files_md5_hash.json`** – Tracks MD5 hashes of the latest committed versions.
- **Base64 Encoding** – Used for storing file snapshots.
- **MD5 Hashing** – Used to ensure file content integrity and detect changes.

---

##  Example Session

```bash
> init
.jit initialized successfully.

> add report.txt
File 'report.txt' added to staging.

> commit -m "Initial draft"
Commit created with hash: 1a2b3c4d

> status
No changes detected. Working directory is clean.

> log
Commit Hash: 1a2b3c4d
Message: Initial draft
Date: 2025-06-16 10:22:33

> rmcommit
Commit removed successfully. Reverted to previous state.

> checkout 1a2b3c4d
Checkout successful. Reverted to commit: 1a2b3c4d
