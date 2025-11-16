#!/usr/bin/env python3
# MADE BY SnowsSky.
import argparse
import json
import urllib.request
import subprocess
import os
import sys
import random
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-S", type=str, required=False, help=f"Install a package from AUR" ,dest="install")
    parser.add_argument("-Ss", type=str, required=False, help=f"Search a package from AUR" ,dest="search")
    parser.add_argument("-Sa", action='store_true', required=False, help="Upgrades AUR packages", dest="aur_upgrade")
    parser.add_argument("-Qa", action='store_true', required=False, help="Show all packages installed with nob", dest="show_installed_aur_pkgs")
    parser.add_argument("-v", action='store_true', required=False, help="See the current version of nob", dest="nob_version")
    parser.add_argument('-R', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rns', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rsn', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rs', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rn', type=str, required=False, help=f'Remove a package.',dest="remove")

    return parser.parse_args()

_version = "1.2.0"
# COLORS
BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
NEGATIVE = "\033[7m"
CROSSED = "\033[9m"
END = "\033[0m"
    

args = parse_args()
Install_URL = f"https://aur.archlinux.org/rpc.php?v=5&type=info&arg={args.install}"


pckg_archive = f"{args.install}.git"

if not os.path.exists("db.txt"):
    try:
        r = subprocess.run(['touch', 'db.txt' ], text=True, capture_output=True)
        if not r.returncode == 0:
            print(f"{RED}==> ERROR{END} : Error while trying to create db file")
    except Exception as e:
        print(f"{RED}==> ERROR{END} : Error while trying to create db file : {e}")

def version():
    print(f"{BOLD}Nob {_version}{END}")

def main():
    if args.show_installed_aur_pkgs:
        installed_aur_pkgs()
        return 
    if args.nob_version:
        version()
        return
    if args.aur_upgrade:
        AUR_upgr()
        return
    if args.remove:
        remove_pckg()
        return
    if args.search:
        find_pkg(args.search)
        return
    if not args.install:
        print(f"{CYAN}==>{END} Checking For updates...")
        
        os.system("sudo pacman -Syu")
        
        return
    if args.install:
        result = download_find_pkg(args.install)
        if result == 0:
            return
        
        with urllib.request.urlopen(f"{Install_URL}") as response:
            data = response.read().decode("utf-8")
            rep = json.loads(data)
        
        pkg_version = rep['results'][0]['Version']

        r = subprocess.run(['pacman', '-Q' , args.install], text=True, capture_output=True)
        if r.returncode == 0:
            print(f"{YELLOW}==> WARNING{END} : {args.install} is already installed. If you continue the installation, this package will be reinstalled.")

        ask = input(f"{BOLD}==>{END} Do you want to continue installation ? Y/n : ")
        if ask == "n":
            print(f"{RED}==> CANCELED{END} : Installation Canceled.")
            return
            
        download_pckg(args.install, pkg_version)
            

def remove_pckg():
    flag = ""
    if '-R' in sys.argv:
        flag = '-R'
    if '-Rns' in sys.argv:
        flag = '-Rns'
    if '-Rsn' in sys.argv:
        flag = '-Rsn'
    if '-Rs' in sys.argv:
        flag = '-Rs'
    if '-Rn' in sys.argv:
        flag = '-Rn'
    print(flag, args.remove)
    print(f"{CYAN}==>{END} Executing pacman...")
    r = subprocess.run(['pacman', '-Q' , args.remove], text=True, capture_output=True)
    if not r.returncode == 0:
        print(f"{RED}==> ERROR{END} : Cannot delete {args.remove} because it isn't installed yet. ")
        return
    try:
        ask = input(f"{BOLD}==>{END} Do you want to remove {args.remove} ? Y/n : ")
        if ask == "n":
            print(f"{RED}==> CANCELED{END} : Uninstallation Canceled.")
            return
    except KeyboardInterrupt:
        print(f"\n{RED}==> CANCELED{END} : Uninstallation Canceled.")
        return
    print(f"{CYAN}==>{END} Removing {args.remove}...")
    try:
        os.system(f"sudo pacman --noconfirm {flag} {args.remove} ")
        
        #r = subprocess.run(['pacman', f'{flag}' '--noconfirm', 'args.remove'], text=True, capture_output=True)
    except Exception as e:
        print(f"{RED}==> ERROR{END} : An error has occured while delete the package {args.remove} : {e}")
        return
    print(f"{GREEN}==>{END} Package {args.remove} successfully deleted from the system.")
    with open("db.txt", "r") as f:
        lines = f.readlines()
    with open("db.txt", "w") as f:
        for line in lines:
            if args.remove not in line.strip("\n"):
                f.write(line)
    f.close()
    

