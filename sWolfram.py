import numpy as np


class CellularAutomaton:
    def __init__(self, size):
        self.size = size
        self.cell = np.zeros((size, size), dtype=np.uint8)
        self.n_reflection = 0
        self.count_reflection = 0

    def reset(self):
        self.n_reflection = 0
        self.count_reflection = 0
        rate = 5
        self.cell = np.zeros((self.size, self.size), dtype=np.uint8)
        for y in range(self.size):
            for x in range(self.size):
                tmp = np.random.randint(0, rate)
                if 0 < tmp <= 1:
                    self.cell[y][x] = 1

    def expression(self):
        self.cell[np.random.randint(0, self.size)][np.random.randint(0, self.size)] = 1

    def reflection(self):
        reflected = self.cell.copy()
        for y in range(self.size):
            for x in range(self.size):
                if self.cell[y][x] == 0:
                    if y == 0 and x == 0:
                        density = np.count_nonzero(self.cell[y:y+2, x:x+2])
                    elif y == 0:
                        density = np.count_nonzero(self.cell[y:y+2, x-1:x+2])
                    elif x == 0:
                        density = np.count_nonzero(self.cell[y-1:y+2, x:x+2])
                    else:
                        density = np.count_nonzero(self.cell[y-1:y+2, x-1:x+2])
                    if density >= 3:
                        reflected[y][x] = 1
        self.cell = reflected
        self.n_reflection += 1


class BZCellularAutomaton(CellularAutomaton):
    def reset(self):
        rate = 60
        self.cell = np.zeros((self.size, self.size), dtype=np.uint8)
        for y in range(self.size):
            for x in range(self.size):
                tmp = np.random.randint(0, rate)
                if 0 < tmp <= 2:
                    self.cell[y][x] = tmp

    def reflection(self):
        """
        Belousov-Zhabotinsky reaction by Greenberg-Hastings model
        """
        reflected = self.cell.copy()
        for y in range(self.size):
            for x in range(self.size):
                if self.cell[y][x] == 0:
                    if y == 0 and x == 0:
                        if np.any(self.cell[y:y+2, x] == 1) or np.any(self.cell[y, x:x+2] == 1):
                            reflected[y][x] = 1
                    elif y == 0:
                        if np.any(self.cell[y:y+2, x] == 1) or np.any(self.cell[y, x-1:x+2] == 1):
                            reflected[y][x] = 1
                    elif x == 0:
                        if np.any(self.cell[y-1:y+2, x] == 1) or np.any(self.cell[y, x:x+2] == 1):
                            reflected[y][x] = 1
                    else:
                        if np.any(self.cell[y-1:y+2, x] == 1) or np.any(self.cell[y, x-1:x+2] == 1):
                            reflected[y][x] = 1
                elif self.cell[y][x] == 1:
                    reflected[y][x] = 2
                elif self.cell[y][x] == 2:
                    reflected[y][x] = 0
        self.cell = reflected
        self.n_reflection += 1


