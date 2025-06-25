import os
import hashlib
import shutil
import json
import sys
from datetime import datetime, timezone
import platform
import numpy as np
import base64

universal_dir_path = None
universal_jit_path = ""

def print_usage_help():
    print("jit - A Version Control System.")
    print("jit init - Initialize a new jit repository")
    print("jit add <file> - Add a file to the index")
    print("jit commit -m <message> - Commit changes with a message")
    print("jit rmadd <file> - Remove a file from the index")
    print("jit rmcommit - Remove last commit")
    print("jit log - Display commit log")
    print("jit checkout <commit> - Checkout a specific commit")
    print("jit help - To see this usage help")
    print("jit status - To see status")
    print("jit user show - To see present user")
    print("jit user set <username> - To change user")
    print("jit push <path> - To push your file to another folder")
    print("jit clear - To clear the terminal")
    print("jit location - To get current location")
    print("Created by - Jeet")

#init logic
class init:
    def __init__(self, dir_path):
        self.curr_dir_path = dir_path
        self.user = ""

        if not os.path.exists(os.path.join(self.curr_dir_path, ".jit")):
            self.user = input("Provide a username: ")
            user_name_arr = self.user.split()
            
            if(len(user_name_arr)>1):
                print("exiting!! kindly enter username without any break")
                return
            
            self.jit_makedirs(self.curr_dir_path, self.user)
            print(".jit created successfully")
            
        else:
            print("This folder has already been intialised once")

    def jit_makedirs(self, base_path, user_name):
        jit_path = os.path.join(base_path, ".jit")
        os.makedirs(jit_path)

        # if the OS is windows then the .jit folder will be hidden

        # if platform.system() == 'Windows':
        #     attrib_cmd = f'attrib +h "{jit_path}"'
        #     os.system(attrib_cmd)
            
        branches_path = os.path.join(jit_path, "branches")
        objects_path = os.path.join(jit_path, "objects")
        os.makedirs(branches_path)
        os.makedirs(objects_path)

        main_branch_path = os.path.join(branches_path, "main")
        os.makedirs(main_branch_path)
        user_txt_path = os.path.join(main_branch_path, "users")
        current_date_time = datetime.now()

        with open(user_txt_path, "w") as file:
            file.write(f"Date: {current_date_time.strftime('%d-%m-%Y')}\n")
            file.write(f"Timestamp: {current_date_time.strftime('%H:%M:%S')}\n")
            file.write(f"User:{user_name}\n")
            file.write("universal_jit_path: " + universal_dir_path)
            file.write("\n\n")
    

#status logic
def print_status(dir_path):
    
    untracked_files = get_untracked_files(dir_path)

    if untracked_files:
        print("Untracked files:")
        for file in untracked_files:
            file_name, folder_name = os.path.splitext(file)[0], os.path.dirname(file)
            print(f"- {file_name} from {folder_name}")
    else:
        print("No untracked files.")

def get_untracked_files(dir_path):
    tracked_hashes = get_tracked_hashes(dir_path) #this returns a set/list of MD5 hashes for files that are already added/committed.
    all_files = []
    get_all_files(dir_path, all_files) # collect all file paths into the all_files list

    untracked_files = []

    for file_path in all_files:
        file_hash = compute_md5(file_path) #compute_md5(file_path) gives the current hash of that file.
        base_name = os.path.basename(file_path) # just the file name
        if file_hash not in tracked_hashes:
            # Include folder name to avoid confusion with same-named files in different folders
            folder_name = os.path.dirname(file_path)
            untracked_files.append(os.path.join(os.path.basename(folder_name), base_name))

    return untracked_files 

def get_tracked_hashes(dir_path):
    json_path = os.path.join(dir_path, ".jit/branches/main/added.json") #This file is expected to store metadata of added/tracked files, including their MD5 hashes.
    try:
        with open(json_path, "r") as added_file:
            added_data = json.load(added_file)
            tracked_hashes = [file_info["md5 hash"] for file_info in added_data.values()]
            return tracked_hashes
    except FileNotFoundError:
        return []

def get_all_files(dir_path, all_files):
    temp_all_files = os.listdir(dir_path) #list contents of cur directory

    for item in temp_all_files:
        item_path = os.path.join(dir_path, item) #builds the full path for each file

        if os.path.isfile(item_path):
            all_files.append(item_path)
        elif os.path.isdir(item_path) and item!=".jit":
            get_all_files(item_path, all_files)

