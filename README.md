# Diagram Studio – flowchart editor using Python
## Usage Guide

Diagram Studio is a lightweight flowchart editor written in Python using Tkinter.  
It allows you to create boxes, decision nodes, and arrows, move elements freely, zoom the canvas, and export/import diagrams using a simple text format.

## Python Version Compatibility
You at least need Python version **3.6**.

## Features

- Create normal boxes and decision boxes  
- Drag boxes freely across the canvas  
- Easy navigation
- Connect boxes with nameable arrows 
- Add/remove a star marker on boxes  
- Export diagrams to a text format/Import diagrams from a text file (the boxes will still be in the same position)
- Dark Mode  

## Controls & Hotkeys

### Box Creation
| Hotkey | Action |
|--------|--------|
| **Ctrl + A** | Create a normal box |
| **Ctrl + Y** | Create a decision box |

---

### Editing Text (box)
| Action | How |
|--------|-----|
| edit a box | **right click** on text inside the box |
| Finish editing a box | Press **Enter** |
| Toggle star (*) at end of text * | **Alt + Double‑Click** on the box |

###### *I use this, for example, when I want to mark something so I know I still need to make changes there.
---

### Right‑Click Menu (on a box)
| Option | Description |
|--------|-------------|
| **Delete Box** | Removes the box |
| **Delete Connections** | Removes all arrows connected to the box |
| **Connect** | Start creating an arrow to another box |

---

### Arrows (Connections)
| Action | How |
|--------|-----|
| Start connecting | Right‑Click Menu → **Connect** |
| Finish connecting | Click another box |
| Rename arrow | **double‑click** the arrow |

Arrows automatically attach to the correct edge of each box.

!!! **If the arrows are bugging around out, you can simply zoom in or out and they'll work again.** !!!

---

### Mouse Controls
| Action | How |
|--------|-----|
| Move Boxes | **hold down left-click** on box and **Drag** to move it |
| Pan Background | **hold down left-click** on empty space and **Drag** to move it |
| Zoom | **Mouse wheel** scroll * |
###### *Zoom centers on the mouse position, text fields do not scale (stay readable)

## Inport/Export

Exports the entire diagram into a text format and you can inport it when you reopen Diagram Studio.

