import pyalpm
import pycman
from pathlib import Path
import subprocess
from colors import Colors 
import tempfile
colors = Colors()
class alpm:
    @staticmethod
    def a(tmpdir):
        global pacdb
        def dumbo(config: str, dbpath : Path, arch : str):
            dbpath.mkdir(exist_ok=True)
            confpath = dbpath / "pacman.conf"
            if not confpath.is_file():
                confpath.write_text(config.format(pacdbpath=dbpath, arch=arch))
            return pycman.config.init_with_config(confpath)
        PACCONF = """
            [options]
            RootDir     = /
            DBPath      = {pacdbpath}
            CacheDir    = {pacdbpath}
            LogFile     = {pacdbpath}
            # Use system GPGDir so that we don't have to populate it
            GPGDir      = /etc/pacman.d/gnupg/
            Architecture = {arch}

            [core]
            Include = /etc/pacman.d/mirrorlist

            [extra]
            Include = /etc/pacman.d/mirrorlist

            [multilib]
            Include = /etc/pacman.d/mirrorlist
        """

        pacdb = dumbo(PACCONF, tmpdir, arch="x86_64")

    with tempfile.TemporaryDirectory() as tmpdir:
        a(Path(tmpdir))
    handle = pyalpm.Handle("/", "/var/lib/pacman")
    localdb = handle.get_localdb()
        
    def update(noconfirm = False):
        localdb = alpm.localdb
        orphan_packages = []
        non_orphan_deps =  []
        download_size = 0
        install_size = 0
        print(f"{colors.CYAN}==>{colors.END} Syncing databases. Please wait.")
        for db in pacdb.get_syncdbs():
            try:
                db.update(False)
            except pyalpm.error as e:
                print(f"{colors.RED}==> ERROR{colors.END} : Error while syncing databases : {e}")
                return
        
        for db in pacdb.get_syncdbs():
            if len(db.pkgcache) <= 0 : continue
            print(f"{colors.CYAN}==>{colors.END} Checking updates for [{db.name}].")
            upgrades = []
            for pkg in db.pkgcache:
                
                local_pkg = localdb.get_pkg(pkg.name)
                if not local_pkg: continue
                if pyalpm.vercmp(pkg.version, local_pkg.version) > 0:
                    for conflict_name in pkg.conflicts:
                        conflict_pkg = localdb.get_pkg(conflict_name)
                        if conflict_pkg:
                            print(f"{colors.YELLOW}==> WARNING{colors.END}: {pkg.name} conflicts with installed package {conflict_name}")
                    download_size += pkg.size
                    install_size += pkg.isize - local_pkg.isize
                    upgrades.append((pkg.name, local_pkg.version, pkg.version))
            if upgrades:
                for name, old_ver, new_ver in upgrades:
                    print(f"{colors.GREEN}==> {colors.END}{name}: {colors.RED}{old_ver}{colors.END} -> {colors.GREEN}{new_ver}{colors.END}")

        if download_size <= 0:
            print(f"{colors.PURPLE}==>{colors.END} There is nothing to do"); return 
                    
        print(f"{colors.CYAN}==>{colors.END} Estimated download size : {download_size / (1024 * 1024):.2f} MiB")
        print(f"{colors.CYAN}==>{colors.END} Estimated Net Upgrade Size  : {install_size / (1024 * 1024):.2f} MiB")
        
        if not noconfirm: 
            ask = input(f"{colors.BOLD}==>{colors.END} Do you want to continue upgrade ? Y/n : ")
            if ask.lower() == "n":
                print(f"{colors.RED}==> CANCELED{colors.END} : Upgrade Canceled.")
                return
        
        subprocess.run(['sudo', 'pacman', '-Syu', '--noconfirm' ], text=True, stdout=True)
        #checking if a dependency package is orphan
        for pkg in localdb.pkgcache:
            # checking used_deps
            for dependency in pkg.depends:
                non_orphan_deps.append(dependency)
        for pkg in localdb.pkgcache:
            if pkg.reason == pyalpm.PKG_REASON_DEPEND and not pkg.name in non_orphan_deps :
                orphan_packages.append(pkg.name)
        print(f"{colors.YELLOW}==> WARNING{colors.END} : I found {len(orphan_packages)} Orphan packages on your system :\n{'    '.join(orphan_packages)}")

        

    def getpkgslist(): 
        localdb = alpm.localdb
        pkgs =  {}
        for pkg in localdb.pkgcache:
            pkgs[pkg.name] = pkg.version
        return pkgs
    
    def version(): return pyalpm.version()
