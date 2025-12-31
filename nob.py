#!/usr/bin/env python3
# MADE BY SnowsSky.
import argparse
import json
import urllib.request
import subprocess
import os 
import sys
from db import Database
import libalpm
import random
from colors import Colors 
from TUI import TUI
colors = Colors()
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-S", type=str, required=False, help=f"Install a package from AUR" ,dest="install")
    parser.add_argument("-Ss", type=str, required=False, help=f"Search a package from AUR" ,dest="search")
    parser.add_argument("-Sb", type=str, required=False, help=f"Build a package (but not installing it.)" ,dest="build")
    parser.add_argument("-Sa", action='store_true', required=False, help="Upgrades AUR packages", dest="aur_upgrade")
    parser.add_argument("-Sr", action='store_true', required=False, help="Install a random package from AUR", dest="install_random") # [WARNING] : I am no responsible for any damage caused by this feature, this will download a random package from the AUR.
    parser.add_argument("-Qa", action='store_true', required=False, help="Show all packages installed with nob", dest="show_installed_aur_pkgs")
    parser.add_argument("--auto-detect", action='store_true', required=False, help="Auto detection for installed AUR packages with another AUR helper", dest="auto_detect")
    parser.add_argument("--noconfirm", action='store_true', required=False, help="No confirmations", dest="noconfirm")
    parser.add_argument("-arch-update-settings", action='store_true', required=False, help="TUI for arch-update settings", dest="arch_update_settings")
    parser.add_argument("-v", action='store_true', required=False, help="See the current version of nob", dest="nob_version")
    parser.add_argument('-R', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rns', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rsn', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rs', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rn', type=str, required=False, help=f'Remove a package.',dest="remove")

    return parser.parse_args()

_version = "1.3.0-dev1"

args = parse_args()
Install_URL = f"https://aur.archlinux.org/rpc.php?v=5&type=info&arg={args.install}"
pckg_archive = f"{args.install}.git"
folder = f"/home/{os.getlogin()}"
os.chdir(folder)
#Check is running as root
if os.geteuid() == 0: print(f"{colors.YELLOW}==> WARNING{colors.END} : Please avoid running nob as root / sudo. Some commands may not work as expected.")

def detect_pkgs():
    print(f"{colors.CYAN}==>{colors.END} Detecting installed AUR packages with other AUR helpers...")
    pkgs = libalpm.alpm.getpkgslist()
    aur_packages = get_aur_packages_list()
    for pkg_name, pkg_ver in pkgs.items():
        if pkg_name in aur_packages:
            print(f"{colors.GREEN}==>{colors.END} Detected AUR package : {pkg_name}/{pkg_ver}.")
            Database.add_db(pkg_name, pkg_ver)
    print(f"{colors.GREEN}==>{colors.END} Detection completed.")

def build_only():
    result = download_find_pkg(args.build)
    if result == None: return
    _, pkg_popularity = result
    if pkg_popularity <= 2:
        print(f"{colors.YELLOW}==> WARNING{colors.END} : This package popularity is LOW ({pkg_popularity}), this may be an indesirable program.)")
    if not args.noconfirm : 
        ask = input(f"{colors.BOLD}==>{colors.END} Do you want to continue ? Y/n : ")
        if ask.lower() == "n":
            print(f"{colors.RED}==> CANCELED{colors.END} : Build Canceled.")
            return
    download_pckg(args.build)
    os.chdir(f"./{args.build.lower()}")
    r = subprocess.run(['makepkg', '-s'], text=True, stdout=True)
    if not r.returncode == 0:
        print(f"{colors.RED}==> ERROR{colors.END} : Error while running makepkg. \n{r.stdout}")
        if not args.noconfirm : 
            ask = input(f"{colors.BOLD}==>{colors.END} Do you want to clean build ? Y/n : ")
            if ask.lower() == "n":
                return
        clean(args.build)
        return
    
    print(f"{colors.GREEN}==>{colors.END} Package {args.build} successfully built.")

