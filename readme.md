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
   - When nob is installed, we highly recommend you to install the arch-update package with 'nob -S arch-update', if you do not, an error will show when trying to run 'nob' and 'pacman -Syu' will be run instead.
 # 3 - Use it
  - You can now use it by doing `nob -h` or just 'nob' to update.

