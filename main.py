""" @R1nY1x1
     ______  ______  __      __
    / ____/ / ____/ / /     / /
   / /     / /___  / /     / /
  / /     / ____/ / /     / /
 / /___  / /___  / /___  / /___
/_____/ /_____/ /_____/ /_____/
"""
import time
import sys
import termios
import shutil
import pickle
import argparse
from concurrent import futures
import numpy as np
import dippy as dp
import sWolfram


class Praparat:
    def __init__(self, ca):
        self.room = [ca, ]
        self.size = ca.size
        self.n_glider = 0
        self.n_eater = 0
        self.room.append(sWolfram.GameOfLife(self.size))
        # self.room[1].reset()


def reflectionLoop(praparat, delay, cmd):
    while(True):
        praparat.room[cmd["ch"]].count_reflection = 0
        while(praparat.room[cmd["ch"]].count_reflection < int(praparat.room[cmd["ch"]].size/2)):
            if cmd["cmd"] == "quit":
                break
            while cmd["cmd"] == "stop":
                time.sleep(0.001)
            praparat.room[cmd["ch"]].count_reflection += 1
            time.sleep(delay)
        if cmd["cmd"] == "quit":
            break
        praparat.room[cmd["ch"]].reflection()


def interactiveLoop(praparat, cmd):
    while(True):
        # =magmax/python-readchar.git/../_posix_read.py=
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        term = termios.tcgetattr(fd)
        try:
            term[3] &= ~(termios.ICANON | termios.ECHO | termios.IGNBRK | termios.BRKINT)
            termios.tcsetattr(fd, termios.TCSAFLUSH, term)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        # ====================So far====================
        cmd["cmd"] = char
        if cmd["cmd"] == "\x0a":
            if cmd["num"] == 1:
                if praparat.room[cmd["ch"]].n_reflection:
                    praparat.n_glider += praparat.room[cmd["ch"]].count_glider()
                    praparat.n_eater += praparat.room[cmd["ch"]].count_eater()
                    praparat.room[cmd["ch"]].count_reflection = 0
                    praparat.room[cmd["ch"]].reset()
            elif cmd["num"] == 2:
                # praparat.room[cmd["ch"]].expression()
                cmd["ch"] = cmd["ch"]+1 if cmd["ch"] != cmd["max_ch"] else 0
                praparat.room[cmd["ch"]].count_reflection = 0
            elif cmd["num"] == 3:
                cmd["cmd"] = "quit"
                break
        elif cmd["cmd"] in ["j"]:
            cmd["num"] = cmd["num"]+1 if cmd["num"] != cmd["max_num"] else 1
        elif cmd["cmd"] in ["k"]:
            cmd["num"] = cmd["num"]-1 if cmd["num"] != 1 else cmd["max_num"]


def stdoutLoop(praparat, cmd):
    while(True):
        if cmd["cmd"] == "quit":
            break
        tmp = praparat.room[cmd["ch"]].cell.copy()
        tmp[tmp != 1] = 0
        print(f"\033[3;{int(praparat.room[cmd['ch']].size/2)+3}H| glider: {praparat.n_glider:>3} |")
        print(f"\033[4;{int(praparat.room[cmd['ch']].size/2)+3}H| eater: {praparat.n_eater:>4} |")
        print(f"\033[5;{int(praparat.room[cmd['ch']].size/2)+3}H| ref = {praparat.room[cmd['ch']].n_reflection:>5} |")
        print(f"\033[6;{int(praparat.size/2)+3}H| room_ch = {cmd['ch']} |")
        print(
            f"\033[8;{int(praparat.room[cmd['ch']].size/2)+3}H|"
            + f"\033[{1 if cmd['num']==1 else 0}m Reset"
            + "\033[0m       |"
        )
        print(
            f"\033[9;{int(praparat.room[cmd['ch']].size/2)+3}H|"
            + f"\033[{1 if cmd['num']==2 else 0}m Room Change"
            + "\033[0m |"
        )
        print(
            f"\033[10;{int(praparat.room[cmd['ch']].size/2)+3}H|"
            + f"\033[{1 if cmd['num']==3 else 0}m Save & Quit"
            + "\033[0m |"
        )
        print(
            f"\033[{int(praparat.room[cmd['ch']].size/4)+2};2H"
            + ("#"*praparat.room[cmd['ch']].count_reflection)
            + (" "*(int(praparat.room[cmd['ch']].size/2)+2-praparat.room[cmd['ch']].count_reflection))
        )
        dp.printImgXY(tmp, 1, 1, 2)
        time.sleep(0.01)


class TerminalSizeError(Exception):
    pass


def main(args):
    terminal_size = shutil.get_terminal_size()
    if terminal_size.lines < 11:
        raise TerminalSizeError("Terminal line size should be 11 or bigger.")
    if terminal_size.columns < 16:
        raise TerminalSizeError("Terminal column size should be 16 or bigger.")

    Y = (terminal_size.lines - 3) * 4
    X = (terminal_size.columns - 18) * 2
    if Y <= X:
        size = Y
    elif X <= Y:
        size = X

    delay = 0.1

    if args.file:
        with open(args.file, "rb") as f:
            praparat = pickle.load(f)
    else:
        if args.template:
            cell = np.load(args.template)
            if size < cell.shape[0]:
                raise TerminalSizeError(f"Terminal size should be {cell.shape[0]} or bigger.")
            size = cell.shape[0]
            ca = sWolfram.GameOfLife(size)
            ca.reset()
            ca.cell = cell
        else:
            # ca = sWolfram.BZCellularAutomaton(size)
            # ca = sWolfram.FilterAutomaton(size)
            ca = sWolfram.GameOfLife(size)
            ca.reset()
        praparat = Praparat(ca)

    print("\033[2J")
    print(f"\033[2;{int(praparat.size/2)+3}H+-------------+")
    print(f"\033[3;{int(praparat.size/2)+3}H| glider: {praparat.n_glider:>3} |")
    print(f"\033[4;{int(praparat.size/2)+3}H| eater: {praparat.n_glider:>4} |")
    print(f"\033[5;{int(praparat.size/2)+3}H| ref = {praparat.room[0].n_reflection:>5} |")
    print(f"\033[6;{int(praparat.size/2)+3}H| room_ch = 0 |")
    print(f"\033[7;{int(praparat.size/2)+3}H+-------------+")
    print(f"\033[8;{int(praparat.size/2)+3}H| Reset       |")
    print(f"\033[9;{int(praparat.size/2)+3}H| Room Change |")
    print(f"\033[10;{int(praparat.size/2)+3}H| Sace & Quit |")
    print(f"\033[11;{int(praparat.size/2)+3}H+-------------+")
    dp.printImgXY(praparat.room[0].cell, 1, 1, 2)

    future_list = []
    command = {"cmd": "", "num": 1, "max_num": 3, "ch": 0, "max_ch": 1}
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_list.append(executor.submit(reflectionLoop, praparat=praparat, delay=delay, cmd=command))
        future_list.append(executor.submit(interactiveLoop, praparat=praparat, cmd=command))
        future_list.append(executor.submit(stdoutLoop, praparat=praparat, cmd=command))
        _ = futures.as_completed(fs=future_list)

    with open("Praparat.pkl", "wb") as f:
        pickle.dump(praparat, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-f", "--file", help="ファイル読込")
    parser.add_argument("-t", "--template", help="テンプレート読込")
    args = parser.parse_args()
    main(args)