def main():
    if args.build:
        build_only()
        return
    if args.auto_detect:
        detect_pkgs()
    if args.arch_update_settings:
        arch_update_timer()
        return
    if args.install_random:
        choose_random_pkg()
        return
    if args.show_installed_aur_pkgs:
        installed_aur_pkgs()
        return 
    if args.nob_version:
        print(f"{colors.BOLD}Nob {_version}{colors.END}")
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
        #Check if 'arch-update' dependency is installed, if not, updating with alpm.
        try:
            r = subprocess.run(['arch-update'], text=True, stdout=True)
        except KeyboardInterrupt:
            print(f"\n{colors.RED}==> CANCELED{colors.END} : Update Canceled.")
            return
        except FileNotFoundError:
            print(f"{colors.YELLOW}==> WARNING{colors.END} : Arch-update not found. Using nob instead.")
            if args.noconfirm : libalpm.alpm.update(True) 
            else : libalpm.alpm.update()
            return
        return
    
    if args.install:
        #Find Package
        result = download_find_pkg(args.install)
        if result == None: return
        pkg_version, pkg_popularity = result
        if pkg_popularity <= 2:
            print(f"{colors.YELLOW}==> WARNING{colors.END} : This package popularity is LOW ({pkg_popularity}), this may be an indesirable program.)")
            if not args.noconfirm : 
                ask = input(f"{colors.BOLD}==>{colors.END} Do you want to continue installation ? Y/n : ")
                if ask.lower() == "n":
                    print(f"{colors.RED}==> CANCELED{colors.END} : Installation Canceled.")
                    return
        pkgs = libalpm.alpm.getpkgslist()
        # Add the package into db with installed version, not latest version.
        if args.install in pkgs:
            installed_pckg_ver = pkgs[args.install]
            Database.add_db(args.install, installed_pckg_ver)
            print(f"{colors.YELLOW}==> WARNING{colors.END} : {args.install} is already installed. If you continue the installation, this package will be reinstalled.")
        
            
        download_pckg(args.install); install_pckg(pkg_version, args.install)

def download_find_pkg(pkg):
    d_Find_URL = f"https://aur.archlinux.org/rpc.php?v=5&type=info&arg={pkg}"
    try : 
        with urllib.request.urlopen(f"{d_Find_URL}") as response:
            data = response.read().decode("utf-8")
            rep = json.loads(data)
        if not rep['results'][0]['URLPath']:
            print(f"{colors.RED}==> ERROR{colors.END} : Cannot find package {pkg} on AUR.")
            return None
    except Exception:
        print(f"{colors.RED}==> ERROR{colors.END} : Cannot find package {pkg} on AUR.")
        return None
    #get basic info
    pkg_version = rep['results'][0]['Version']; pkg_maintainer = rep['results'][0]['Maintainer']; pkg_popularity = rep['results'][0]['Popularity']
    print(f"{colors.GREEN}==>{colors.END} Package found for query : {pkg}/{pkg_version} by {pkg_maintainer} .\n")
    return pkg_version, pkg_popularity

def download_pckg(pkg):
    if not os.path.exists(f"./{pkg.lower()}"):
        download_path = str(f"https://aur.archlinux.org/{pkg}.git")
        print(f"{colors.CYAN}==>{colors.END} Cloning {pkg}'s repository...")
        if not 'git' in libalpm.alpm.getpkgslist():
            print(f"{colors.RED}==> ERROR{colors.END} : Missing package 'git'.")
            sys.exit()
        #r = subprocess.run(['pacman', '-Q' , 'git'], text=True, capture_output=True)
        #if not r.returncode == 0:
        r = subprocess.run(['git', 'clone' , download_path], text=True, stdout=subprocess.PIPE)
        if not r.returncode == 0:
            print(f"{colors.RED}==> ERROR{colors.END} : Error while cloning {pkg}'s repository.\n{r.stdout}")
            return
    else : 
        print(f"{colors.YELLOW}==> WARNING{colors.END} : Directory ./{pkg} already exists.")
        
def install_pckg(pkg_version, pkg):
    print(f"{colors.CYAN}==>{colors.END} Going to ./{pkg} directory...")
    try:
        os.chdir(f"./{pkg.lower()}")
    except Exception as e:
        print(f"{colors.RED}==> ERROR{colors.END} : cannot find ./{pkg}.")
        return
    if not args.noconfirm :
        ask = input(f"{colors.BOLD}==>{colors.END} Do you want to read PKGBUILD ? Y/n : ")
        
        if ask.lower() == 'y' or ask == '': 
            os.system("cat ./PKGBUILD")
            try: 
                input(f"{colors.BOLD}==>{colors.END} Press any key to continue installation.\nCTRL+C to cancel installation.\n")
            except KeyboardInterrupt:
                return clean(pkg)

    print(f"{colors.CYAN}==>{colors.END} Executing makepkg")
    if not args.noconfirm:
        r = subprocess.run(['makepkg', '-si'], text=True, stdout=True)
    else :
        r = subprocess.run(['makepkg', '-si', '--noconfirm'], text=True, stdout=True)
    if not r.returncode == 0:
        print(f"{colors.RED}==> ERROR{colors.END} : Error while running makepkg. \n{r.stdout}")
        clean(pkg)
        return
    clean(pkg)
    #Add the pkg to db (if already exit, editing it with new version)
    Database.add_db(pkg, pkg_version)