def download_pckg(pkg, pkg_version):
    download_path = str(f"https://aur.archlinux.org/{pkg}.git") #?format=gzip
    print(download_path)
    print(f"{CYAN}==>{END} Cloning {pkg}'s repository...")
    
    r = subprocess.run(['pacman', '-Q' , 'git'], text=True, capture_output=True)
    if not r.returncode == 0:
        print(f"{RED}==> ERROR{END} : Missing package 'git'")
        return

    try :
        os.system(f"sudo rm -rf {pckg_archive}")
    except OSError as e:
        if not e.errno == 2:
            print(f"{RED}==> ERROR{END} : Cannot delete existing package .tar.gz : {e}")
        
    try:
        subprocess.run(['git', 'clone' ,download_path], text=True, capture_output=True)
    except Exception as e:
        print(f"{RED}==> ERROR {END} : {e}.")
        return

    install_pckg(pkg_version, pkg)


def install_pckg(pkg_version, pkg):
    print(f"{CYAN}==>{END} Checking required dependencies for makepkg...")
    r = subprocess.run(['pacman', '-Q', 'fakeroot', 'debugedit', 'base-devel'], capture_output=True, text=True)
    if not r.returncode == 0:
        print(f"{YELLOW}==> WARNING{END} : Missing dependencies, Installing them...")
        os.system("sudo pacman -S base-devel fakeroot debugedit")

    print(f"{CYAN}==>{END} Going to ./{pkg} directory...")
    try:
        os.chdir(f"./{pkg.lower()}")
    except Exception as e:
        print(f"{RED}==> ERROR{END} : cannot find ./{pkg}.")
        return
    try:
        print(f"{CYAN}==>{END} Executing makepkg")
        os.system("makepkg -si")
        #subprocess.run(['makepkg', '-si'], capture_output=True, text=True)
    except Exception as e:
        print(f"{RED}==> ERROR{END} : {e}.")
        return
    clean(pkg_version, pkg)

def clean(pkg_version, pkg):
    print(f"{CYAN}==>{END} Cleaning installation...")
    os.chdir("../")
    try:
        os.system(f"sudo rm -rf ./{pkg.lower()}")
    except Exception as e:
        print(f"{RED}==> ERROR{END} : Error while cleaning :{e}.")
        return
    print(f"{CYAN}==>{END} Adding {pkg} to nob's DB...")
    #Add the pkg to db (if already exit, editing it with new version)
    with open('db.txt', 'r+') as file:
        lines = file.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip() and line.split()[0] == pkg:
                lines[i] = f"{pkg} {pkg_version}\n"
                found = True
                break
        if not found:
            lines.append(f"{pkg} {pkg_version}\n")
            
        file.seek(0)
        file.writelines(lines)
        file.truncate()
    print(f"{GREEN}==>{END} Installation finished !")
            
    file.close()
   
def installed_aur_pkgs():
    print(f"{CYAN}==>{END} Reading nob's DB...")
    packages = []
    # reading db file + Adding Packages in packages var 
    with open('db.txt', 'r') as file:
        for lign in file.readlines():
            pckg_name, pckg_ver = lign.strip().split()
            packages.append({
            "pckg_name": pckg_name,
            "pckg_ver": pckg_ver
        })
    nb_packages = len(packages)
    print(f"{GREEN}==>{END} {nb_packages} Package(s) were found installed with nob :")
    for package in packages:
        pkg_name = package['pckg_name']
        pkg_ver =  package['pckg_ver']
        print(f"    {GREEN}==>{END} {pkg_name}/{pkg_ver}")



