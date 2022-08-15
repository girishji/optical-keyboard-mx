# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# Console script to place footprints
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
from pcbnew import wxPoint, wxPointMM
import math
import itertools

BORDER = 4.0 * pcbnew.IU_PER_MM


class Switch:
    # S, D, Q, RL
    _pos = {
        "S": (0, 0),
        "D": (-3.4, 0),
        "Q": (3.4, 0),
        "RL": (8.3, 3.5),
        "M": (0, -5.1),
    }

    _radius = 1.5 * 1e6

    def __init__(self, board, num) -> None:
        if not board and not num:
            return  # dummy
        self.footprints = {
            "S": board.FindFootprintByReference("S" + str(num)),
            "D": board.FindFootprintByReference("D" + str(num)),
            "Q": board.FindFootprintByReference("Q" + str(num)),
            "RL": board.FindFootprintByReference("RL" + str(num)),
            "M": board.FindFootprintByReference("M" + str(num)),
        }
        self.orient()

    def orient(self):
        orientation = {"S": 0, "D": -90, "Q": 90, "RL": -90, "M": 0}
        for sym, fp in self.footprints.items():
            if fp:
                fp.SetOrientation(orientation[sym] * 10)

    def get_pad_center(self, fp, pad_num):
        return self.footprints[fp].FindPadByNumber(str(pad_num)).GetCenter()

    def add_tracks(self):
        sta = self.get_pad_center("D", 2)
        end = self.get_pad_center("RL", 2)
        ref = self.footprints["S"].GetPosition()
        theta = -1 * self.footprints["S"].GetOrientation() // 10
        sta1 = transform(wxPoint(sta.x - ref.x, sta.y - ref.y), ref, -theta)
        end1 = transform(wxPoint(end.x - ref.x, end.y - ref.y), ref, -theta)
        r = end1.y - sta1.y
        ctr = wxPoint(sta1.x + r, sta1.y)
        mid = wxPoint(ctr.x - r / math.sqrt(2), ctr.y + r / math.sqrt(2))
        end2 = wxPoint(sta1.x + r, sta1.y + r)
        end3 = transform(wxPoint(end2.x - ref.x, end2.y - ref.y), ref, theta)
        add_arc(sta, end3, mid)
        add_track(end3, end)

    def place(self, offset):
        for fp in self._pos.keys():
            if self.footprints[fp]:
                p = wxPointMM(
                    Switch._pos[fp][0] + offset[0], Switch._pos[fp][1] + offset[1]
                )
                self.footprints[fp].SetPosition(p)

    def rotate(self, deg):
        p = self.footprints["S"].GetPosition()
        for _, fp in self.footprints.items():
            if fp:
                fp.Rotate(p, deg * 10)