def clean(pkg):
    print(f"{colors.CYAN}==>{colors.END} Cleaning installation...")
    os.chdir("../")
    try:
        os.system(f"sudo rm -rf ./{pkg.lower()}")
    except Exception as e:
        print(f"{colors.RED}==> ERROR{colors.END} : Error while cleaning :{e}.")
        return

def get_aur_packages_list():
    packages = []
    #Downloading && extacting packages list from AUR
    if not os.path.exists("/tmp/packages"):
        print(f"{colors.CYAN}==>{colors.END} Fetching AUR packages list...")
        r = subprocess.run("curl --retry 3 -s -o /tmp/packages.gz https://aur.archlinux.org/packages.gz", shell=True, text=True, stdout=subprocess.PIPE)
        r = subprocess.run(["gunzip", "-f", "/tmp/packages.gz"],text=True, stdout=subprocess.PIPE)
        if not r.returncode == 0:
            print(f"{colors.RED}==> ERROR{colors.END} : Error while fetching AUR packages list. Please try again.")
            return
    r = subprocess.run(["cat", "/tmp/packages"],text=True, stdout=subprocess.PIPE)
    for _, line in enumerate(r.stdout.splitlines()): packages.append(line.split()[0])
    return packages
    
def choose_random_pkg():
    packages = get_aur_packages_list()
    pkg = random.choice(packages)
    print(f"{colors.CYAN}==>{colors.END} Randomly selected package : {pkg} [{len(packages)} packages available on AUR]")
    ask = input(f"{colors.RED}==> WARNING{colors.END} This feature will download & install a {colors.RED}RANDOM{colors.END} package from the AUR.\n{colors.YELLOW}This feature may break your system / install undesirable software.\nThe author of NOB is not responsible for any damage caused by this feature.{colors.END}\n{colors.BOLD}==>{colors.END} Are you sure you want to proceed ? y/N : ")
    if ask.lower() != "y":
        print(f"{colors.RED}==> CANCELED{colors.END} : Installation Canceled.")
        return
    pkg_version = download_find_pkg(pkg)
    download_pckg(pkg); install_pckg(pkg_version, pkg)
    
def remove_pckg():
    #Checking flags -> if '-R', '-Rs'....
    flag = ""
    if '-R' in sys.argv: flag = '-R'
    if '-Rns' in sys.argv: flag = '-Rns'
    if '-Rsn' in sys.argv: flag = '-Rsn'
    if '-Rs' in sys.argv: flag = '-Rs'
    if '-Rn' in sys.argv:flag = '-Rn'
    #Removing package.
    if not args.remove in libalpm.alpm.getpkgslist():
        print(f"{colors.RED}==> ERROR{colors.END} : Cannot delete {args.remove} because it isn't installed yet. ")
        Database.remove_db(args.remove)
        return
    print(f"{colors.CYAN}==>{colors.END} Removing {args.remove}...")
    if not args.noconfirm:
        r = subprocess.run(['sudo', 'pacman', flag, args.remove], text=True, stdout=True)
    else:
        r = subprocess.run(['sudo', 'pacman', '--noconfirm', flag, args.remove], text=True, stdout=True)
    if not r.returncode == 0:
        print(f"{colors.RED}==> ERROR{colors.END} : An error has occured while deleting the package {args.remove}.")
        return
    print(f"{colors.GREEN}==>{colors.END} Package {args.remove} successfully deleted from the system.")
    Database.remove_db(args.remove)
           
def installed_aur_pkgs():
    print(f"{colors.CYAN}==>{colors.END} Reading nob's DB...")
    packages = Database.read_db()
    nb_packages = len(packages)
    print(f"{colors.GREEN}==>{colors.END} {nb_packages} Package(s) were found installed with nob :")
    for pkg_name, pkg_ver in packages:
        print(f"    {colors.GREEN}==>{colors.END} {pkg_name}@{pkg_ver}")

