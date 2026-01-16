from curses import *
# TUI VER 1.1.1
class TUI():
    def __init__(self, timer = "60", disabled = False):
        self.timer = timer 
        self.disabled = disabled
        def main(stdscr):
            stdscr.clear()
            
            stdscr.refresh()
            height, width = stdscr.getmaxyx()
            title = "=> NOB - Arch-Update settings [INDEV] <="
            title_width = (width // 2) - len(title) // 2

            win = newwin(height, width, 0, 0)
            win.box()

            options = [f"==> Change Arch-update timer check", f"==> Disable arch-update.timer","press Q to quit [save changes]"]
            win.addstr(0, title_width, title, A_BOLD)
            for i, option in enumerate(options): win.addstr(i + 1, 2, f"  {option}")
            win.refresh()
            key = None
            current_selection = -1
            while key != ord('q') and key != ord('Q'):
                win.clear()
                win.box()

                def update(): 
                    for i, option in enumerate(options):
                        win.addstr(0, title_width, title, A_BOLD)
                        if i == current_selection:
                            if current_selection == 0:
                                win.addstr(i + 1, 2, f"> {option} : [CURRENT : {self.timer}min]", A_STANDOUT)
                            else :
                                win.addstr(i + 1, 2, f"> {option} : [Arch-Update DISABLED : {self.disabled}]", A_STANDOUT)
                        else:
                            win.addstr(i + 1, 2, f"  {option}")
                        
                
                key = stdscr.getch()
                if key == KEY_UP:
                    if current_selection > 0 : current_selection -= 1
                    update()
                elif key == KEY_DOWN:
                    if current_selection < len(options) -2 : current_selection += 1
                    update()
                elif key == 10 or key == 13:  # Enter key
                    if current_selection == 0:
                        win.addstr(5, 1, "New time value (min) : ")
                        echo()
                        new_time = win.getstr(5, 18, 5).decode('utf-8')
                        self.timer = float(new_time)
                        if self.timer <= 0:
                            self.timer = 60
                        noecho()
                        win.addstr(6, 1, f"new time set : {self.timer}min ")
                        win.refresh()
                        
                        update()
                        win.refresh()

                        echo()
                    elif current_selection == 1:
                        self.disabled = not self.disabled
                        status = "Disabled" if self.disabled else "Enabled"
                        win.addstr(5, 1, f"Arch-update.timer is now {status} ")
                        win.refresh()
                        update()
                else:
                    update()
                win.refresh()
            win.clear()
            win.refresh()
            return self.timer, self.disabled
        

            
        wrapper(main)
