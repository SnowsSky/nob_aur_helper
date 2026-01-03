# Welcome to a simple AUR helper written in python named nob 
 # 1 - Downloading 🛜.
  - To download nob you need to clone the repo ->
  `git clone ....`
  - or, download the latest release to have 'PKGBUILD'
 # 2 - Installing ⬇️.
   ## 2.1 - Checking dependencies for `makepkg -si`
   - Run `pacman -S base-devel fakeroot debugedit`
  - Run `makepkg -si` in the folder you had download.
   ## 2.2 - Install arch-update
   - When nob is installed, we highly recommend you to install the arch-update package with 'nob -S arch-update', if you do not, an error will show when trying to run 'nob', and nob will show upgrades instead of arch-update.
 # 3 - Use it
  - You can now use it by doing `nob -h` or just 'nob' to update.
  - DO NOT run nob with sudo or logged with root otherwise somes commands will break especially nob -Sa and nob -S
 # 4 - Documentation
  ## 4.1 - Arch-Update TUI settings
    - You can edit Arch-Update settings with '-nob -arch-update-settings' which will open a TUI to help you while configuring it. 