class FilterAutomaton(CellularAutomaton):
    def reset(self):
        self.cell = np.zeros((self.size, self.size), dtype=np.uint8)
        for i in range(self.size//3*2, self.size):
            tmp = np.random.randint(0, 5)
            if 0 < tmp <= 1:
                self.cell[0, i] = 1
        self.y = 0

    def expression(self):
        self.cell[self.y+1][np.random.randint(0, self.size)] = 1

    def reflection(self):
        """
        soliton
        """
        r = 3
        for x in range(self.size):
            if x < r:
                tmp = np.sum(self.cell[self.y+1, 0:x]) + np.sum(self.cell[self.y, x:x+r+1])
            elif (x + r) > self.size:
                tmp = np.sum(self.cell[self.y+1, x-r:x]) + np.sum(self.cell[self.y, x:self.size+1])
            else:
                tmp = np.sum(self.cell[self.y+1, x-r:x]) + np.sum(self.cell[self.y, x:x+r+1])
            if tmp > 0 and (tmp % 2) == 0:
                self.cell[self.y+1][x] = 1
            else:
                self.cell[self.y+1][x] = 0
        if sum(self.cell[self.y, 0:3]) >= 2:
            # self.cell[self.y+1, :] = 0
            pass
        self.y += 1
        self.n_reflection += 1


class GameOfLife(CellularAutomaton):
    def reflection(self):
        reflected = self.cell.copy()
        for y in range(self.size):
            for x in range(self.size):
                if y == 0 and x == 0:
                    density = np.count_nonzero(self.cell[y:y+2, x:x+2])
                elif y == 0:
                    density = np.count_nonzero(self.cell[y:y+2, x-1:x+2])
                elif x == 0:
                    density = np.count_nonzero(self.cell[y-1:y+2, x:x+2])
                else:
                    density = np.count_nonzero(self.cell[y-1:y+2, x-1:x+2])
                if self.cell[y][x] == 1:
                    density -= 1
                    if 2 <= density <= 3:
                        reflected[y][x] = 1
                    if (density <= 1) or (density >= 4):
                        reflected[y][x] = 0
                elif self.cell[y][x] == 0:
                    if density == 3:
                        reflected[y][x] = 1
        self.cell = reflected
        self.n_reflection += 1

    def pattern_matching(self, patterns):
        """
        pattern should 1-padding with 0
        """
        n = 0
        w = patterns.shape[1]
        zeros = np.zeros((1, w))
        for y in range(0, self.size-w-1):
            for x in range(0, self.size-w-1):
                # if np.any(patterns[:, 0, :] == self.cell[y, x:x+w]):
                if np.all(zeros == self.cell[y, x:x+w]):
                    idx = np.where(np.all(patterns[:, 1, :] == self.cell[y+1, x:x+w], axis=1))[0]
                    if len(idx):
                        for i in idx:
                            for j in range(2, w):
                                if not np.all(patterns[i, j, :] == self.cell[y+j, x:x+w]):
                                    break
                            else:
                                n += 1
                                break
        return n

    def count_glider(self):
        glider = np.array([
            [
                [0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 1, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 1, 1, 0],
                [0, 1, 1, 0, 0],
                [0, 0, 0, 0, 0],
            ],
        ])
        w = glider.shape[1]
        glider = np.append(glider, glider[0].T.reshape(1, w, w), axis=0)
        glider = np.append(glider, glider[1].T.reshape(1, w, w), axis=0)
        # RightUpper
        glider = np.append(glider, np.rot90(glider[0], 1).reshape(1, w, w), axis=0)
        glider = np.append(glider, np.rot90(glider[1], 1).reshape(1, w, w), axis=0)
        glider = np.append(glider, np.rot90(glider[2], 1).reshape(1, w, w), axis=0)
        glider = np.append(glider, np.rot90(glider[3], 1).reshape(1, w, w), axis=0)
        # LeftUpper
        glider = np.append(glider, np.rot90(glider[0], 2).reshape(1, w, w), axis=0)
        glider = np.append(glider, np.rot90(glider[1], 2).reshape(1, w, w), axis=0)
        glider = np.append(glider, np.rot90(glider[2], 2).reshape(1, w, w), axis=0)
        glider = np.append(glider, np.rot90(glider[3], 2).reshape(1, w, w), axis=0)
        # LeftLower
        glider = np.append(glider, np.rot90(glider[0], 3).reshape(1, w, w), axis=0)
        glider = np.append(glider, np.rot90(glider[1], 3).reshape(1, w, w), axis=0)
        glider = np.append(glider, np.rot90(glider[2], 3).reshape(1, w, w), axis=0)
        glider = np.append(glider, np.rot90(glider[3], 3).reshape(1, w, w), axis=0)
        return self.pattern_matching(glider)

    def count_eater(self):
        eater = np.array([
            [
                [0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0],
                [0, 1, 0, 1, 0, 0],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 0, 1, 1, 0],
                [0, 0, 0, 0, 0, 0],
            ],
        ])
        w = eater.shape[1]
        eater = np.append(eater, eater[0].T.reshape(1, w, w), axis=0)
        eater = np.append(eater, np.rot90(eater[0], 1).reshape(1, w, w), axis=0)
        eater = np.append(eater, np.rot90(eater[1], 1).reshape(1, w, w), axis=0)
        eater = np.append(eater, np.rot90(eater[0], 2).reshape(1, w, w), axis=0)
        eater = np.append(eater, np.rot90(eater[1], 2).reshape(1, w, w), axis=0)
        eater = np.append(eater, np.rot90(eater[0], 3).reshape(1, w, w), axis=0)
        eater = np.append(eater, np.rot90(eater[1], 3).reshape(1, w, w), axis=0)
        return self.pattern_matching(eater)
