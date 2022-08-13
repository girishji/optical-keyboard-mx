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
from pcbnew import wxPoint
import math


DIM = 19.0 * pcbnew.IU_PER_MM
# RADIUS = 2.0 * pcbnew.IU_PER_MM
RADIUS = 3.0 * pcbnew.IU_PER_MM
# BORDER = 5.5 * pcbnew.IU_PER_MM
BORDER = 4.0 * pcbnew.IU_PER_MM

WR = {"offset": 64 * pcbnew.IU_PER_MM, "depth": 87 * pcbnew.IU_PER_MM}


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
    arc.SetArcAngleAndEnd(-angle * 10, reverse)
    arc.SetLayer(layer)
    arc.SetWidth(int(0.15 * pcbnew.IU_PER_MM))
    board.Add(arc)


def centerpt(start, quadrant, d=RADIUS):
    ctr = {
        1: wxPoint(start.x + d, start.y),
        2: wxPoint(start.x, start.y + d),
        3: wxPoint(start.x - d, start.y),
        4: wxPoint(start.x, start.y - d),
    }
    return ctr[quadrant]


def endpt(start, quadrant, d=RADIUS):
    end = {
        1: wxPoint(start.x + d, start.y + d),
        2: wxPoint(start.x - d, start.y + d),
        3: wxPoint(start.x + d, start.y - d),
        4: wxPoint(start.x - d, start.y - d),
    }
    return end[quadrant]


def transform(pt, around, theta):
    matrix = [
        [math.cos(math.radians(theta)), -math.sin(math.radians(theta))],
        [math.sin(math.radians(theta)), math.cos(math.radians(theta))],
    ]
    return wxPoint(
        around.x + pt.x * matrix[0][0] + pt.y * matrix[0][1],
        around.y + pt.x * matrix[1][0] + pt.y * matrix[1][1],
    )


def remove_drawings():
    board = pcbnew.GetBoard()
    for t in board.GetDrawings():
        board.Delete(t)


def draw_border_tilted_keys():
    dim = DIM
    brd = BORDER
    rad = RADIUS
    board = pcbnew.GetBoard()
    switches = [board.FindFootprintByReference("S1")]  # dummy
    for i in range(1, 75):
        switches.append(board.FindFootprintByReference("S" + str(i)))

    lth = switches[65].GetPosition()
    deg = 90 - switches[65].GetOrientation() // 10
    lsta = wxPoint(-dim / 2 - brd + rad, dim / 2 + dim / 8 + brd)
    lend = wxPoint(dim / 2 + brd - rad, dim / 2 + dim / 8 + brd)
    sta = transform(lsta, lth, deg)
    end = transform(lend, lth, deg)
    add_line(sta, end)
    ctr = transform(wxPoint(lsta.x, lsta.y - rad), lth, deg)
    add_line_arc(sta, ctr)
    end1 = transform(wxPoint(lsta.x - rad, lsta.y - rad), lth, deg)
    lend2 = wxPoint(lsta.x - rad, lsta.y - dim / 2 + 2.8 * pcbnew.IU_PER_MM)
    end2 = transform(lend2, lth, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x - rad, lend2.y), lth, deg)
    add_line_arc(end2, ctr, reverse=True, angle=90 + deg)
    ctr = transform(wxPoint(lend.x, lend.y - rad), lth, deg)
    add_line_arc(end, ctr, reverse=True, angle=90)
    lend1 = wxPoint(lend.x + rad, lend.y - rad)
    end1 = transform(lend1, lth, deg)
    lend2 = wxPoint(lend1.x, lend1.y - dim + 4 * pcbnew.IU_PER_MM)
    end2 = transform(lend2, lth, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x + rad, lend2.y), lth, deg)
    add_line_arc(end2, ctr, reverse=False, angle=-90 + deg)

    rth = switches[67].GetPosition()
    deg = 90 - switches[67].GetOrientation() // 10
    lend = wxPoint(-dim / 2 - brd + rad, dim / 2 + dim / 8 + brd)
    lsta = wxPoint(dim / 2 + brd - rad, dim / 2 + dim / 8 + brd)
    sta = transform(lsta, rth, deg)
    end = transform(lend, rth, deg)
    add_line(sta, end)
    ctr = transform(wxPoint(lsta.x, lsta.y - rad), rth, deg)
    add_line_arc(sta, ctr, reverse=True, angle=90)
    end1 = transform(wxPoint(lsta.x + rad, lsta.y - rad), rth, deg)
    lend2 = wxPoint(lsta.x + rad, lsta.y - dim / 2 + 2.8 * pcbnew.IU_PER_MM)
    end2 = transform(lend2, rth, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x + rad, lend2.y), rth, deg)
    add_line_arc(end2, ctr, reverse=False, angle=-90 + deg)
    ctr = transform(wxPoint(lend.x, lend.y - rad), rth, deg)
    add_line_arc(end, ctr, reverse=False, angle=-90)
    lend1 = wxPoint(lend.x - rad, lend.y - rad)
    end1 = transform(lend1, rth, deg)
    lend2 = wxPoint(lend1.x, lend1.y - dim + 4 * pcbnew.IU_PER_MM)
    end2 = transform(lend2, rth, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x - rad, lend2.y), rth, deg)
    add_line_arc(end2, ctr, reverse=True, angle=90 + deg)


