import tkinter as tk
from tkinter import simpledialog, filedialog
import math
def get_edge_point(node, target):
    cx, cy = node.get_center()
    tx, ty = target.get_center()

    dx = tx - cx
    dy = ty - cy

    if dx == 0 and dy == 0:
        return cx, cy

    w = node.width / 2
    h = node.height / 2

    if node.kind == "decision":
        if abs(dx) > abs(dy):
            return (node.x + node.width, node.y + h) if dx > 0 else (node.x, node.y + h)
        else:
            return (node.x + w, node.y + node.height) if dy > 0 else (node.x + w, node.y)

    if abs(dx) > abs(dy):
        return (node.x + node.width, cy) if dx > 0 else (node.x, cy)
    else:
        return (cx, node.y + node.height) if dy > 0 else (cx, node.y)

class Node:
    def __init__(self, canvas, x, y, text, kind="normal", index=0):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.text = text
        self.kind = kind
        self.index = index

        self.width = 160
        self.height = 70

        self.bg_normal = "#3C3C3C"
        self.bg_decision = "#454545"
        self.text_color = "#E6E6E6"
        self.border_color = "#5A5A5A"

        if self.kind == "decision":
            self.rect = canvas.create_polygon(
                x, y + self.height/2,
                x + self.width/2, y,
                x + self.width, y + self.height/2,
                x + self.width/2, y + self.height,
                fill=self.bg_decision, outline=self.border_color, width=2
            )
        else:
            self.rect = canvas.create_rectangle(
                x, y, x + self.width, y + self.height,
                fill=self.bg_normal, outline=self.border_color, width=2
            )

        self.entry = tk.Entry(
            canvas, bd=0, justify="center",
            bg=self.bg_normal, fg=self.text_color,
            insertbackground=self.text_color,
            font=("Segoe UI", 11)
        )
        self.entry.insert(0, text)
        self.entry_window = canvas.create_window(
            x + self.width/2, y + self.height/2,
            window=self.entry, width=self.width-20
        )

        self.entry.bind("<FocusOut>", self.on_focus_out)
        self.entry.bind("<Return>", self.on_enter)

        self.edges = []

    def on_enter(self, event):
        self.canvas.focus_set()
        return "break"

    def on_focus_out(self, event):
        txt = self.entry.get().strip()
        if txt == "":
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f"Entscheidung {self.index}" if self.kind == "decision" else f"Box {self.index}")

    def get_center(self):
        return (self.x + self.width/2, self.y + self.height/2)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.entry_window, dx, dy)
        for e in self.edges:
            e.update_position()

    def add_star_toggle(self):
        txt = self.entry.get()
        if txt.endswith("*"):
            self.entry.delete(0, tk.END)
            self.entry.insert(0, txt[:-1])
        else:
            self.entry.insert(tk.END, "*")


class Edge:
    def __init__(self, canvas, src, dst, label=""):
        self.canvas = canvas
        self.src = src
        self.dst = dst
        self.label_text = label

        self.line = canvas.create_line(
            0, 0, 0, 0,
            arrow=tk.LAST,
            fill="#FFFFFF",
            width=2
        )

        self.hitbox = canvas.create_line(
            0, 0, 0, 0,
            width=12,
            fill="",
            activefill="",
            state="normal"
        )

        self.label = canvas.create_text(
            0, 0,
            text=self.label_text,
            fill="#FFFFFF",
            font=("Segoe UI", 10)
        )

        src.edges.append(self)
        dst.edges.append(self)

        self.update_position()

    def update_position(self):
        x1, y1 = get_edge_point(self.src, self.dst)
        x2, y2 = get_edge_point(self.dst, self.src)

        self.canvas.coords(self.line, x1, y1, x2, y2)
        self.canvas.coords(self.hitbox, x1, y1, x2, y2)
        self.canvas.coords(self.label, (x1+x2)/2, (y1+y2)/2 - 10)

    def rename(self):
        new = simpledialog.askstring("Pfeil benennen", "Neuer Name:")
        if new:
            self.label_text = new
            self.canvas.itemconfig(self.label, text=new)