def find_pkg(pkg):
    d_Find_URL = f"https://aur.archlinux.org/rpc/v5/search/{pkg}"
    try : 
        with urllib.request.urlopen(f"{d_Find_URL}") as response:
            data = response.read().decode("utf-8")
            rep = json.loads(data)
        if not rep['results'][0]['URLPath']:
            print(f"{colors.RED}==> ERROR{colors.END} : Cannot find result(s) for {pkg} on AUR.")
            return 0
    except Exception as e:
        print(f"{colors.RED}==> ERROR{colors.END} : Cannot find package result(s) for {pkg} on AUR.")
        return 0
    results = int(rep['resultcount'])
    max_results = 100
    
    if results <= max_results:
        print(f"{colors.GREEN}==>{colors.END} {colors.BOLD}{results}{colors.END} results found for {pkg}.")
    else:
        print(f"{colors.RED}==>{colors.END} More than {colors.BOLD}{max_results}{colors.END} results found for {pkg}. Skipping {colors.BOLD}{results - max_results}{colors.END} Results.")
        if not args.noconfirm:
            ask = input(f"{colors.BOLD}==>{colors.END} Do you want to see them anyways ? y/N : ")
            if ask.lower() == "y":
                max_results = results
    for i in range(0, results):
        if i > max_results:
            return 1
        #get basic info
        pkg_name = rep['results'][i]['Name']; pkg_version = rep['results'][i]['Version']; pkg_maintainer = rep['results'][i]['Maintainer']; pkg_popularity = rep['results'][i]['Popularity']
        
        print(f"{colors.GREEN}==>{colors.END} Package found : {pkg_name}/{pkg_version} by {pkg_maintainer} (Pop : {pkg_popularity})")
    return 1

def AUR_upgr():
    packages = Database.read_db()
    packages_to_update = []
    # reading db file + Adding Packages in packages var 
    
    print(f"{colors.CYAN}==>{colors.END} Checking for AUR packages updates...")
    #Check for updates && check if package is on th AUR.
    for pkg_name, pkg_ver in packages:
        try:
            with urllib.request.urlopen(f"https://aur.archlinux.org/rpc.php?v=5&type=info&arg={pkg_name}") as response:
                data = response.read().decode("utf-8")
                rep = json.loads(data)
        except Exception:
            print(f"{colors.RED}==> ERROR{colors.END} : Error while attempting to find {pkg_name}.")
            continue
        try : 
            pkg_version = rep['results'][0]['Version']
            result_name = rep['results'][0]['Name']
        except Exception:
            print(f"{colors.RED}==> ERROR{colors.END} : DATABASE corrupted. Manual repair needed (PACKAGE {pkg_name} found in database but not in AUR).")
            return
        if pkg_version != pkg_ver:
            print(f"{colors.CYAN}==>{colors.END} Available update found : {pkg_name}/{colors.RED}{pkg_ver}{colors.END} ==> {pkg_name}/{colors.GREEN}{pkg_version}{colors.END}.")
            packages_to_update.append({
                "result_name": result_name,
                "pkg_version": pkg_version
            })
    
    if len(packages_to_update) > 0:
        if not args.noconfirm:
            ask = input(f"{colors.BOLD}==>{colors.END} Do you want update ? Y/n : ")
            if ask.lower() == "n":
                print(f"{colors.RED}==> CANCELED{colors.END} : Update Canceled.")
                return
        for pkg in packages_to_update:
            print(pkg["result_name"], pkg["pkg_version"])
            args.noconfirm = True
            download_pckg(pkg["result_name"]); install_pckg(pkg["pkg_version"], pkg["result_name"])
    
    else: print(f"{colors.CYAN}==>{colors.END} No available updates found."); return

def arch_update_timer() :
    print("Do not run this at root / sudo.")
    if not 'arch-update' in libalpm.alpm.getpkgslist():
        print(f"{colors.RED}==> ERROR{colors.END} : 'arch-update package not found. Run 'nob -S arch-update' to fix it.")
        return
    tui = TUI()
    time, status = tui.timer, tui.disabled
    if status:
        r = subprocess.run(['systemctl', '--user', 'disable', '--now', 'arch-update.timer'], text=True)
        if not r.returncode == 0:
            print(f"{colors.RED}==> ERROR{colors.END} : Error while enabling arch-update.timer.")
            return
        return
    print(f"{colors.CYAN}==>{colors.END} Editing arch-update's timer to {time} minutes... && enabling it...")
    r = subprocess.run(['systemctl', '--user', 'enable', '--now', 'arch-update.timer'], text=True)
    if not r.returncode == 0:
        print(f"{colors.RED}==> ERROR{colors.END} : Error while enabling arch-update.timer.")
        return
    user = os.getlogin()
    os.system(f"sudo chown {user}:{user} /home/{user}/.config/systemd/user/timers.target.wants/arch-update.timer")
    with open(f"/home/{user}/.config/systemd/user/timers.target.wants/arch-update.timer", "r") as f:
        lines = f.readlines()

    with open(f"/home/{user}/.config/systemd/user/timers.target.wants/arch-update.timer", "w") as f:
        for line in lines:
            if "OnUnitActiveSec" in line:
                f.write(f"OnUnitActiveSec={time}m\n")
            else:
                f.write(line)
    os.system("arch-update --tray --enable")
    print(f"{colors.GREEN}==>{colors.END} arch-update.timer successfully edited to {time} minutes.")
    f.close()
    
main()
