#!/usr/bin/python3
import os, sys
import curses, random

import modules

screen  = curses.initscr()
width   = screen.getmaxyx()[1]
height  = screen.getmaxyx()[0]
size    = width*height
# menu    = {"chat" : korchat}
curses.start_color()
curses.init_pair(1,0,0)
curses.init_pair(2,1,0)
curses.init_pair(3,3,0)
curses.init_pair(4,4,0)

print(modules.__all__)

while True:
    screen.clear()
    screen.border()
    # menu_x = 2
    # menu_y = 1
    # for m in menu:
    #     screen.addstr(menu_x, menu_y, m)
    #     menu_x += 2
    #     menu_y += 2
    screen.addstr(height - 3, 2, "Enter command:")
    screen.refresh()
    try:
        cmd = screen.getstr(height - 2, 2, 60).decode('latin-1')
        if 'exit' in cmd:
            break
        if cmd in modules.__all__:
            mo = getattr(modules, cmd)
            # try:
            #     runner = mo.korchat
            # except AttributeError:
            #     screen.addstr(2, 2, "the module does not have run function")
            #     continue

            mo.run()
            # runner.run()
    except KeyboardInterrupt as e:
        break
    screen.refresh()
    # screen.getch()
    # screen.timeout(30)
    # if (screen.getch()!=-1): break

curses.endwin()