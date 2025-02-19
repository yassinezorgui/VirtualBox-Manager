import curses
import subprocess
import re
from typing import List, Tuple

class VBoxManager:
    def __init__(self):
        self.screen = None
        self.current_row = 0
        self.vms = []

    def get_vms(self) -> List[Tuple[str, str]]:
        """Get list of VMs from VBoxManage"""
        try:
            result = subprocess.run(['VBoxManage', 'list', 'vms'], 
                                 capture_output=True, text=True)
            vms = []
            for line in result.stdout.splitlines():
                match = re.match(r'"([^"]+)" {(.+)}', line)
                if match:
                    vms.append((match.group(1), match.group(2)))
            return vms
        except FileNotFoundError:
            return []

    def draw_menu(self, options: List[str], title: str = ""):
        """Draw menu with given options"""
        self.screen.clear()
        h, w = self.screen.getmaxyx()
        
        if title:
            self.screen.addstr(0, 0, title, curses.A_BOLD)
        
        for idx, option in enumerate(options):
            x = w//4
            y = h//4 + idx
            if idx == self.current_row:
                self.screen.attron(curses.color_pair(1))
                self.screen.addstr(y, x, option)
                self.screen.attroff(curses.color_pair(1))
            else:
                self.screen.addstr(y, x, option)
        
        self.screen.refresh()

    def vm_actions(self, vm_name: str):
        """Handle actions for selected VM"""
        actions = [
            f"Start VM: {vm_name}",
            f"Show VM Info: {vm_name}",
            f"Delete VM: {vm_name}",
            "Back"
        ]
        
        while True:
            self.draw_menu(actions, f"VM Actions - {vm_name}")
            key = self.screen.getch()
            
            if key == curses.KEY_UP and self.current_row > 0:
                self.current_row -= 1
            elif key == curses.KEY_DOWN and self.current_row < len(actions)-1:
                self.current_row += 1
            elif key == ord('\n'):
                if self.current_row == 0:  # Start VM
                    subprocess.run(['VBoxManage', 'startvm', vm_name])
                elif self.current_row == 1:  # Show VM Info
                    # Get VM info
                    result = subprocess.run(['VBoxManage', 'showvminfo', vm_name], 
                                         capture_output=True, text=True)
                    info_lines = result.stdout.splitlines()
                    
                    # Initialize paging
                    page_size = self.screen.getmaxyx()[0] - 4  # Leave room for header/footer
                    current_page = 0
                    total_pages = (len(info_lines) + page_size - 1) // page_size
                    
                    while True:
                        self.screen.clear()
                        # Show header
                        self.screen.addstr(0, 0, f"VM Info - {vm_name} (Page {current_page + 1}/{total_pages})", curses.A_BOLD)
                        self.screen.addstr(1, 0, "use UP/DOWN to scroll, q to return")
                        
                        start_idx = current_page * page_size
                        for i, line in enumerate(info_lines[start_idx:start_idx + page_size]):
                            self.screen.addstr(i + 2, 0, line[:self.screen.getmaxyx()[1]-1])
                        
                        self.screen.refresh()
                        key = self.screen.getch()
                        
                        if key == curses.KEY_UP and current_page > 0:
                            current_page -= 1
                        elif key == curses.KEY_DOWN and current_page < total_pages - 1:
                            current_page += 1
                        elif key == ord('q'):
                            break
                elif self.current_row == 2:  # Delete VM
                    subprocess.run(['VBoxManage', 'unregistervm', vm_name, '--delete'])
                    break
                elif self.current_row == 3:  # Back
                    break
            elif key == ord('q'):
                break

    def create_vm(self):
        """Create new VM (basic implementation)"""
        # TODO: Implement interactive VM creation
        self.screen.clear()
        self.screen.addstr(5, 10, "Create VM feature coming soon...q to return")
        self.screen.refresh()
        self.screen.getch()

    def main(self, stdscr):
        self.screen = stdscr
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)   
        curses.curs_set(0)

        self.screen.addstr(1, 1, """/)  /)   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
( •-• ) ~ | VirtualBox Manager V0.4    |
/   /   ~ | use with caution!          |
          | enter to continue...       |
          | q to quit.                 |
          ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛""")
        
        self.screen.refresh()
        self.screen.getch()
        
        while True:
            self.vms = self.get_vms()
            options = ["Create New VM"]
            options.extend([f"Select VM: {vm[0]}" for vm in self.vms])
            options.append("Quit")
            
            self.draw_menu(options, "VirtualBox Manager")
            
            key = self.screen.getch()
            
            if key == curses.KEY_UP and self.current_row > 0:
                self.current_row -= 1
            elif key == curses.KEY_DOWN and self.current_row < len(options)-1:
                self.current_row += 1
            elif key == ord('\n'):
                if self.current_row == 0:  # Create New VM
                    self.create_vm()
                elif self.current_row == len(options)-1:  # Quit
                    break
                else:  # Select VM
                    vm_name = self.vms[self.current_row-1][0]
                    self.vm_actions(vm_name)
            elif key == ord('q'):
                break

def main():
    try:
        manager = VBoxManager()
        curses.wrapper(manager.main)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()