def compute_md5(file_path):
    initial_chunk_size = 4096
    max_chunk_size = 65536
    hash_md5 = hashlib.md5()
    chunk_size = initial_chunk_size

    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hash_md5.update(chunk)
                if chunk_size < max_chunk_size:
                    chunk_size *= 2
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except PermissionError:
        print(f"Permission error. Check file permissions: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return hash_md5.hexdigest()

#add logic
def add(to_file_name, file_path):
        
    dir_path = universal_dir_path
    files_directories = os.listdir(dir_path)    
    file_name = to_file_name
    jit_path = os.path.join(dir_path,".jit")
    
    if ".jit" not in files_directories:
        jit_path = universal_jit_path
    
    index_path = os.path.join(jit_path, "branches", "main", "index.json")
    added_path = os.path.join(jit_path, "branches", "main", "added.json")
    md5_hash = compute_md5(file_path)
    append_to_json(index_path, file_name, {"md5 hash": md5_hash})
    append_to_json(added_path, file_name, {"md5 hash": md5_hash, "file_path": file_path})
    print(f"File '{file_name}' successfully added to the repository.")

def append_to_json(json_path, key, value):
    try:
        os.makedirs(os.path.dirname(json_path), exist_ok=True) #create the directory if it doesn't already exists.

        if os.path.exists(json_path):
            with open(json_path, "r") as json_file:
                existing_data = json.load(json_file) #It reads the existing data into a Python dictionary, this ensure we don't erase existing data
        else:
            existing_data = {} #it starts with an empty dictionary
    except FileNotFoundError:
        existing_data = {}
    existing_data[key] = value

    #Write the updated dictionary back to the JSON file
    with open(json_path, "w") as json_file:
        json.dump(existing_data, json_file, indent=2)

def extract_universal_jit_path(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines() #reads the file content into list
            for line in lines:
                if "universal_jit_path:" in line:
                    path = line.split("universal_jit_path:")[1].strip() #triming whitespace using .strip()
                    return path

            print(f"Error: 'universal_jit_path:' not found in '{file_path}'.")
            return None
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

def addallfiles(dir_path, flag):
    files_directories = os.listdir(dir_path) #list all files and folders in the current dir
    if '.jit' not in files_directories and flag==False:
        print("Exiting program, This folder has not been intialized/ .jit doesnt exist, Use init command to intialize ")
        return
    
    for item in files_directories:
        
        full_path = os.path.join(dir_path,item)
        #if it's a folder
        if os.path.isdir(full_path) and item != '.jit':
            addallfiles(full_path,True)
        #if it's a file
        elif item!='.jit':
            add(item,full_path) 

#rmadd logic
def rmadd(base_directory, filename=None):
    jit_path = os.path.join(base_directory, ".jit") 
    added_path = os.path.join(jit_path, "branches", "main", "added.json")

    if not os.path.exists(added_path):
        print("Files have not been tracked yet or added.json doesn't exist. Use add command to track files.")
        return

    if filename is None:
        remove_from_json(added_path)
        print("All files successfully removed from tracking.")
    else:
        remove_specific_file_from_json(added_path, filename)

def remove_specific_file_from_json(json_path, filename):
    try:
        with open(json_path, "r") as json_file:
            data = json.load(json_file) #load it's content into data

        if filename in data:
            del data[filename] #if filename present, delete that from data
            with open(json_path, "w") as json_file:
                json.dump(data, json_file, indent=4) #dump the updated data
            print(f"File '{filename}' successfully removed from tracking.")
        else:
            print(f"File '{filename}' is not currently added/tracked.")

    except FileNotFoundError:
        print(f"Error: File '{json_path}' not found.")
    except json.JSONDecodeError:
        print("Error reading JSON file. Possibly corrupted.")

def remove_from_json(json_path):
    try:
        with open(json_path, "w") as json_file:
            json_file.write("{}") #open json file and overwrites it with {} empty list
    except FileNotFoundError:
        print(f"Error: File '{json_path}' not found.")
        return

#show username logic
def extract_username_from_file(dir_path):
    
    file_path = os.path.join(dir_path,".jit","branches","main","users")
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if "User:" in line:
                    username = line.split("User:")[1].strip()
                    return username
            return None
    except FileNotFoundError:
        return None
    
#change username logic
def change_user_name(dir_path, new_username):
    
    file_path = os.path.join(dir_path,".jit","branches","main","users")
    old_user = extract_username_from_file(dir_path)
    
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if "User:" in line:
                line = line.replace(line.split("User:")[1].strip(), new_username)
            file.write(line)

    print(f"Username changed to '{new_username}' in users.txt.")

#commit logic  

def encode_file_content_to_base64(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
        return base64.b64encode(binary_data).decode('utf-8')  

def commits(base_directory, message):
    
    jit_path = os.path.join(base_directory, ".jit")
    added_path = os.path.join(jit_path, "branches", "main", 'added.json')
    commits_path = os.path.join(jit_path, 'objects', 'commits.json') #this file contains previous commits 
    md5_hash_path = os.path.join(jit_path, 'objects', 'files_md5_hash.json') #this file contains md5 hash of previous commits
    
    if not os.path.exists(added_path):
        print("Files have not been tracked yet. Use the add command to track files. After that, you can use the commit command.")
        return

    # Create an empty MD5 hash dictionary if the file doesn't exist
    md5_hash_data = {} # hash of last committed files
    if os.path.exists(md5_hash_path):
        with open(md5_hash_path, 'r') as md5_hash_file:
            md5_hash_data = json.load(md5_hash_file)
    
    commits = []
    
    if os.path.exists(commits_path):
        with open(commits_path, 'r') as commits_file:
            commits = json.load(commits_file)
        
    with open(added_path, 'r') as added_file:
        added_data = json.load(added_file)
 
    username = extract_username_from_file(universal_dir_path)
    
    commit = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user-name": username, 
        "message": message,
        "date": datetime.now(timezone.utc).strftime("%d-%m-%Y"),
        "commit_hash": None,  # Placeholder for the commit-specific hash
        "files": []
    }

    # Calculate a unique MD5 hash for this commit based on timestamp and files
    commit_hash_input = f"{commit['timestamp']}:{json.dumps(commit['files'], sort_keys=True)}"
    commit_hash = hashlib.md5(commit_hash_input.encode()).hexdigest()
    commit["commit_hash"] = commit_hash
    untracked_files = []
    isdeleted = False
    
    # Iterate over a list of keys to avoid dictionary size change during iteration
    for filename in list(added_data.keys()):
        file_info = added_data[filename]
        file_path = file_info.get("file_path")
        if os.path.exists(file_path):
            actual_md5 = compute_md5(file_path)
            encoded_content = encode_file_content_to_base64(file_path)
            #File Already Committed, No Change
            if actual_md5 == md5_hash_data.get(file_path):
                # print(f"No changes made to file '{filename}'. Skipping.")
                untracked_files.append({"filename": filename, "file_path": file_path, "encoded_content": encoded_content})
                continue
            #File Hash Matches the Hash When Added
            if actual_md5 == file_info.get("md5 hash"):
                commit["files"].append({"filename": filename, "file_path": file_path, "encoded_content": encoded_content})
                md5_hash_data[file_path] = actual_md5  # Update the MD5 hash in the dictionary
            else:
                print(f"Warning: File '{filename}' has changed. Kindly use the Add command first.")
                return
        else:
            print(f"Warning: File '{filename}' not found. Removed from added.json.")
            isdeleted = True
            del added_data[filename]  # Remove the not found file from added_data

    # Update added.json with the remaining files
    with open(added_path, 'w') as added_file:
        json.dump(added_data, added_file, indent=2)
        added_file.write('\n')        

    # Check if commit has files before appending it to commits
    if isdeleted:
        for item in untracked_files:
            commit["files"].append(item)
    # Check Whether We Have Anything to Commit
    if commit["files"]:
        commits.append(commit)
    
        with open(commits_path, 'w') as commits_file:
            json.dump(commits, commits_file, indent=2)
            commits_file.write('\n')

        print("Commit Successful")
    else:
        print("No changes made. Commit skipped.")

    with open(md5_hash_path, 'w') as md5_hash_file:
        json.dump(md5_hash_data, md5_hash_file, indent=2)
        md5_hash_file.write('\n')
        
def remove_commit(commits_path):
    if not os.path.exists(commits_path):
        print("Error: 'commits.json' not found.")
        return None
    
    with open(commits_path, 'r') as commits_file:
        commits = json.load(commits_file)
        
    if not commits:
        print("Error: No commits to remove.")
        return None

    removed_commit = commits.pop()
    
    if not commits:
        print("Error: No commit left after removal.")
        return None
    
    commit_before_removed = commits[-1]

    with open(commits_path, 'w') as commits_file:
        json.dump(commits, commits_file, indent=2)

    print("Commit removed successfully:")

    return commit_before_removed
    
def rmcommit(dir_path):
    commits_path = os.path.join(dir_path,".jit","objects","commits.json")
    
    if(os.path.exists(commits_path)==False):
        print("The path of commits.json has been changed. Kindly check if the file exists and it is placed in correct folder")
        return
    
    to_be_restore = remove_commit(commits_path)
    
    if(to_be_restore):
        decode_and_update_files(to_be_restore,dir_path, True)  

def decode_and_update_files(commit, destination_folder, flag2):
    
    base_path = universal_dir_path
    files = commit.get("files", [])
    for file_data in files:
        filename = file_data.get("filename")
        encoded_content = file_data.get("encoded_content")
        file_path = file_data.get("file_path")

        try:
            decoded_content = base64.b64decode(encoded_content)
            relative_path = os.path.relpath(file_path, base_path)
            destination_path = os.path.join(destination_folder, filename)
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            with open(destination_path, 'wb') as file:
                file.write(decoded_content)

            if flag2:
                md5_hash_path = os.path.join(universal_dir_path,".jit",'objects', 'files_md5_hash.json')
                md5_hash_data = {}
                
                actual_md5 = compute_md5(destination_path)
                md5_hash_data[relative_path] = actual_md5

                with open(md5_hash_path, 'w') as md5_hash_file:
                    json.dump(md5_hash_data, md5_hash_file, indent=2)
                    md5_hash_file.write('\n')
                    
            print(f"File '{filename}' updated/copied.")
                    
        except (PermissionError, FileNotFoundError) as e:
            print(f"Error updating/copying file '{filename}': {str(e)}")
            return None
        
        except Exception as e:
            print(f"Unexpected error updating/copying file '{filename}': {str(e)}")
            return None
        
    return True

def checkout_commit(md5_hash, dir_path):
    commits_path = os.path.join(dir_path, ".jit", "objects", "commits.json")
    md5_hash_path = os.path.join(dir_path, ".jit", "objects", "files_md5_hash.json")

    try:
        with open(commits_path, 'r') as commits_file:
            commits_data = json.load(commits_file)

        # Find the index of the commit with the specified MD5 hash
        commit_index = None
        for i, commit in enumerate(commits_data):
            if commit['commit_hash'] == md5_hash:
                commit_index = i
                break

        if commit_index is not None:
            # Remove subsequent commits from the end
            while len(commits_data) > commit_index + 1:
                commits_data.pop()
                
            commit_to_checkout = commits_data[-1];
            decode_and_update_files(commit_to_checkout, dir_path, True)
            # Update MD5 hash file with the MD5 values from the specified commit
            with open(md5_hash_path, 'w') as md5_hash_file:
                md5_hash_data = {file_info['file_path']: compute_md5(file_info['file_path'])
                                 for file_info in commits_data[-1]['files']}
                json.dump(md5_hash_data, md5_hash_file, indent=2)
                md5_hash_file.write('\n')

            # Update commits.json with the remaining commit
            with open(commits_path, 'w') as commits_file:
                json.dump(commits_data, commits_file, indent=2)
                commits_file.write('\n')

            print(f"Checkout successful. Reverted to commit with hash: {md5_hash}")
        else:
            print(f"Error: Commit with hash {md5_hash} not found.")

    except FileNotFoundError:
        print(f"Error: File '{commits_path}' not found.")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
         
#logs logic
def display_logs(commits_path):
    print()
    try:
        with open(commits_path, 'r') as commits_file:
            commits_data = json.load(commits_file)

        if commits_data:
            print("Commits:")
            print()
            for commit in commits_data:
                print(f"Commit Hash: {commit['commit_hash']}")
                print(f"Timestamp: {commit['timestamp']}")
                print(f"User: {commit['user-name']}")
                print(f"Message: {commit['message']}")
                print(f"Date: {commit['date']}")
                print("Files:")
                for file_info in commit['files']:
                    print(f"  - Filename: {file_info['filename']}")
                    print(f"    File Path: {file_info['file_path']}")
                print("------------------------------")
        else:
            print("No commits found.")

    except FileNotFoundError:
        print(f"Error: File '{commits_path}' not found.")

#push logic
def push(base_directory, destination_path):
    jit_path = os.path.join(base_directory, ".jit")
    commits_path = os.path.join(jit_path, 'objects', 'commits.json')
    
    if os.path.exists(destination_path)==False or destination_path[0]=='.':
        print("Destination path/directory doesnt exist kindly check")
        return

    if not os.path.exists(commits_path):
        print("No commits found. Use commit command to commit changes.")
        return

    with open(commits_path, 'r') as commits_file:
        commits = json.load(commits_file)

    if not commits:
        print("No commits found. Use commit command to commit changes.")
        return

    last_commit = commits[-1]
    
    if decode_and_update_files(last_commit,destination_path,False):
        print("commits successfully copied to destination folder")

while True:
    
    if universal_dir_path==None:
        universal_dir_path = input("Enter directory location where you want to use .jit : ")
        print()
                
        if(os.path.exists(universal_dir_path)==False or universal_dir_path[0]=='.'):
            print("The path you have given doesnt exists, kindly give existing path")
            print()
            universal_dir_path = None
            continue
    
    user_input = input("Enter command: ")
    print()
    if not user_input:
        continue
    
    # whatever command you have given it will splits into a list
    args = user_input.split()
    # print(args)
    
    if args[0] == "exit":
        print("Exiting program.")
        print()
        break
    
    if args[0]=="help":
        if len(args) > 1:
            print("wrong syntax for help. Kindly recompile")
            print()
            continue
    
        print_usage_help()
        print()
        
    elif args[0]=="location":
        if len(args) > 1:
            print("wrong syntax for location. Kindly recompile")
            print()
            continue
        
        print(f"location : {universal_dir_path}")
        print()
        
    elif args[0] == "init":
        if len(args) > 1:
            print("wrong syntax for init. Kindly recompile")
            print()
            continue
        
        init(universal_dir_path)
        print()
        
    elif args[0] == "status":
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized/ .jit doesn't exist, Use init command to initialize ")
            print()
            continue
        
        if len(args) > 1:
            print("Wrong syntax for status. Kindly recompile.")
            print()
            continue

        print_status(universal_dir_path)
        print()

    elif args[0] == "add":
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized/ .jit doesn't exist, Use init command to initialize ")
            print()
            continue
        
        if len(args) > 2:
            print("wrong syntax for add command")
            print()
            continue

        if len(args) <= 1:
            print("File Name not given")
            print()
            continue

        elif args[1] == '.':
            universal_jit_path = extract_universal_jit_path(os.path.join(universal_dir_path, ".jit", "branches", "main", "users"))
            addallfiles(universal_dir_path, False)
            print()
        
        else:
            file_path = os.path.join(universal_dir_path, args[1])
            universal_jit_path = extract_universal_jit_path(os.path.join(universal_dir_path, ".jit", "branches", "main", "users"))
            if not os.path.exists(file_path):
                print("File doesn't exist or File name not given!!")
                print()
                continue
            
            add(args[1], file_path)
            print()
        
    elif args[0] == "rmadd":
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized / .jit doesn't exist. Use init command to initialize.")
            print()
            continue

        if len(args) > 2:
            print("Wrong syntax for rmadd. Usage:")
            print(" - rmadd              → to remove all added files")
            print(" - rmadd <filename>   → to remove a specific file from tracking")
            print()
            continue

        filename = args[1] if len(args) == 2 else None
        rmadd(universal_dir_path, filename)
        print()
    
    elif args[0] == "clear":
        
        if len(args)>1:
            print("Wrong syntax for log. Use 'log'.")
            print()
            continue
        
        if os.name == 'posix': #On Linux or macOS, os.name is 'posix'
            os.system('clear')
            
        elif os.name == 'nt':  #On Windows, os.name is 'nt'
            os.system('cls')
            
        else:
            print("Clear screen command not supported on this platform.")
            print()
            continue
    
    elif args[0] == "user" and len(args)>=2 and args[1]=="show":
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized/ .jit doesn't exist, Use init command to initialize ")
            print()
            continue
        
        if not os.path.exists(os.path.join(universal_dir_path,".jit","branches","main","users")):
            print("Error. The users.txt file has been deleted or has been moved. kindly check")
            print()
            continue

        if len(args) == 2 and args[1] == "show":
            user = extract_username_from_file(universal_dir_path)
            print(f"user : {user}")
            print()
            
        else:
            print("Wrong syntax for user. Use 'user show'.")
            print()
            continue

    elif args[0] == "user" and len(args)>=3 and args[1]=="set":
        
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized/ .jit doesn't exist, Use init command to initialize ")
            print()
            continue
        
        if not os.path.exists(os.path.join(universal_dir_path,".jit","branches","main","users")):
            print("Error. The users.txt file has been deleted or has been moved. kindly check")
            print()
            continue
    
        if len(args) == 3 and args[1] == "set":
            username = args[2]
            change_user_name(universal_dir_path, username)
            print()
            
        else:
            print("Wrong syntax for user set. Use 'user set <username>'.")
            print()
            continue
    
    elif args[0] == "commit":
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized/ .jit doesn't exist, Use init command to initialize ")
            print()
            continue

        if args[1] == "-m":
            if args[2][0] == '"' and args[-1][-1] == '"':
                commit_message = " ".join(args[2:])
                commit_message = commit_message[1:-1]  
                flag1 = False
                
                for i in commit_message:
                    if i!=' ':
                        flag1 = True

                if flag1==False:
                    print("Cannot commit with empty message kindly recompile")
                    print()
                    continue
                        
                commits(universal_dir_path, commit_message)
                print()
            else:
                print("Invalid commit command. Use 'commit -m \"message\"'.")
                print()
                continue
        else:
            print("Invalid commit command. Use 'commit -m \"message\"'.")
            print()
            continue
    
    elif args[0] == "rmcommit":
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized/ .jit doesn't exist, Use init command to initialize ")
            print()
            continue

        if len(args) > 1:
            print("Wrong syntax for rmcommit. Kindly recompile.")
            print()
            continue

        rmcommit(universal_dir_path)
        print()


    elif args[0] == "log":
        
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized/ .jit doesn't exist, Use init command to initialize ")
            print()
            continue
        
        if not os.path.exists(os.path.join(universal_dir_path,".jit","objects","commits.json")):
            print("commits.json doesnt exist. Kindly use add command and then commit command to create one or restore back the old one")
            print() 
            continue

        if len(args) == 1:
            commits_path = os.path.join(universal_dir_path, ".jit", "objects","commits.json")
            display_logs(commits_path)
            print()
            
        else:
            print("Wrong syntax for log. Use 'log'.")
            print()
            continue

    elif args[0] == "push":
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized/ .jit doesn't exist, Use init command to initialize ")
            print()
            continue
        
        dest_path = " ".join(args[1:]).strip('"')
        push(universal_dir_path,dest_path)
        print()
      
    elif args[0] == "checkout":
        
        if not os.path.exists(universal_dir_path + "/.jit"):
            print("Exiting program, This folder has not been initialized/ .jit doesn't exist, Use init command to initialize ")
            print()
            continue
        
        if len(args)>2 or len(args)==1:
            print("Wrong syntax for log. Use 'checkout <hash>'.")
            print()
            continue
        
        checkout_commit(args[1],universal_dir_path)
        print()

    elif args[0] == "ls":
        if len(args) != 2:
            print("Invalid syntax for ls. Use 'ls <path>'.")
            print()
            continue

        dest_path = args[1] 

        if not os.path.exists(dest_path):
            print(f"The specified path '{dest_path}' does not exist.")
            print("Syntax for ls: Use 'ls <path>'.")
            print()
            continue

        if not os.path.isdir(dest_path):
            print(f"The specified path '{dest_path}' is not a directory.")
            print("Syntax for ls: Use 'ls <path>'.")
            print()
            continue

        all_files = []
        get_all_files(dest_path, all_files)

        if not all_files:
            print(f"No files found in '{dest_path}'.")
        else:
            print(f"Files in '{dest_path}':")
            for file_path in all_files:
                print(f"  - {file_path}")
        print()

    elif args[0] == "exit":
        break

    else:
        print("Invalid command. Please try again.")
        print()
    