class DiagramApp:
    def __init__(self, root):
        self.root = root
        root.title("Diagram Studio – Windows Dark Mode")

        self.canvas = tk.Canvas(root, bg="#141414")
        self.canvas.pack(fill="both", expand=True)

        bottom = tk.Frame(root, bg="#141414")
        bottom.pack(fill="x")

        tk.Button(bottom, text="Export", command=self.export_text,
                  bg="#3A3A3A", fg="#E6E6E6").pack(side="left", padx=5)
        tk.Button(bottom, text="Import", command=self.import_text,
                  bg="#3A3A3A", fg="#E6E6E6").pack(side="left", padx=5)

        self.nodes = []
        self.edges = []
        self.drag_node = None
        self.drag_start = None
        self.pan_start = None
        self.connect_mode = False
        self.connect_source = None

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_left)
        self.canvas.bind("<Alt-Double-Button-1>", self.on_alt_double_left)


        self.canvas.bind("<MouseWheel>", self.zoom)

        root.bind("<Control-a>", self.hotkey_add_box)
        root.bind("<Control-y>", self.hotkey_add_decision)

    def hotkey_add_box(self, event):
        self.add_box()
        return "break"

    def hotkey_add_decision(self, event):
        self.add_decision_box()
        return "break"

    def on_left_click(self, event):
        n = self.find_node(event.x, event.y)
        if n:
            if self.connect_mode and self.connect_source and self.connect_source is not n:
                e = Edge(self.canvas, self.connect_source, n)
                self.edges.append(e)
                self.connect_mode = False
                self.connect_source = None
            else:
                self.drag_node = n
                self.drag_start = (event.x, event.y)
        else:
            self.drag_node = None
            self.pan_start = (event.x, event.y)

    def on_drag(self, event):
        if self.drag_node:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.drag_node.move(dx, dy)
            self.drag_start = (event.x, event.y)
        elif self.pan_start:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.canvas.move("all", dx, dy)
            self.pan_start = (event.x, event.y)

    def on_left_release(self, event):
        self.drag_node = None
        self.pan_start = None

    def zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9

        entry_windows = [n.entry_window for n in self.nodes]
        for item in self.canvas.find_all():
            if item not in entry_windows:
                self.canvas.scale(item, event.x, event.y, factor, factor)

        for n in self.nodes:
            bbox = self.canvas.bbox(n.rect)
            if not bbox:
                continue

            x1, y1, x2, y2 = bbox
            n.x = x1
            n.y = y1
            n.width = x2 - x1
            n.height = y2 - y1

            cx = n.x + n.width / 2
            cy = n.y + n.height / 2
            self.canvas.coords(n.entry_window, cx, cy)

        for e in self.edges:
            e.update_position()

    def add_box(self):
        idx = len(self.nodes) + 1
        x, y = (self.nodes[-1].x, self.nodes[-1].y + 140) if self.nodes else (100, 100)
        node = Node(self.canvas, x, y, "", "normal", idx)
        self.nodes.append(node)

        if len(self.nodes) > 1:
            self.edges.append(Edge(self.canvas, self.nodes[-2], node))

        node.entry.focus_set()

    def add_decision_box(self):
        idx = len(self.nodes) + 1
        x, y = (self.nodes[-1].x + 220, self.nodes[-1].y) if self.nodes else (300, 100)
        node = Node(self.canvas, x, y, "", "decision", idx)
        self.nodes.append(node)
        node.entry.focus_set()

    def find_node(self, x, y):
        items = self.canvas.find_overlapping(x, y, x, y)
        for n in self.nodes:
            if n.rect in items or n.entry_window in items:
                return n
        return None

    def find_edge(self, x, y):
        items = self.canvas.find_overlapping(x, y, x, y)
        for e in self.edges:
            if e.line in items or e.hitbox in items or e.label in items:
                return e
        return None

    def on_double_left(self, event):
        e = self.find_edge(event.x, event.y)
        if e:
            e.rename()

    def on_alt_double_left(self, event):
        n = self.find_node(event.x, event.y)
        if n:
            n.add_star_toggle()

    def on_right_click(self, event):
        n = self.find_node(event.x, event.y)
        if not n:
            return

        menu = tk.Menu(self.root, tearoff=0, bg="#2A2A2A", fg="#E6E6E6")
        menu.add_command(label="Box löschen", command=lambda: self.delete_node(n))
        menu.add_command(label="Verbindungen löschen", command=lambda: self.delete_edges(n))
        menu.add_command(label="Verbinden", command=lambda: self.start_connect(n))
        menu.post(event.x_root, event.y_root)

    def delete_edges(self, node):
        rem = []
        for e in self.edges:
            if e.src is node or e.dst is node:
                self.canvas.delete(e.line)
                self.canvas.delete(e.hitbox)
                self.canvas.delete(e.label)
                rem.append(e)
        for e in rem:
            self.edges.remove(e)
        node.edges = []

    def delete_node(self, node):
        self.delete_edges(node)
        self.canvas.delete(node.rect)
        self.canvas.delete(node.entry_window)
        self.nodes.remove(node)

    def start_connect(self, node):
        self.connect_mode = True
        self.connect_source = node

    # Import / Export
    def export_text(self):
        data = []
        for i, n in enumerate(self.nodes):
            data.append(f"NODE {i} {n.x} {n.y} {n.kind} {n.entry.get()}")
        for e in self.edges:
            s = self.nodes.index(e.src)
            d = self.nodes.index(e.dst)
            data.append(f"EDGE {s} {d} {e.label_text}")

        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(data))

    def import_text(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        self.canvas.delete("all")
        self.nodes = []
        self.edges = []

        temp = {}

        for line in lines:
            if line.startswith("NODE"):
                _, idx, x, y, kind, text = line.split(" ", 5)
                n = Node(self.canvas, int(x), int(y), text, kind, int(idx)+1)
                self.nodes.append(n)
                temp[int(idx)] = n

        for line in lines:
            if line.startswith("EDGE"):
                _, s, d, label = line.split(" ", 3)
                self.edges.append(Edge(self.canvas, temp[int(s)], temp[int(d)], label))


if __name__ == "__main__":
    root = tk.Tk()
    app = DiagramApp(root)
    root.mainloop()