def draw_border():
    dim = DIM
    brd = BORDER
    rad = RADIUS
    blackpill_wid = (21.0 + 0.5) * pcbnew.IU_PER_MM

    draw_border_tilted_keys()

    board = pcbnew.GetBoard()
    switches = [board.FindFootprintByReference("S1")]  # dummy
    for i in range(1, 75):
        switches.append(board.FindFootprintByReference("S" + str(i)))

    # topl = switches[1].GetPosition()
    left = switches[30].GetPosition()
    topr = switches[15].GetPosition()
    tl = wxPoint(left.x - dim / 2 + rad, topr.y - dim / 2 - brd)
    tr = wxPoint(topr.x + dim / 2 + brd - rad, topr.y - dim / 2 - brd)
    add_line(tl, tr)
    add_line_arc(tl, centerpt(tl, 2), reverse=True, angle=90)
    end = wxPoint(tl.x - rad, tl.y + 2 * dim - rad + brd)
    add_line(endpt(tl, 2), end)

    add_line_arc(end, centerpt(end, 3))
    sta = endpt(end, 2)
    blackpill = board.FindFootprintByReference("U1")
    bl = switches[60].GetPosition()
    ctr = switches[66].GetPosition()
    wr_width = -1
    if blackpill:
        end = wxPoint(sta.x + rad - blackpill_wid, sta.y)
        add_line(sta, end)
        bl = switches[60].GetPosition()
        end1 = wxPoint(end.x, bl.y + dim / 2 + WR["depth"] - rad)
        add_line(end, end1)
        add_line_arc(end1, centerpt(end1, 1), reverse=True, angle=90)
        end2 = endpt(end1, 1)
        end3 = wxPoint(ctr.x - WR["offset"] - rad, end2.y)
        wr_width = end3.x - end2.x
        add_line(end2, end3)
        add_line_arc(end3, centerpt(end3, 4), reverse=True, angle=90)
        end4 = endpt(end3, 3)
        end5 = wxPoint(end4.x, ctr.y + dim / 2 + brd + rad)
        add_line(end4, end5)
        add_line_arc(end5, centerpt(end5, 1))
    else:
        end = wxPoint(sta.x, bl.y + dim / 2 + brd - rad)
        add_line(sta, end)
        add_line_arc(end, centerpt(end, 1), reverse=True, angle=90)
        end5 = endpt(end, 1)

    ctr = switches[66].GetPosition()
    if blackpill:
        sta = wxPoint(ctr.x + WR["offset"] - rad, ctr.y + dim / 2 + brd)
        add_line_arc(sta, centerpt(sta, 2), reverse=False, angle=-90)
        end = endpt(sta, 1)
        end1 = wxPoint(end.x, end.y + WR["depth"] - brd - 2 * rad)
        add_line(end, end1)
        add_line_arc(end1, centerpt(end1, 1), reverse=True, angle=90)
        end2 = endpt(end1, 1)
        end3 = wxPoint(end2.x + wr_width, end2.y)
        add_line(end2, end3)
        add_line_arc(end3, centerpt(end3, 4), reverse=True, angle=90)
        end4 = endpt(end3, 3)
        end5 = wxPoint(end4.x, sta.y + rad)
        add_line(end4, end5)
        add_line_arc(end5, centerpt(end5, 1), reverse=False, angle=-90)
        end6 = endpt(end5, 3)
    else:
        end6 = ctr

    redge = switches[74].GetPosition()
    end7 = wxPoint(redge.x + dim / 2 + brd - rad, end6.y)
    add_line(end6, end7)
    add_line_arc(end7, centerpt(end7, 4), reverse=True, angle=+90)
    sta = endpt(end7, 3)
    tsw = switches[59].GetPosition()
    end = wxPoint(sta.x, tsw.y - dim / 2 - brd + rad)
    add_line(sta, end)
    add_line_arc(end, centerpt(end, 3), reverse=True, angle=+90)
    end1 = endpt(end, 4)
    tsw = switches[44].GetPosition()
    end2 = wxPoint(tsw.x + dim / 2 + brd + rad, end1.y)
    add_line(end1, end2)
    add_line_arc(end2, centerpt(end2, 4), reverse=False, angle=-90)
    end3 = endpt(end2, 4)
    tsw = switches[15].GetPosition()
    end4 = wxPoint(end3.x, tsw.y - dim / 2 - brd + rad)
    add_line(end3, end4)
    add_line_arc(end4, centerpt(end4, 3), reverse=True, angle=90)

    pcbnew.Refresh()


remove_drawings()
draw_border()
