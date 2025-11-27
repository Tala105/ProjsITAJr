import tkinter as tk
import tkinter.simpledialog as simpledialog
from PIL import ImageTk, Image
from ctypes import *


# CLib Prep
class board(Structure):
    _fields_= [
            ("state", c_char*67)
    ]

lib_path = './tree_linux.so'
try:
    treelib = CDLL(lib_path)
except OSError as e:
    print(f"Smt's wrn: {e}")
    raise

treelib.createBoard.restype = (board)
treelib.deepLines.argtypes = (board, c_int, c_int, c_void_p)
treelib.deepLines.restype = (c_char_p)

CommentCb = CFUNCTYPE(None, POINTER(c_char))
PromotionCb = CFUNCTYPE(None, POINTER(c_char))
treelib.getMove.argtypes = (board, POINTER(c_int), c_char_p, CommentCb, PromotionCb)
treelib.getMove.restype = (board)

sqlite3 = CDLL("libsqlite3.so")
sqlite3.sqlite3_open.argtypes = [c_char_p, POINTER(c_void_p)]
sqlite3.sqlite3_open.restype = c_int


b = treelib.createBoard()
db = c_void_p()
sqlite3.sqlite3_open(b"optree.db", byref(db))

root = tk.Tk()
root.title("Chess Opening Explorer")
rw=192*5
rh=108*5
root.geometry(f"{rw}x{rh}")
root.resizable(width=True, height=True)


# Make Board
pieces_id: dict[tuple[int,int], tuple[str, int]] = {}
imgs = []
bw=rh
bh=rh
board_canvas = tk.Canvas(root, name="board", width=bw, height=bh, bg="black")
board_canvas.pack(side="left", fill="y")

def draw_piece(bo, i, j):
    piece = chr(bo.state[8*j+i])
    if piece != ' ':
        name = "w" if piece.islower() else "b"
        img = Image.open(f"./pieces/{name + piece.lower()}.png")
        img = img.convert("RGBA")
        img = img.resize((bw//8, bh//8), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        imgs.append(img)
        pieces_id.update({(i,j): (img , board_canvas.create_image(i*bw/8, j*bh/8, image=img, anchor="nw"))})
    
for i in range(8):
    for j in range(8):
        if not (i+j)%2:
            board_canvas.create_rectangle(i*bw/8, j*bw/8, (i+1)*bw/8, (j+1)*bh/8, fill="#f3d69e", outline="black")
        else:
            board_canvas.create_rectangle(i*bw/8, j*bw/8, (i+1)*bw/8, (j+1)*bh/8, fill="#af481b", outline="black")

        draw_piece(b, i, j)

selected_piece = []
moveType = c_int * 4

# Make Line Visualizer
lines_canvas = tk.Canvas(root, name="lines", width=rw-bw, height=rh, bg = "grey60")
lines_canvas.pack(side="right", fill="y")

# Make Comment Box
comment_canvas = tk.Canvas(lines_canvas, name="comment", width=rw-bw, height=rh/4, bg="black")
comment_canvas.pack(side="bottom", fill="y")

comment_box = tk.Text(comment_canvas, name="comment_box", width=rw-bw, height=rh/5, fg="white", bg="black")
comment_label = tk.Label(comment_canvas, name='comment_label', width=(rw-bw)//16*3//4, text="Comment:", fg="blue", bg="red", font=("Arial", 16, "bold"), anchor="w")
comment_canvas.create_window(0, 0, height=rh/20, window=comment_label, anchor="nw")
comment_canvas.create_window(0, rh/20, height=rh/5, window=comment_box, anchor="nw")

# Make Move Logic
def commentCallback(buf):
    comment = simpledialog.askstring("Comment", "Add a Comment:", parent = root)
    if comment is None:
        comment = ""
    else:
        comment = comment.encode()
    for i, b in enumerate(comment):
        buf[i] = b
    buf[len(comment)] = 0

def promotionCallback(buf):
    piece = simpledialog.askstring("Promotion", "Q/R/N/B:", parent = root)
    if piece is None:
        piece = ""
    else:
        buf.contents.value = piece[0].encode()


curr_line = 0
def getLines(max_depth):
    lines: str = treelib.deepLines(b, max_depth, 0, db).decode()
    lines = lines.rpartition('\n')[0]
    return (lines_canvas.create_text(0, 0, text=lines, fill="black", font=("arial", 16, "bold"), anchor="nw"))
curr_line = getLines(3)


line = simpledialog.askstring("Line", "What's the name of the Line: ", parent = root)
while line is None:
    line = simpledialog.askstring("Line", "What's the name of the Line: ", parent = root)
line = line.encode()
cb = CommentCb(commentCallback)
pb = PromotionCb(promotionCallback)

def on_click(event):
    global selected_piece, b, curr_line
    col = event.x//(bw//8)
    row = event.y//(bh//8)
    piece = chr(b.state[8*row+col])
    if not selected_piece:
        if piece != ' ':
            selected_piece = [row, col]
    else:
        new_pos = [row,col]
        selected_piece.extend([row, col])
        n = treelib.getMove(b, moveType(*selected_piece), line, cb, pb)
        if n.state != b.state:
            _, id = pieces_id.pop((selected_piece[1], selected_piece[0]))
            board_canvas.delete(id)
            if piece != ' ':
                delpiecelc = (selected_piece[3], selected_piece[2])
                _, nid = pieces_id.pop(delpiecelc)
                board_canvas.delete(nid)
            elif chr(b.state[selected_piece[0]*8 + selected_piece[1]]).lower() == 'p' and row != selected_piece[0] and col != selected_piece[1]:
                delpiecelc = (selected_piece[1] + (col-selected_piece[1]), selected_piece[0])
                _, nid = pieces_id.pop(delpiecelc)
                board_canvas.delete(nid)

            draw_piece(n, col, row)
            selected_piece = []
            b=n
            lines_canvas.delete(curr_line)
            curr_line = getLines(3)

        else:
            print("Failed to move")
            selected_piece.pop()
            selected_piece.pop()
            selected_piece.pop()
            selected_piece.pop()

    return (col, row)

board_canvas.bind("<Button-1>", on_click)

root.mainloop()
