# xround

A Python script to add rounded corners to X-based displays.

xround uses [python-xlib](https://github.com/python-xlib/) and X's Shape extension to draw faux corners above the user's display. The corners are #000000 and will persist across workspaces and above all (most) windows.

[![xround.png](https://s3.postimg.org/serjvz1w3/xround.png)](https://postimg.org/image/pkoeiizpr/)

## Installation:

```sh
pip install xround
```

Or call the script directly with [python-xlib](https://github.com/python-xlib/) installed.

## Usage:

```sh

# Running the script without flags uses defaults of 16 for all corners
xround.py

# Set which corners to display using cardinal direction (nw,ne,se,sw) in any order (case insensitive)
xround.py --corners NW,NE
xround.py --corners NW,ne,SE

# Set the size of the corners
xround.py --size 24
xround.py --size 32
xround.py --corners NW,NE --size 20
```

## Todo / Further Ideas :

1. Make the corners less jagged, perhaps by using a compositor of some sort, or a method to draw pixels with varying alpha values along the edges of each corner's pixmap.
1. Find a way to keep the corners above a fullscreen'ed window.
1. Create an optional way to prevent the mouse pointer from going underneath each corner.
1. Options to set individual sizes for each corner.