class Keyboard(object):
    def __init__(self) -> None:
        self.switches = [Switch(None, None)]
        board = pcbnew.GetBoard()
        for i in range(1, 75):
            self.switches.append(Switch(board, i))
        self.DIM = 19
        self.RP = [
            board.FindFootprintByReference("RP" + str(fp))
            for fp in [1] + list(range(1, 6))
        ]

    def place_footprints(self):
        dim = self.DIM
        board = pcbnew.GetBoard()
        rp_pos = (8.3, -0.5)

        # row 1
        for i in range(1, 16):
            self.switches[i].place((i * dim, 0))
        place_fp((4 * dim, 0), self.RP[1], rp_pos, 90)

        # row 2
        offs = dim + dim / 4
        self.switches[16].place((offs, dim))
        for i in range(17, 29):
            self.switches[i].place((offs + dim / 4 + (i - 16) * dim, dim))
        self.switches[29].place((offs + dim / 4 + dim * 13 + dim / 4, dim))
        place_fp((offs + dim / 4 + 3 * dim, dim), self.RP[2], rp_pos, 90)

        # row 3
        self.switches[30].place((dim / 2 + dim / 4, 2 * dim))
        self.switches[31].place((3 * dim / 2 + dim / 4, 2 * dim))
        offs = 3 * dim / 2 + dim / 4
        for i in range(32, 43):
            self.switches[i].place((offs + (i - 31) * dim, 2 * dim))
        place_fp((offs + 2 * dim, 2 * dim), self.RP[3], rp_pos, 90)
        offs += 12 * dim + dim / 8
        self.switches[43].place((offs, 2 * dim))
        self.switches[44].place((offs + dim + dim / 8, 2 * dim))

        # row 4
        offs = dim * (0.5 + 0.75 / 2)
        self.switches[45].place((offs + dim / 8, 3 * dim))
        offs += dim + dim * 0.75 / 2
        for i in range(46, 57):
            self.switches[i].place((offs + (i - 46) * dim, 3 * dim))
        place_fp((offs + 2 * dim, 3 * dim), self.RP[4], rp_pos, 90)
        offs += dim * 11
        self.switches[57].place((offs + dim / 8, 3 * dim))
        offs += dim * 1.25
        self.switches[58].place((offs, 3 * dim))
        self.switches[59].place((offs + dim, 3 * dim))

        # row 5
        for i in range(60, 63):
            self.switches[i].place((dim / 2 + (i - 60) * dim + dim / 4, 4 * dim))
        offs = dim / 2 + dim * 3
        self.switches[63].place((offs + dim / 4, 4 * dim))
        place_fp((offs + dim / 4, 4 * dim), self.RP[5], rp_pos, 90)

        # self.switches[64].place((offs + dim * 1.25 + dim / 8, 4 * dim))
        self.switches[64].place((offs + dim * 1.25 + dim / 8 + 1.4, 4 * dim + 5))
        self.switches[64].rotate(-16)
        offs += dim * 1.25 * 2
        # self.switches[65].place((offs - 1.5, 4.5 * dim + 4))
        self.switches[65].place((offs - 1.0, 4.5 * dim + 7))
        # self.switches[66].rotate(-15 + 90)
        self.switches[65].rotate(-20 + 90)

        offs += dim * 1.25
        self.switches[66].place((offs, 4 * dim))

        # self.switches[67].place((offs + dim + dim / 4 + 1.5, 4.5 * dim + 4))
        self.switches[67].place((offs + dim + dim / 4 + 1.0, 4.5 * dim + 7))
        self.switches[67].rotate(20 + 90)
        offs += dim * 1.25
        # self.switches[68].place((offs + dim, 4 * dim))
        self.switches[68].place((offs + dim - 1.4, 4 * dim + 5))
        self.switches[68].rotate(16)
        offs += dim

        for i in range(69, 75):
            self.switches[i].place((offs + (i - 68) * dim, 4 * dim))

        bp = board.FindFootprintByReference("U1")
        if bp:
            bp.SetPosition(wxPointMM(-dim / 4 - 1.5, 3 * dim - 2.0))

        bp = board.FindFootprintByReference("U2")
        if bp:
            bp.SetOrientation(45 * 10)  # 1/10 of degree
            bp.SetPosition(wxPointMM(dim * 8, 4 * dim - 4.5))

            fp = board.FindFootprintByReference("R1")
            fp.SetOrientation(90 * 10)  # 1/10 of degree
            fp.SetPosition(wxPointMM(dim * 6 + 7, 4 * dim - 5))
            for i in range(2, 5):
                fp = board.FindFootprintByReference("R" + str(i))
                fp.SetOrientation(90 * 10)  # 1/10 of degree
                fp.SetPosition(wxPointMM(dim * 8 + 17, 5 * dim - 10 - i * 4))

            for i in range(4, 6):
                fp = board.FindFootprintByReference("C" + str(i))
                fp.SetOrientation(0 * 10)  # 1/10 of degree
                fp.SetPosition(wxPointMM(dim * 8 + 12, 5 * dim - i * 5))

            for i, fpi in enumerate(["C3", "R5", "R6"]):
                fp = board.FindFootprintByReference(fpi)
                fp.SetOrientation(0 * 10)  # 1/10 of degree
                fp.SetPosition(wxPointMM(dim * 8 - 2 + i * 4, 4 * dim + 3))

            for i in range(1, 3):
                fp = board.FindFootprintByReference("C" + str(i))
                fp.SetOrientation(90 * 10)  # 1/10 of degree
                fp.SetPosition(wxPointMM(dim * 6 - 8 + i * 6, 4 * dim))

        pcbnew.Refresh()

    def remove_tracks(self):
        # delete tracks and vias
        board = pcbnew.GetBoard()
        tracks = board.GetTracks()
        for t in tracks:
            board.Delete(t)

    def add_via(self, loc):
        board = pcbnew.GetBoard()
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(loc)
        via.SetDrill(int(0.3 * 1e6))
        via.SetWidth(int(0.6 * 1e6))
        board.Add(via)

    def via_track(self, point, offset=-0.9, reverse=False, vertical=False):
        offset = -offset if reverse else offset
        end = (
            wxPoint(point.x + offset * 1e6, point.y)
            if not vertical
            else wxPoint(point.x, point.y + offset * 1e6)
        )
        add_track(point, end)
        self.add_via(end)
        return end

    def add_tracks(self):

        # return if this is switch plate and not pcb
        if not self.switches[1].footprints["RL"]:
            return

        # add tracks
        for i in range(1, 75):
            self.switches[i].add_tracks()

        # rows
        for i in itertools.chain(
            range(1, 15),
            range(16, 29),
            range(30, 44),
            range(45, 59),
            range(60, 63),
            range(69, 74),
        ):

            sta = self.switches[i].get_pad_center("Q", 1)
            sta1 = add_arc_from(sta, 1, 0)
            end = self.switches[i + 1].get_pad_center("Q", 1)
            end1 = add_arc_from(end, 0, 0)
            add_track(sta1, end1)

            # LEDs
            corner = [8, 23, 37, 52]
            if i not in corner:
                start = self.switches[i].get_pad_center("M", 1)
                sta = wxPoint(start.x, start.y - 0.5 * 1e6)
                add_track(sta, start)
                end = add_arc_from(sta, True, False)

                start = self.switches[i + 1].get_pad_center("M", 1)
                sta = wxPoint(start.x, start.y - 0.5 * 1e6)
                if i + 1 in corner + [15, 29, 45, 60, 75]:
                    add_track(sta, start)
                end2 = add_arc_from(sta, False, False)
                add_track(end, end2)

        # columns
        def connect(sta, end, straight_end=False):
            if sta.x < end.x:
                end2 = add_arc_from(sta, 1, 1, layer=pcbnew.B_Cu)
                end3 = (
                    end if straight_end else add_arc_from(end, 0, 0, layer=pcbnew.B_Cu)
                )
            elif sta.x > end.x:
                end2 = add_arc_from(sta, 0, 1, layer=pcbnew.B_Cu)
                end3 = (
                    end if straight_end else add_arc_from(end, 1, 0, layer=pcbnew.B_Cu)
                )
            else:
                end2, end3 = sta, end
            add_track(end2, end3, pcbnew.B_Cu)

        exclude = [64, 65, 67, 68, -1]
        for i1, i2, i3, i4, i5 in list(
            zip(
                range(1, 16),
                range(16, 30),
                range(30, 45),
                range(45, 60),
                range(60, 75),
            )
        ) + [(-1, 15, 44, 59, 74)]:
            vias = {
                sw: self.via_track(self.switches[sw].get_pad_center("RL", 1))
                for sw in [i1, i2, i3, i4, i5]
                if sw not in exclude
            }
            drop = 5.5 * 1e6
            for st, en in [(i1, i2), (i2, i3), (i3, i4), (i4, i5)]:
                if st in exclude or en in exclude:
                    continue
                sta = vias[st]
                end = add_arc_from(sta, 0, 1, False, layer=pcbnew.B_Cu)
                end2 = wxPoint(
                    end.x, sta.y + (drop if st != 15 else drop + self.DIM * 1e6)
                )
                add_track(end, end2, pcbnew.B_Cu)
                sta = vias[en]
                end = add_arc_from(sta, 0, 0, False, layer=pcbnew.B_Cu)
                end3 = wxPoint(
                    end.x, end.y - self.DIM * 1e6 + drop + 3 * Switch._radius
                )
                add_track(end, end3, pcbnew.B_Cu)
                connect(end2, end3)

        # RPs
        vias = {}
        for rp in range(1, 6):
            start = self.RP[rp].FindPadByNumber(str(1)).GetCenter()
            vias[rp] = self.via_track(start, offset=0.9)
        for st, en in [(s, s + 1) for s in range(1, 5)]:
            sta = vias[st]
            drop = 7.0 * 1e6 if st in (1, 3) else 8.5 * 1e6
            end = add_arc_from(sta, True, True, False, layer=pcbnew.B_Cu)
            end2 = wxPoint(end.x, sta.y + drop)
            add_track(end, end2, pcbnew.B_Cu)
            sta = vias[en]
            end = add_arc_from(sta, 1, 0, False, layer=pcbnew.B_Cu)
            end3 = wxPoint(end.x, end.y - self.DIM * 1e6 + drop + 3 * Switch._radius)
            add_track(end, end3, pcbnew.B_Cu)
            connect(end2, end3)

        # LED matrix
        for st, en in zip(range(2, 16), range(17, 30)):
            vst = self.via_track(self.switches[st].get_pad_center("M", 2), offset=3)
            end1 = add_arc_from(vst, 1, 1, False, layer=pcbnew.B_Cu)
            if st == 9:
                ven = self.via_track(self.switches[en].get_pad_center("M", 1))
                end3 = wxPoint(end1.x, ven.y - Switch._radius)
                add_track(end1, end3, pcbnew.B_Cu)
                connect(end3, ven, True)
            else:
                ven = self.via_track(
                    self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
                )
                end3 = wxPoint(end1.x, ven.y - 2 * Switch._radius)
                add_track(end1, end3, pcbnew.B_Cu)
                connect(end3, ven)

        for st, en in list(zip(range(18, 25), range(32, 39))) + list(
            zip(range(26, 30), range(40, 44))
        ):
            if st == 20:
                continue
            vst = self.via_track(
                self.switches[st].get_pad_center("M", 2), vertical=True, offset=1.2
            )
            end1 = add_arc_from(vst, 0, 1, layer=pcbnew.B_Cu)
            ven = self.via_track(
                self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
            )
            end2 = add_arc_from(ven, 1, 0, layer=pcbnew.B_Cu)
            end3 = wxPoint(end2.x + 1 * 1e6, end2.y)
            add_track(end2, end3, pcbnew.B_Cu)
            end4 = add_arc_from(end3, 1, 0, False, layer=pcbnew.B_Cu)
            end5 = wxPoint(end4.x, end1.y + Switch._radius)
            add_track(end4, end5, pcbnew.B_Cu)
            end6 = add_arc_from(end5, 1, 0, layer=pcbnew.B_Cu)
            add_track(end6, end1, pcbnew.B_Cu)

        for st, en in zip(range(30, 45), range(45, 60)):
            if st in (32, 40):
                continue
            vst = self.via_track(self.switches[st].get_pad_center("M", 2), offset=2.5)
            end1 = add_arc_from(vst, 1, 1, False, layer=pcbnew.B_Cu)
            ven = self.via_track(
                self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
            )
            if st == 30:
                end2 = wxPoint(ven.x, ven.y - Switch._radius)
            else:
                end2 = add_arc_from(ven, 0, 0, layer=pcbnew.B_Cu)
            end3 = wxPoint(end1.x, end2.y - Switch._radius)
            add_track(end1, end3, pcbnew.B_Cu)
            if st == 30:
                add_track(ven, end3, pcbnew.B_Cu)
            else:
                connect(end3, end2, True)

        for st, en in zip(range(45, 50), range(60, 65)):
            if st == 48:
                continue
            vst = self.via_track(
                self.switches[st].get_pad_center("M", 2), vertical=True, offset=1.2
            )
            end1 = add_arc_from(vst, 0, 1, layer=pcbnew.B_Cu)
            ven = self.via_track(
                self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
            )
            end2 = wxPoint(ven.x, end1.y + Switch._radius)
            add_track(ven, end2, pcbnew.B_Cu)
            end3 = add_arc_from(end2, 1, 0, layer=pcbnew.B_Cu)
            add_track(end3, end1, pcbnew.B_Cu)

        for st, en in zip(range(53, 60), range(68, 75)):
            if st == 56:
                continue
            vst = self.via_track(
                self.switches[st].get_pad_center("M", 2), vertical=True, offset=1.2
            )
            end1 = add_arc_from(vst, 0, 1, layer=pcbnew.B_Cu)
            ven = self.via_track(
                self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
            )
            end2 = add_arc_from(ven, 0, 0, layer=pcbnew.B_Cu)
            end3 = wxPoint(end1.x - 3 * 1e6, end1.y)
            add_track(end1, end3, pcbnew.B_Cu)
            end4 = add_arc_from(end3, 0, 1, False, layer=pcbnew.B_Cu)
            end5 = wxPoint(end4.x, end2.y - Switch._radius)
            add_track(end4, end5, pcbnew.B_Cu)
            end6 = add_arc_from(end5, 1, 1, layer=pcbnew.B_Cu)
            add_track(end6, end2, pcbnew.B_Cu)

        # ground
        for i in range(1, 75):
            self.via_track(self.switches[i].get_pad_center("Q", 2), offset=-1.2)
            self.via_track(self.switches[i].get_pad_center("D", 1), offset=1.2)

        pcbnew.Refresh()

    def place_conn(self):
        board = pcbnew.GetBoard()
        ofx, ofy, leng = 7 * 1e6, -2 * 1e6, 2.54 * 3 * 1e6

        def around_hole(n, hnum, above=True, fp="H", vertical=False):
            hl = board.FindFootprintByReference(fp + str(hnum)).GetPosition()
            offx, offy = ofx + (2 * 1e6 if fp == "HS" else 0), ofy + (
                2 * 1e6 if fp == "HS" else 0
            )
            offy = offy if above else -offy
            if n[0]:
                if vertical:
                    fps[n[0]].SetOrientation(0 * 10)  # 1/10 of degree
                    fps[n[0]].SetPosition(wxPoint(hl.x - offy, hl.y - offx - 3 * leng))
                else:
                    fps[n[0]].SetPosition(wxPoint(hl.x - offx - leng, hl.y + offy))
            if n[1]:
                if vertical:
                    fps[n[1]].SetOrientation(0 * 10)  # 1/10 of degree
                    fps[n[1]].SetPosition(wxPoint(hl.x - offy, hl.y + offx + leng))
                else:
                    fps[n[1]].SetPosition(wxPoint(hl.x + offx, hl.y + offy))

        fps = {}
        for i in range(37):
            fps[i] = board.FindFootprintByReference("J" + str(i))
            if fps[i]:
                fps[i].SetOrientation(90 * 10)  # 1/10 of degree
        around_hole([0, 1], 1)
        around_hole([2, 3], 2)
        around_hole([4, 5], 3)
        around_hole([6, 0], 4)
        around_hole([7, 0], 13, False)
        around_hole([0, 8], 14, False)
        around_hole([9, 10], 16, False)
        around_hole([11, 0], 17, False)

        around_hole([0, 12], 1, False, "HS")
        around_hole([13, 0], 2, False, "HS")
        around_hole([0, 14], 3, False, "HS")
        around_hole([15, 0], 4, False, "HS")
        around_hole([0, 16], 5, False, "HS")
        around_hole([17, 0], 6, False, "HS")
        around_hole([0, 18], 7, False, "HS")
        around_hole([19, 0], 8, False, "HS")

        around_hole([20, 0], 1, False, "HS", vertical=True)
        around_hole([21, 0], 2, False, "HS", vertical=True)
        around_hole([22, 0], 3, False, "HS", vertical=True)
        around_hole([23, 0], 4, False, "HS", vertical=True)

        around_hole([0, 24], 1, False, "H", vertical=True)
        around_hole([0, 25], 4, vertical=True)

        dim = self.DIM * 1e6
        hl = board.FindFootprintByReference("S18").GetPosition()
        fps[26].SetPosition(wxPoint(hl.x - 5 * 1e6, hl.y + dim / 2))
        hl = board.FindFootprintByReference("S22").GetPosition()
        fps[27].SetPosition(wxPoint(hl.x - 5 * 1e6, hl.y + dim / 2))
        hl = board.FindFootprintByReference("S27").GetPosition()
        fps[28].SetPosition(wxPoint(hl.x - 5 * 1e6, hl.y + dim / 2))

        sw = board.FindFootprintByReference("S65")
        hl = sw.GetPosition()
        theta = sw.GetOrientation() // 10
        fps[29].SetPosition(transform(wxPoint(-4 * 1e6, dim / 2 - ofy), hl, 90 - theta))
        fps[29].SetOrientation(theta * 10)
        sw = board.FindFootprintByReference("S67")
        hl = sw.GetPosition()
        theta = sw.GetOrientation() // 10
        fps[30].SetPosition(transform(wxPoint(-4 * 1e6, dim / 2 - ofy), hl, 90 - theta))
        fps[30].SetOrientation(theta * 10)

        pcbnew.Refresh()


