from build123d import *
from pcbkit import Board, Enclosure, fdm
from pcbkit.shapes import prism, box
board = Board.load()
p = fdm()
enc = Enclosure(board, p)
W, H, T = board.width, board.height, board.thickness
margin = 6.0
floor = 2.4
board.set_height("U2", 1.0)
board.set_height("U3", 1.0)
board.set_height("U5", 1.0)
outer = prism(board.sketch(margin), -T-8.0, -1.7)
inner = prism(board.sketch(1.0), -T-8.0+floor, -1.69)
tray = outer - inner
# Four integrated support posts rise from the tray floor to the PCB back.
post_z0, post_z1 = -T-8.0+floor, -T
posts = [
    box(2.0, 5.0, 2.0, 5.0, post_z0, post_z1),
    box(W-5.0, W-2.0, 2.0, 5.0, post_z0, post_z1),
    box(2.0, 5.0, H-5.0, H-2.0, post_z0, post_z1),
    box(W-5.0, W-2.0, H-5.0, H-2.0, post_z0, post_z1),
]
for post in posts:
    tray += post
enc.part("lower_tray", tray, up=(0,0,-1))
cover_outer = prism(board.sketch(margin), 9.5, 12.0)
cover_inner = prism(board.sketch(2.0), 9.4, 12.1)
cover = cover_outer - cover_inner
enc.part("top_frame_placeholder", cover, up=(0,0,-1))
enc.step("Place the lower tray on the table.", "lower_tray")
enc.step("Seat the PCB on the perimeter support ledges.", "board")
enc.step("Fit the provisional top frame. The display window is not finalized.", "top_frame_placeholder")
enc.build()
