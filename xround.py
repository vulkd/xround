#!/usr/bin/python
#from __future__ import print_function
import sys
import os
import getopt

from Xlib import X, display, protocol
from Xlib.ext import shape


global hasRun
hasRun = False

display = display.Display()
screen = display.screen()

screenResolution = screen.root.get_geometry()
screenResolution = [screenResolution.width, screenResolution.height]

if not display.has_extension("SHAPE"): # Need X's shape extension
    sys.stderr.write("%s: X server has no SHAPE extension\n")
    sys.exit(1)


def create_window(bg_size, corners): # This function serves to create the window and pixmaps, but does not map them
    bg_size = bg_size # Size of the corners in pixels
    bg_pm = screen.root.create_pixmap(bg_size, bg_size, screen.root_depth)
    bg_gc = screen.root.create_gc(foreground = screen.black_pixel, background = screen.black_pixel)
    bg_pm.fill_rectangle(bg_gc, 0, 0, bg_size, bg_size)

    window = screen.root.create_window(
                                0, 0, screenResolution[0], screenResolution[1], 0,
                                screen.root_depth,
                                background_pixmap = bg_pm,
                                event_mask = (X.StructureNotifyMask)
                                )

    def draw_corner(arc_start, arc_one, arc_two, pos_x, pos_y, pos_in_x=0, pos_in_y=0): # Draws a corner. TODO: Explain params
        global hasRun
        def draw_corner_pixmap(arc_start, arc_one, arc_two, pos_in_x=0, pos_in_y=0):
            corner_pm = window.create_pixmap(bg_size, bg_size, 1)
            corner_gc = corner_pm.create_gc(foreground = 1, background = 1)
            corner_pm.fill_rectangle(corner_gc, 0, 0, bg_size, bg_size)
            corner_gc.change(foreground = 0)
            corner_pm.fill_arc(corner_gc, pos_in_x, pos_in_y, bg_size, bg_size, arc_start, arc_one * arc_two)
            return corner_pm

        corner_pixmap = draw_corner_pixmap(arc_start, arc_one, arc_two, pos_in_x, pos_in_y)

        if hasRun == False: # If function hasn't run, use shape.SO.Set to initiate shape(s), otherwise add to mask with shape.SO.Union
            window.shape_mask(shape.SO.Set, shape.SK.Bounding, pos_x, pos_y, corner_pixmap)
            hasRun = True
        else:
            window.shape_mask(shape.SO.Union, shape.SK.Bounding, pos_x, pos_y, corner_pixmap)
        return

    sz = bg_size // 2
    if "nw" in corners: # Check for the co-ord in corners array (that can be changed by user)
        draw_corner(11520, -90, 64, -sz, -sz, sz, sz)
    if "ne" in corners:
        draw_corner(0, 90, 64, screenResolution[0]-sz, -sz, -sz, sz)
    if "se" in corners:
        draw_corner(0, -90, 64, screenResolution[0]-sz, screenResolution[1]-sz, -sz, -sz)
    if "sw" in corners:
        draw_corner(-5760, -90, 64, -sz, screenResolution[1]-sz, sz, -sz)

    window.shape_select_input(0)

    return window


def set_wm_state(window, action, data): # Function to set window states via Xlib
# Thanks parkouss for help with this (https://github.com/parkouss/pyewmh/blob/master/ewmh/ewmh.py)
    if action == "_NET_WM_STATE":
        data[1] = display.get_atom(data[1], 1) # Get the int for associated action, as X wants this in data array, not a string

    event = protocol.event.ClientMessage(
            window = window,
            client_type = display.get_atom(action),
            data = (32, data))

    screen.root.send_event(event, event_mask=(X.SubstructureRedirectMask))


def usage():
    print('''xround 2017

Usage: "xround [--size 16] [--corners nw,ne,sw,se]""

Flags:
    --corners     Choose which corners to display eg; "xround --corners sw,se".
    --size        Choose the size of corners eg; "xround --size 32".
    -h --help     Display this help screen.
    ''')
    sys.exit()


def main(argv):

    bg_size = 16 # Default corner size
    corners = ['nw','ne','se','sw'] # Default corners to draw

    try:
        opts, args = getopt.getopt(argv, "h", ["help", "corners=", "size="])
    except:
        return usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            return usage()
        elif opt in ("--corners"):
            corners = ''.join(str(arg)).lower()
            if not any(sz in corners for sz in ["nw","ne","sw","se"]):
                return usage()
        elif opt in ("--size"):
            try:
                bg_size = int(arg)
            except:
                return usage()

    for arg in sys.argv:
        print(arg)

    window = create_window(bg_size, corners) # Make the window using specified size / corners
    window.map() # Make the window appear

    while True:
        e = display.next_event()

        set_wm_state(window, "_NET_WM_DESKTOP", data=[0xFFFFFFFF, 1, 0, 0, 0]) # Keeps window on all workspaces
        set_wm_state(window, "_NET_WM_STATE", data=[1, "_NET_WM_STATE_SKIP_TASKBAR", 0, 1, 0]) # Removes window from task list
        set_wm_state(window, "_NET_WM_STATE", data=[1, "_NET_WM_STATE_ABOVE", 0, 1, 0]) # Keeps window above (almost all) other windows

        # TODO: How to keep above fullscreened windows (F11 sublime / chrome / etc.) ? This doesn't work:
        # set_wm_state(window, "_NET_WM_STATE", data=[1, "_NET_WM_STATE_FULLSCREEN", 0, 1, 0])

        display.flush() # Is this really needed? Seems to work fine without

if __name__ == "__main__":
    #print("PID: " + str(os.getpid()))
    main(sys.argv[1:])
