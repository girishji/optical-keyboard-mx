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
import collections


DIM = 19.0 * pcbnew.IU_PER_MM
RADIUS = 2.0 * pcbnew.IU_PER_MM
BORDER = 5.5 * pcbnew.IU_PER_MM


def add_line(start, end, layer=pcbnew.Edge_Cuts):
    board = pcbnew.GetBoard()
    ls = pcbnew.PCB_SHAPE(board)
    ls.SetShape(pcbnew.SHAPE_T_SEGMENT)
    ls.SetStart(start)
    ls.SetEnd(end)
    ls.SetLayer(layer)
    ls.SetWidth(int(0.15 * pcbnew.IU_PER_MM))
    board.Add(ls)


def add_line_arc(start, center, angle=-90, reverse=False, layer=pcbnew.Edge_Cuts):
    board = pcbnew.GetBoard()
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetStart(start)
    arc.SetCenter(center)
    if reverse:
        arc.SetArcAngleAndEnd(-angle * 10, False)
    else:
        arc.SetArcAngleAndEnd(angle * 10, True)
    arc.SetLayer(layer)
    arc.SetWidth(int(0.15 * pcbnew.IU_PER_MM))
    board.Add(arc)


def add_line_arc_from(
    start,
    dir,
    angle=-90,
    reverse=False,
    d=RADIUS, 
    layer=pcbnew.Edge_Cuts,
):
    Point = collections.namedtuple("Point", ["x", "y"])
    ctr = {"n": Point(0, -1), "e": Point(-1, 0), "s": Point(0, 1), "w": Point(0, 1)}
    center = pcbnew.wxPoint(start.x + d * ctr[dir].x, start.y + d * ctr[dir].y)
    add_line_arc(start, center, angle, reverse, layer)
    end = {"n": Point(0, -1), "e": Point(-1, 0), "s": Point(0, 1), "w": Point(0, 1)}


def remove_drawings():
    board = pcbnew.GetBoard()
    for t in board.GetDrawings():
        board.Delete(t)


def draw_border():
    dim = DIM
    brd = BORDER
    rad = RADIUS

    board = pcbnew.GetBoard()
    switches = [board.FindFootprintByReference("S1")]  # dummy
    for i in range(1, 75):
        switches.append(board.FindFootprintByReference("S" + str(i)))

    topl = switches[1].GetPosition()
    topr = switches[15].GetPosition()
    tl = pcbnew.wxPoint(topl.x - dim / 2 - brd + rad, topl.y - dim / 2 - brd)
    tr = pcbnew.wxPoint(topr.x + dim / 2 + brd - rad, topr.y - dim / 2 - brd)
    add_line(tl, tr)
    add_line_arc(tl, pcbnew.wxPoint(tl.x, tl.y + rad))
    sta = pcbnew.wxPoint(tl.x - rad, tl.y + rad)
    end = pcbnew.wxPoint(tl.x - rad, tl.y + 2 * dim - rad + brd)
    add_line(sta, end)

    left = switches[60].GetPosition()
    right = switches[74].GetPosition()
    pcbnew.Refresh()


remove_drawings()
draw_border()
