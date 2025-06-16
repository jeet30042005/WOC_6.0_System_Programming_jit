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
    
   
