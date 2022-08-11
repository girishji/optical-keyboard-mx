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
import math
import itertools


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
        self.footprints["S"].SetOrientation(0)  # 1/10 of degree
        self.footprints["D"].SetOrientation(-90 * 10)  # 1/10 of degree
        self.footprints["Q"].SetOrientation(90 * 10)  # 1/10 of degree
        self.footprints["RL"].SetOrientation(-90 * 10)  # 1/10 of degree
        self.footprints["M"].SetOrientation(0 * 10)  # 1/10 of degree

    def get_pad_center(self, fp, pad_num):
        return self.footprints[fp].FindPadByNumber(str(pad_num)).GetCenter()

    def add_tracks(self):
        sta = self.get_pad_center("D", 2)
        end = self.get_pad_center("RL", 2)
        r = end.y - sta.y
        add_track(add_arc_from(sta, 1, 1, 1, 0, True, d=r), end)

    def place(self, offset):
        for fp in self._pos.keys():
            p = pcbnew.wxPointMM(
                Switch._pos[fp][0] + offset[0], Switch._pos[fp][1] + offset[1]
            )
            self.footprints[fp].SetPosition(p)

    def rotate(self, deg):
        p = self.footprints["S"].GetPosition()
        for _, fp in self.footprints.items():
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
        self.switches[64].place((offs + dim * 1.25 + dim / 8, 4 * dim))
        offs += dim * 1.25 * 2
        self.switches[65].place((offs - 1.5, 4.5 * dim + 4))
        # self.switches[66].rotate(-15 + 90)
        self.switches[65].rotate(-20 + 90)
        offs += dim * 1.25
        self.switches[66].place((offs, 4 * dim))
        self.switches[67].place((offs + dim + dim / 4 + 1.5, 4.5 * dim + 4))
        self.switches[67].rotate(20 + 90)
        offs += dim * 1.25
        for i in range(68, 75):
            self.switches[i].place((offs + (i - 67) * dim, 4 * dim))

        bp = board.FindFootprintByReference("U1")
        bp.SetOrientation(0 * 10)  # 1/10 of degree
        bp.SetPosition(pcbnew.wxPointMM(-6, 3 * dim - 1))

        bp = board.FindFootprintByReference("U2")
        bp.SetOrientation(45 * 10)  # 1/10 of degree
        bp.SetPosition(pcbnew.wxPointMM(dim * 8, 4 * dim - 4.5))

        for i in range(1, 5):
            fp = board.FindFootprintByReference("R" + str(i))
            fp.SetOrientation(90 * 10)  # 1/10 of degree
            fp.SetPosition(pcbnew.wxPointMM(dim * 8 + 17, 5 * dim - 10 - i * 4))

        for i in range(4, 6):
            fp = board.FindFootprintByReference("C" + str(i))
            fp.SetOrientation(0 * 10)  # 1/10 of degree
            fp.SetPosition(pcbnew.wxPointMM(dim * 8 + 12, 5 * dim - i * 5))

        for i, fpi in enumerate(["C3", "R5", "R6"]):
            fp = board.FindFootprintByReference(fpi)
            fp.SetOrientation(0 * 10)  # 1/10 of degree
            fp.SetPosition(pcbnew.wxPointMM(dim * 8 - 2 + i * 4, 4 * dim + 1))

        for i in range(1, 3):
            fp = board.FindFootprintByReference("C" + str(i))
            fp.SetOrientation(0 * 10)  # 1/10 of degree
            fp.SetPosition(pcbnew.wxPointMM(dim * 8 - 8 + i * 6, 4 * dim + 6))

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
            pcbnew.wxPoint(point.x + offset * 1e6, point.y)
            if not vertical
            else pcbnew.wxPoint(point.x, point.y + offset * 1e6)
        )
        add_track(point, end)
        self.add_via(end)
        return end

    def add_tracks(self):

        # add tracks
        for i in range(1, 75):
            if i not in [65, 67]:
                self.switches[i].add_tracks()

        for i in itertools.chain(
            range(1, 15),
            range(16, 29),
            range(30, 44),
            range(45, 59),
            range(60, 64),
            range(68, 74),
        ):

            sta = self.switches[i].get_pad_center("Q", 1)
            sta1 = add_arc_from(sta, 1, 0, 1, 1)
            end = self.switches[i + 1].get_pad_center("Q", 1)
            end1 = add_arc_from(end, 0, 0, 0, 1, True)
            add_track(sta1, end1)

            # LEDs
            corner = [8, 23, 37, 52]
            if i not in corner:
                start = self.switches[i].get_pad_center("M", 1)
                sta = pcbnew.wxPoint(start.x, start.y - 0.5 * 1e6)
                add_track(sta, start)
                end = add_arc_from(sta, True, False, True, True)

                start = self.switches[i + 1].get_pad_center("M", 1)
                sta = pcbnew.wxPoint(start.x, start.y - 0.5 * 1e6)
                if i + 1 in corner + [15, 29, 45, 60, 75]:
                    add_track(sta, start)
                end2 = add_arc_from(sta, False, False, False, True, True)
                add_track(end, end2)

        # columns
        def connect(sta, end, straight_end=False):
            if sta.x < end.x:
                end2 = add_arc_from(sta, 1, 1, 1, 0, True, layer=pcbnew.B_Cu)
                end3 = (
                    end
                    if straight_end
                    else add_arc_from(end, 0, 0, 0, 1, True, layer=pcbnew.B_Cu)
                )
            elif sta.x > end.x:
                end2 = add_arc_from(sta, 0, 1, 0, 0, layer=pcbnew.B_Cu)
                end3 = (
                    end
                    if straight_end
                    else add_arc_from(end, 1, 0, 1, 1, layer=pcbnew.B_Cu)
                )
            else:
                end2, end3 = sta, end
            add_track(end2, end3, pcbnew.B_Cu)

        exclude = [65, 67, -1]
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
                end = add_arc_from(sta, 0, 1, 1, 1, True, layer=pcbnew.B_Cu)
                end2 = pcbnew.wxPoint(
                    end.x, sta.y + (drop if st != 15 else drop + self.DIM * 1e6)
                )
                add_track(end, end2, pcbnew.B_Cu)
                sta = vias[en]
                end = add_arc_from(sta, 0, 0, 1, 0, layer=pcbnew.B_Cu)
                end3 = pcbnew.wxPoint(
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
            end = add_arc_from(sta, True, True, False, True, layer=pcbnew.B_Cu)
            end2 = pcbnew.wxPoint(end.x, sta.y + drop)
            add_track(end, end2, pcbnew.B_Cu)
            sta = vias[en]
            end = add_arc_from(sta, 1, 0, 0, 0, True, layer=pcbnew.B_Cu)
            end3 = pcbnew.wxPoint(
                end.x, end.y - self.DIM * 1e6 + drop + 3 * Switch._radius
            )
            add_track(end, end3, pcbnew.B_Cu)
            connect(end2, end3)

        # LED matrix
        for st, en in zip(range(2, 16), range(17, 30)):
            vst = self.via_track(self.switches[st].get_pad_center("M", 2), offset=3)
            end1 = add_arc_from(vst, 1, 1, 0, 1, layer=pcbnew.B_Cu)
            if st == 9:
                ven = self.via_track(self.switches[en].get_pad_center("M", 1))
                end3 = pcbnew.wxPoint(end1.x, ven.y - Switch._radius)
                add_track(end1, end3, pcbnew.B_Cu)
                connect(end3, ven, True)
            else:
                ven = self.via_track(
                    self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
                )
                end3 = pcbnew.wxPoint(end1.x, ven.y - 2 * Switch._radius)
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
            end1 = add_arc_from(vst, 0, 1, 0, 0, layer=pcbnew.B_Cu)
            ven = self.via_track(
                self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
            )
            end2 = add_arc_from(ven, 1, 0, 1, 1, layer=pcbnew.B_Cu)
            end3 = pcbnew.wxPoint(end2.x + 1 * 1e6, end2.y)
            add_track(end2, end3, pcbnew.B_Cu)
            end4 = add_arc_from(end3, 1, 0, 0, 0, True, layer=pcbnew.B_Cu)
            end5 = pcbnew.wxPoint(end4.x, end1.y + Switch._radius)
            add_track(end4, end5, pcbnew.B_Cu)
            end6 = add_arc_from(end5, 1, 0, 1, 1, layer=pcbnew.B_Cu)
            add_track(end6, end1, pcbnew.B_Cu)

        for st, en in zip(range(30, 45), range(45, 60)):
            if st in (32, 40):
                continue
            vst = self.via_track(self.switches[st].get_pad_center("M", 2), offset=2.5)
            end1 = add_arc_from(vst, 1, 1, 0, 1, layer=pcbnew.B_Cu)
            ven = self.via_track(
                self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
            )
            if st == 30:
                end2 = pcbnew.wxPoint(ven.x, ven.y - Switch._radius)
            else:
                end2 = add_arc_from(ven, 0, 0, 0, 1, True, layer=pcbnew.B_Cu)
            end3 = pcbnew.wxPoint(end1.x, end2.y - Switch._radius)
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
            end1 = add_arc_from(vst, 0, 1, 0, 0, layer=pcbnew.B_Cu)
            ven = self.via_track(
                self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
            )
            end2 = pcbnew.wxPoint(ven.x, end1.y + Switch._radius)
            add_track(ven, end2, pcbnew.B_Cu)
            end3 = add_arc_from(end2, 1, 0, 1, 1, layer=pcbnew.B_Cu)
            add_track(end3, end1, pcbnew.B_Cu)

        for st, en in zip(range(53, 60), range(68, 75)):
            if st == 56:
                continue
            vst = self.via_track(
                self.switches[st].get_pad_center("M", 2), vertical=True, offset=1.2
            )
            end1 = add_arc_from(vst, 0, 1, 0, 0, layer=pcbnew.B_Cu)
            ven = self.via_track(
                self.switches[en].get_pad_center("M", 2), vertical=True, offset=-1.2
            )
            end2 = add_arc_from(ven, 0, 0, 0, 1, True, layer=pcbnew.B_Cu)
            end3 = pcbnew.wxPoint(end1.x - 3 * 1e6, end1.y)
            add_track(end1, end3, pcbnew.B_Cu)
            end4 = add_arc_from(end3, 0, 1, 1, 1, True, layer=pcbnew.B_Cu)
            end5 = pcbnew.wxPoint(end4.x, end2.y - Switch._radius)
            add_track(end4, end5, pcbnew.B_Cu)
            end6 = add_arc_from(end5, 1, 1, 1, 0, True, layer=pcbnew.B_Cu)
            add_track(end6, end2, pcbnew.B_Cu)

        # ground
        for i in range(1, 75):
            self.via_track(self.switches[i].get_pad_center("Q", 2), offset=-1.2)
            self.via_track(self.switches[i].get_pad_center("D", 1), offset=1.2)

        pcbnew.Refresh()

    def add_holes(self):
        dim = self.DIM
        board = pcbnew.GetBoard()
        holes = [board.FindFootprintByReference("H1")]  # dummy
        holes += [
            board.FindFootprintByReference("H" + str(num)) for num in range(1, 21)
        ]
        holes[1].SetPosition(pcbnew.wxPointMM(dim * 3, dim * 0.5))
        holes[2].SetPosition(pcbnew.wxPointMM(dim * 4, dim * 1.5))
        holes[3].SetPosition(pcbnew.wxPointMM(dim * (1 + 1 / 8), dim * 2.0))
        holes[4].SetPosition(pcbnew.wxPointMM(dim * (1 / 4 + 1 / 8), dim * 3.0))
        holes[5].SetPosition(pcbnew.wxPointMM(dim * (2 + 1 / 2 + 1 / 4), dim * 3.5))
        holes[6].SetPosition(pcbnew.wxPointMM(dim * (4 + 3 / 4), dim * 2.5))
        holes[7].SetPosition(pcbnew.wxPointMM(dim * (6 + 3 / 4), dim * 2.5))
        holes[8].SetPosition(
            pcbnew.wxPointMM(dim * (5 + 3 / 4 - 1 / 8), dim * (3 + 1 / 2 + 1 / 8))
        )
        holes[9].SetPosition(
            pcbnew.wxPointMM(dim * (8 + 3 / 4 + 1 / 8), dim * (3 + 1 / 2 + 1 / 8))
        )
        holes[10].SetPosition(pcbnew.wxPointMM(dim * 8, dim * 0.5))
        holes[11].SetPosition(pcbnew.wxPointMM(dim * 10, dim * 1.5))
        holes[12].SetPosition(pcbnew.wxPointMM(dim * 12, dim * 1.5))
        holes[13].SetPosition(
            pcbnew.wxPointMM(dim * (14 + 1 / 8), dim * (1 / 2 + 1 / 8))
        )
        holes[14].SetPosition(pcbnew.wxPointMM(dim * (14 + 1 / 2 + 1 / 4), dim * (2)))
        holes[15].SetPosition(pcbnew.wxPointMM(dim * (12), dim * (3 + 1 / 2)))
        holes[16].SetPosition(pcbnew.wxPointMM(dim * (14), dim * (3 + 1 / 2 - 1 / 8)))

        holes[17].SetPosition(pcbnew.wxPointMM(dim * (3 + 1 / 2 + 1 / 4), dim * 3.5))
        holes[18].SetPosition(pcbnew.wxPointMM(dim * 14, dim * 1.5))
        holes[19].SetPosition(pcbnew.wxPointMM(dim * (11 - 1 / 4), dim * (2 + 1 / 2)))
        holes[20].SetPosition(pcbnew.wxPointMM(dim * (1 / 4 + 1 / 8), dim * 2.5))

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
    if track.GetAngle() < 0:
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(start)
        track.SetEnd(end)
    track.SetWidth(int(0.3 * 1e6))
    track.SetLayer(layer)
    board.Add(track)


def add_arc_from(
    point, ex, ey, mx, my, reverse=False, d=Switch._radius, layer=pcbnew.F_Cu
):
    end = pcbnew.wxPoint(point.x + (d if ex else -d), point.y + (d if ey else -d))
    mid = pcbnew.wxPoint(point.x + (d if mx else -d), point.y + (d if my else -d))
    if reverse:
        add_arc(end, point, mid, layer)
    else:
        add_arc(point, end, mid, layer)
    return end


def place_fp(offset, fp, pos, orient):
    fp.SetOrientation(orient * 10)  # 1/10 of degree
    p = pcbnew.wxPointMM(pos[0] + offset[0], pos[1] + offset[1])
    fp.SetPosition(p)


kb = Keyboard()
kb.place_footprints()
kb.remove_tracks()
kb.add_tracks()
# kb.add_holes()