def add_track(start, end, layer=pcbnew.F_Cu):
    board = pcbnew.GetBoard()
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetWidth(int(0.3 * 1e6))
    track.SetLayer(layer)
    board.Add(track)


def add_arc(start, end, mid, layer=pcbnew.F_Cu):
    board = pcbnew.GetBoard()
    track = pcbnew.PCB_ARC(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetMid(mid)
    track.SetWidth(int(0.3 * 1e6))
    track.SetLayer(layer)
    board.Add(track)


def add_arc_from(sta, xp, yp, reverse=True, d=Switch._radius, layer=pcbnew.F_Cu):
    dcos = d / math.sqrt(2)
    if xp and yp:
        end = wxPoint(sta.x + d, sta.y + d)
        mid = (
            wxPoint(sta.x + d - dcos, sta.y + dcos)
            if reverse
            else wxPoint(sta.x + dcos, sta.y + d - dcos)
        )
    elif xp and not yp:
        end = wxPoint(sta.x + d, sta.y - d)
        mid = (
            wxPoint(sta.x + d - dcos, sta.y - dcos)
            if reverse
            else wxPoint(sta.x + dcos, sta.y - d + dcos)
        )
    elif not xp and yp:
        end = wxPoint(sta.x - d, sta.y + d)
        mid = (
            wxPoint(sta.x - d + dcos, sta.y + dcos)
            if reverse
            else wxPoint(sta.x - dcos, sta.y + d - dcos)
        )
    else:
        end = wxPoint(sta.x - d, sta.y - d)
        mid = (
            wxPoint(sta.x - d + dcos, sta.y - dcos)
            if reverse
            else wxPoint(sta.x - dcos, sta.y - d + dcos)
        )
    add_arc(sta, end, mid, layer)
    return end


def place_fp(offset, fp, pos, orient):
    if fp:
        fp.SetOrientation(orient * 10)  # 1/10 of degree
        p = wxPointMM(pos[0] + offset[0], pos[1] + offset[1])
        fp.SetPosition(p)


def transform(pt, around, theta):
    matrix = [
        [math.cos(math.radians(theta)), -math.sin(math.radians(theta))],
        [math.sin(math.radians(theta)), math.cos(math.radians(theta))],
    ]
    return wxPoint(
        around.x + pt.x * matrix[0][0] + pt.y * matrix[0][1],
        around.y + pt.x * matrix[1][0] + pt.y * matrix[1][1],
    )


kb = Keyboard()
kb.place_footprints()
kb.remove_tracks()
kb.add_tracks()
# kb.place_conn()
