import os
import hashlib
import shutil
import json
import sys
from datetime import datetime
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

    
        
   