def find_pkg(pkg):
    d_Find_URL = f"https://aur.archlinux.org/rpc/v5/search/{pkg}"
    try : 
        with urllib.request.urlopen(f"{d_Find_URL}") as response:
            data = response.read().decode("utf-8")
            rep = json.loads(data)
        if not rep['results'][0]['URLPath']:
            print(f"{RED}==> ERROR{END} : Cannot find result(s) for {pkg} on AUR.")
            return 0
    except Exception as e:
        print(f"{RED}==> ERROR{END} : Cannot find package result(s) for {pkg} on AUR.")
        return 0
    results = int(rep['resultcount'])
    max_results = 100
    
    if results <= max_results:
        print(f"{GREEN}==>{END} {BOLD}{results}{END} results found for {pkg}.")
    else:
        print(f"{RED}==>{END} More than {BOLD}{max_results}{END} results found for {pkg}. Skipping {BOLD}{results - max_results}{END} Results.")
        ask = input(f"{BOLD}==>{END} Do you want to see them anyways ? y/N : ")
        if ask == "y":
            max_results = results
    for i in range(0, results):
        if i > max_results:
            return 1
        pkg_name = rep['results'][i]['Name']
        pkg_version = rep['results'][i]['Version']
        pkg_maintainer = rep['results'][i]['Maintainer']
        pkg_popularity = rep['results'][i]['Popularity']
        print(f"{GREEN}==>{END} Package found : {pkg_name}/{pkg_version} by {pkg_maintainer} (Pop : {pkg_popularity})")
    return 1

def download_find_pkg(pkg):
    d_Find_URL = f"https://aur.archlinux.org/rpc.php?v=5&type=info&arg={pkg}"
    try : 

        with urllib.request.urlopen(f"{d_Find_URL}") as response:
            data = response.read().decode("utf-8")
            rep = json.loads(data)
        if not rep['results'][0]['URLPath']:
            print(f"{RED}==> ERROR{END} : Cannot find package {pkg} on AUR.")
            return 0
    except Exception as e:
        print(f"{RED}==> ERROR{END} : Cannot find package {pkg} on AUR.")
        return 0
    pkg_version = rep['results'][0]['Version']
    pkg_maintainer = rep['results'][0]['Submitter']
    print(f"{GREEN}==>{END} Package found for query : {pkg}/{pkg_version} by {pkg_maintainer} .\n")
    return 1

def AUR_upgr():
    packages = []
    # reading db file + Adding Packages in packages var 
    with open('db.txt', 'r') as file:
        for lign in file.readlines():
            pckg_name, pckg_ver = lign.strip().split()
            packages.append({
            "pckg_name": pckg_name,
            "pckg_ver": pckg_ver
        })
    print(f"{CYAN}==>{END} Checking for AUR packages updates...")
    #Check for updates && check if package is on th AUR.
    for package in packages:
        pkg_name = package['pckg_name']
        with urllib.request.urlopen(f"https://aur.archlinux.org/rpc.php?v=5&type=info&arg={pkg_name}") as response:
            data = response.read().decode("utf-8")
            rep = json.loads(data)
            try : 

                pkg_version = rep['results'][0]['Version']
                result_name = rep['results'][0]['Name']
            except Exception:
                print(f"{RED}==> ERROR{END} : DATABASE corrupted. Manual repair needed (PACKAGE {pkg_name} found in database but not in AUR).")
                return
            
            if pkg_version != package['pckg_ver']:
                print(f"{CYAN}==>{END} Available update found : {pkg_name}{package['pckg_ver']} ==> {pkg_name}{pkg_version}.")
                ask = input(f"{BOLD}==> ASK{END} : Do you want to update {pkg_name} ? Y/n : ")
                if ask == 'n':
                    print(f"\n{RED}==> CANCELED{END} : Update Canceled.")
                else:
                    print(result_name, pkg_version)
                    download_pckg(result_name, pkg_version)
            
                
                    
    print(f"{CYAN}==>{END} No available updates found.")
    return

main()
