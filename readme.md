# Welcome to a simple AUR helper written in python named nob 
 # 1 - Downloading 🛜.
  - To download nob you need to clone the repo ->
  `git clone ....`
  - or, download the latest release to have 'PKGBUILD'
 # 2 - Installing ⬇️.
   ## 2.1 - Checking dependencies for `makepkg -si`
   - Run `pacman -S base-devel fakeroot debugedit
  - Run `makepkg -si` in the folder you had download.
   ## 2.2 - Install arch-update
   - When nob is installed, we highly recommend you to install the arch-update package with 'nob -S arch-update', if you do not, an error will show when trying to run 'nob' and `pacman -Syu` will be run instead.
 # 3 - Use it
  - You can now use it by doing `nob -h` or just 'nob' to update.
  - DO NOT run nob with sudo or logged with root otherwise somes commands will break especially nob -Sa and nob -S
 # 4 - Documentation
  ## 4.1 - How to use nob ?
   - To install a package from the AUR run : `nob -S pkg1 pkg2.....`
   - To upgrade `nob -Sa`
   - To list installed AUR packages, run : `nob -Qa`
   - If you were using another AUR helper before nob you'll need to run `nob --auto-detect`
   - You can install localy package if they were installed with `nob -U`, packages cache folder is located at /var/cache/nob/pkgs/
   - To Clear the cache, you can run `nob --clean-cache`
  ## 4.2 - Arch-Update TUI settings
    - You can edit Arch-Update settings with `-nob -arch-update-settings` which will open a TUI to help you while configuring it. 
  ## 4.3 - Remove nob
    - You just need to do `sudo pacman -Rns nob_aur_helper` and then do : `sudo rm -r /var/cache/nob/`.
