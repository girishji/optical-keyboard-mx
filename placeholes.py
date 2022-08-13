# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# Console script to place mouting holes
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/6.0/scripting/plugins
#   Run from python console using 'import filename'
#   To reapply:
#     import importlib
#     importlib.reload(filename)
#  OR
#    exec(open("path-to-script-file").read())

import pcbnew

DIM = 19.0
# BORDER = 2.1
BORDER = 0.0


def add_holes():
    dim = DIM
    delta = 0.5
    border = BORDER
    board = pcbnew.GetBoard()
    holes = [board.FindFootprintByReference("H1")]  # dummy
    holes += [board.FindFootprintByReference("H" + str(num)) for num in range(1, 21)]

    def set_position(num, x, y):
        holes[num].SetPosition(pcbnew.wxPointMM(x, y))

    set_position(1, dim * 0.5, -dim * 0.5 - border)
    set_position(2, dim * 5.5, -dim * 0.5 - border)
    set_position(3, dim * 10.5, -dim * 0.5 - border)
    set_position(4, dim * 15.5, -dim * 0.5 - border)
    set_position(5, dim * 3, dim * 0.5 + delta)
    set_position(6, dim * 8, dim * 0.5 + delta)
    set_position(7, dim * 13, dim * 0.5 + delta)
    set_position(8, dim * 0.5, dim * 1.25 + delta)
    set_position(9, dim * 3.75, dim * 2.5 + delta)
    set_position(10, dim * 7.75, dim * 2.5 + delta)
    set_position(11, dim * 11.75, dim * 2.5 + delta)
    set_position(12, dim * 16.0, dim * 2.5 + delta)
    set_position(13, -dim * 0.3, dim * 4.5 + border)
    set_position(14, dim * 2.25, dim * 4.5 + border)
    set_position(15, dim * 7.25, dim * 4.5 + border)
    set_position(16, dim * 12.0, dim * 4.5 + border)
    set_position(17, dim * 16.0, dim * 4.5 + border)

    pcbnew.Refresh()


add_holes()
