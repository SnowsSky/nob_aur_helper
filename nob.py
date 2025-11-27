#!/usr/bin/env python3
# MADE BY SnowsSky.
import argparse
import json
import urllib.request
import subprocess
import os 
import sys
import random
from colors import Colors 
colors = Colors()
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-S", type=str, required=False, help=f"Install a package from AUR" ,dest="install")
    parser.add_argument("-Ss", type=str, required=False, help=f"Search a package from AUR" ,dest="search")
    parser.add_argument("-Sa", action='store_true', required=False, help="Upgrades AUR packages", dest="aur_upgrade")
    parser.add_argument("-Sr", action='store_true', required=False, help="Install a random package from AUR", dest="install_random") # [WARNING] : I am no responsible for any damage caused by this feature, this will download a random package from the AUR.
    parser.add_argument("-Qa", action='store_true', required=False, help="Show all packages installed with nob", dest="show_installed_aur_pkgs")
    parser.add_argument("--noconfirm", action='store_true', required=False, help="No confirmations", dest="noconfirm")
    parser.add_argument("-v", action='store_true', required=False, help="See the current version of nob", dest="nob_version")
    parser.add_argument('-R', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rns', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rsn', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rs', type=str, required=False, help=f'Remove a package.',dest="remove")
    parser.add_argument('-Rn', type=str, required=False, help=f'Remove a package.',dest="remove")

    return parser.parse_args()

_version = "1.2.3"

args = parse_args()
Install_URL = f"https://aur.archlinux.org/rpc.php?v=5&type=info&arg={args.install}"
pckg_archive = f"{args.install}.git"

#Check is running as root
if os.geteuid() == 0: print(f"{colors.YELLOW}==> WARNING{colors.END} : Please avoid running nob as root / sudo. Some commands may not work as expected.")

#Create DB file if not found
if not os.path.exists("/usr/bin/nob_db.txt"):
    try:
        r = subprocess.run(['sudo', 'touch', '/usr/bin/nob_db.txt' ], text=True, capture_output=True)
        if not r.returncode == 0:
            print(f"{colors.RED}==> ERROR{colors.END} : Error while trying to create db file")
            pass
        subprocess.run(['sudo', 'chmod', '666', '/usr/bin/nob_db.txt'], text=True, capture_output=True) #Allowing user & programs to edit it without root permissions.
    except Exception as e:
        print(f"{colors.RED}==> ERROR{colors.END} : Error while trying to create db file : {e}")
def add_db(pkg, pkg_version):
    #ADD a package to the nobDB with it name & version
    with open('/usr/bin/nob_db.txt', 'r+') as file:
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
    file.close()

def main():
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
        #Check if 'arch-update' dependency is installed, if not, updating with pacman.
        def upt_pacman():
            r = subprocess.run(['sudo', 'pacman', '-Syu'], text=True, stdout=True)
            if not r.returncode == 0:
                print(f"{colors.RED}==> ERROR{colors.END} : Error while updating the system.")
                return
        print(f"{colors.CYAN}==>{colors.END} Running arch-update script...")
        try:
            subprocess.run(['arch-update'], text=True, stdout=True)
        except :
            print(f"{colors.YELLOW}==> WARNING{colors.END} : Error. Running 'pacman -Syu instead'...")
            upt_pacman()
            return
        return
    
    if args.install:
        #Find Package
        result = download_find_pkg(args.install)
        if result == None: return
        pkg_version, pkg_popularity = result
        if pkg_popularity <= 2:
            print(f"{colors.YELLOW}==> WARNING{colors.END} : This package popularity is LOW ({pkg_popularity}), this may be an indesirable program.)")

        r = subprocess.run(['pacman', '-Q' , args.install], text=True, capture_output=True)
        # Add the package into db with installed version, not latest version.
        if r.returncode == 0:
            _, installed_pckg_ver = r.stdout.strip().split()
            add_db(args.install, installed_pckg_ver)
            print(f"{colors.YELLOW}==> WARNING{colors.END} : {args.install} is already installed. If you continue the installation, this package will be reinstalled.")
        if not args.noconfirm : 
            ask = input(f"{colors.BOLD}==>{colors.END} Do you want to continue installation ? Y/n : ")
            if ask == "n":
                print(f"{colors.RED}==> CANCELED{colors.END} : Installation Canceled.")
                return
            
        download_pckg(args.install, pkg_version)
            
def get_aur_packages_list():
    packages = []
    #Downloading && extacting packages list from AUR
    if not os.path.exists("/tmp/packages"):
        print(f"{colors.CYAN}==>{colors.END} Fetching AUR packages list...")
        r = subprocess.run("curl --retry 3 -s -o /tmp/packages.gz https://aur.archlinux.org/packages.gz", shell=True, text=True, stdout=subprocess.PIPE)
        r = subprocess.run(["gunzip", "-f", "/tmp/packages.gz"],text=True, stdout=subprocess.PIPE)
        if not r.returncode == 0:
            print(f"{colors.RED}==> ERROR{colors.END} : Error while fetching AUR packages list.")
            return
    r = subprocess.run(["cat", "/tmp/packages"],text=True, stdout=subprocess.PIPE)
    for _, line in enumerate(r.stdout.splitlines()): packages.append(line.split()[0])
    return packages
    
def choose_random_pkg():
    packages = get_aur_packages_list()
    pkg = random.choice(packages)
    print(f"{colors.CYAN}==>{colors.END} Randomly selected package : {pkg} [{len(packages)} packages available on AUR]")
    ask = input(f"{colors.RED}==> WARNING{colors.END} This feature will download & install a {colors.RED}RANDOM{colors.END} package from the AUR.\n{colors.YELLOW}This feature may break your system / install undesirable software.\nThe author of NOB is not responsible for any damage caused by this feature.{colors.END}\n{colors.BOLD}==>{colors.END} Are you sure you want to proceed ? y/N : ")
    if ask != "y":
        print(f"{colors.RED}==> CANCELED{colors.END} : Installation Canceled.")
        return
    pkg_version = download_find_pkg(pkg)
    download_pckg(pkg, pkg_version)
    
def remove_pckg():
    #Checking flags -> if '-R', '-Rs'....
    flag = ""
    if '-R' in sys.argv: flag = '-R'
    if '-Rns' in sys.argv: flag = '-Rns'
    if '-Rsn' in sys.argv: flag = '-Rsn'
    if '-Rs' in sys.argv: flag = '-Rs'
    if '-Rn' in sys.argv:flag = '-Rn'
    #Removing package.
    print(f"{colors.CYAN}==>{colors.END} Executing pacman...")
    r = subprocess.run(['pacman', '-Q' , args.remove], text=True, capture_output=True)
    if not r.returncode == 0:
        print(f"{colors.RED}==> ERROR{colors.END} : Cannot delete {args.remove} because it isn't installed yet. ")
        return
    try:
        if not args.noconfirm:
            ask = input(f"{colors.BOLD}==>{colors.END} Do you want to remove {args.remove} ? Y/n : ")
            if ask == "n":
                print(f"{colors.RED}==> CANCELED{colors.END} : Uninstallation Canceled.")
                return
    except KeyboardInterrupt:
        print(f"\n{colors.RED}==> CANCELED{colors.END} : Uninstallation Canceled.")
        return
    print(f"{colors.CYAN}==>{colors.END} Removing {args.remove}...")
    r = subprocess.run(['sudo', 'pacman', '--noconfirm', flag, args.remove], text=True, stdout=True)
    if not r.returncode == 0:
        print(f"{colors.RED}==> ERROR{colors.END} : An error has occured while deleting the package {args.remove}.")
        return
    print(f"{colors.GREEN}==>{colors.END} Package {args.remove} successfully deleted from the system.")
    with open("/usr/bin/nob_db.txt", "r") as f:
        lines = f.readlines()
    with open("/usr/bin/nob_db.txt", "w") as f:
        for line in lines:
            if args.remove not in line.strip("\n"):
                f.write(line)
    f.close()
    
def download_pckg(pkg, pkg_version):
    download_path = str(f"https://aur.archlinux.org/{pkg}.git")
    print(f"{colors.CYAN}==>{colors.END} Cloning {pkg}'s repository...")
    r = subprocess.run(['pacman', '-Q' , 'git'], text=True, capture_output=True)
    if not r.returncode == 0:
        print(f"{colors.RED}==> ERROR{colors.END} : Missing package 'git'")
        return
    try :
        os.system(f"sudo rm -rf {pckg_archive}")
    except OSError as e:
        if not e.errno == 2:
            print(f"{colors.RED}==> ERROR{colors.END} : Cannot delete existing package .tar.gz : {e}")
    try:
        subprocess.run(['git', 'clone' , download_path], text=True, capture_output=True)
    except Exception as e:
        print(f"{colors.RED}==> ERROR {colors.END} : {e}.")
        return

    install_pckg(pkg_version, pkg)

def install_pckg(pkg_version, pkg):
    print(f"{colors.CYAN}==>{colors.END} Checking required dependencies for makepkg...")
    r = subprocess.run(['pacman', '-Q', 'fakeroot', 'debugedit', 'base-devel'], capture_output=True, text=True)
    if not r.returncode == 0:
        print(f"{colors.YELLOW}==> WARNING{colors.END} : Missing dependencies, Installing them...")
        if not args.noconfirm :
            os.system("sudo pacman -S base-devel fakeroot debugedit")
        else :
            os.system("sudo pacman -S --noconfirm base-devel fakeroot debugedit")

    print(f"{colors.CYAN}==>{colors.END} Going to ./{pkg} directory...")
    try:
        os.chdir(f"./{pkg.lower()}")
    except Exception as e:
        print(f"{colors.RED}==> ERROR{colors.END} : cannot find ./{pkg}.")
        return
    if not args.noconfirm :
        ask = input(f"{colors.BOLD}==>{colors.END} Do you want to read PKGBUILD ? Y/n : ")
        if ask == "n":
            print("Skipping...")
        else : 
            os.system("cat ./PKGBUILD")
            input(f"{colors.BOLD}==>{colors.END} Press any key to continue installation. ")
        

    print(f"{colors.CYAN}==>{colors.END} Executing makepkg")
    #os.system("makepkg -si")
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
    add_db(pkg, pkg_version)

def clean(pkg):
    print(f"{colors.CYAN}==>{colors.END} Cleaning installation...")
    os.chdir("../")
    try:
        os.system(f"sudo rm -rf ./{pkg.lower()}")
    except Exception as e:
        print(f"{colors.RED}==> ERROR{colors.END} : Error while cleaning :{e}.")
        return
        
def installed_aur_pkgs():
    print(f"{colors.CYAN}==>{colors.END} Reading nob's DB...")
    packages = []
    # reading db file + Adding Packages in packages var 
    with open('/usr/bin/nob_db.txt', 'r') as file:
        for lign in file.readlines():
            pckg_name, pckg_ver = lign.strip().split()
            packages.append({
            "pckg_name": pckg_name,
            "pckg_ver": pckg_ver
        })
    nb_packages = len(packages)
    print(f"{colors.GREEN}==>{colors.END} {nb_packages} Package(s) were found installed with nob :")
    for package in packages:
        pkg_name = package['pckg_name']
        pkg_ver =  package['pckg_ver']
        print(f"    {colors.GREEN}==>{colors.END} {pkg_name}/{pkg_ver}")
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
            if ask == "y":
                max_results = results
    for i in range(0, results):
        if i > max_results:
            return 1
        pkg_name = rep['results'][i]['Name']
        pkg_version = rep['results'][i]['Version']
        pkg_maintainer = rep['results'][i]['Maintainer']
        pkg_popularity = rep['results'][i]['Popularity']
        print(f"{colors.GREEN}==>{colors.END} Package found : {pkg_name}/{pkg_version} by {pkg_maintainer} (Pop : {pkg_popularity})")
    return 1

def download_find_pkg(pkg):
    d_Find_URL = f"https://aur.archlinux.org/rpc.php?v=5&type=info&arg={pkg}"
    try : 
        with urllib.request.urlopen(f"{d_Find_URL}") as response:
            data = response.read().decode("utf-8")
            rep = json.loads(data)
        if not rep['results'][0]['URLPath']:
            print(f"{colors.RED}==> ERROR{colors.END} : Cannot find package {pkg} on AUR.")
            return None
    except Exception as e:
        print(f"{colors.RED}==> ERROR{colors.END} : Cannot find package {pkg} on AUR.")
        return None
    pkg_version = rep['results'][0]['Version']
    pkg_maintainer = rep['results'][0]['Submitter']
    pkg_popularity = rep['results'][0]['Popularity']
    print(f"{colors.GREEN}==>{colors.END} Package found for query : {pkg}/{pkg_version} by {pkg_maintainer} .\n")
    return pkg_version, pkg_popularity

def AUR_upgr():
    packages = []
    # reading db file + Adding Packages in packages var 
    with open('/usr/bin/nob_db.txt', 'r') as file:
        for lign in file.readlines():
            pckg_name, pckg_ver = lign.strip().split()
            packages.append({
            "pckg_name": pckg_name,
            "pckg_ver": pckg_ver
        })
    print(f"{colors.CYAN}==>{colors.END} Checking for AUR packages updates...")
    #Check for updates && check if package is on th AUR.
    for package in packages:
        pkg_name = package['pckg_name']
        try:
            with urllib.request.urlopen(f"https://aur.archlinux.org/rpc.php?v=5&type=info&arg={pkg_name}") as response:
                data = response.read().decode("utf-8")
                rep = json.loads(data)
        except Exception as e:
            print(f"{colors.RED}==> ERROR{colors.END} : Cannot connect to AUR, {e}")
            return
        try : 
            pkg_version = rep['results'][0]['Version']
            result_name = rep['results'][0]['Name']
        except Exception:
            print(f"{colors.RED}==> ERROR{colors.END} : DATABASE corrupted. Manual repair needed (PACKAGE {pkg_name} found in database but not in AUR).")
            return
        if pkg_version != package['pckg_ver']:
            print(f"{colors.CYAN}==>{colors.END} Available update found : {pkg_name}{colors.RED}{package['pckg_ver']}{colors.END} ==> {pkg_name}{colors.GREEN}{pkg_version}{colors.END}.")
            if not args.noconfirm:
                ask = input(f"{colors.BOLD}==> ASK{colors.END} : Do you want to update {pkg_name} ? Y/n : ")
                if ask == 'n':
                    print(f"\n{colors.RED}==> CANCELED{colors.END} : Update Canceled.")
                    return
            print(result_name, pkg_version)
            download_pckg(result_name, pkg_version)
            
                
                    
    print(f"{colors.CYAN}==>{colors.END} No available updates found.")
    return

main()
