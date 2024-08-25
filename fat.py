import sys
from typing import Optional
import PyQt5
from PyQt5.QtCore import QSize
from PyQt5.Qt import *
import time
import os
import pickle
blockSize = 512
blockNum = 512

class FAT:
    def __init__(self):
        self.fat = []
        for i in range(blockNum):
            self.fat.append(-2)

    def findBlank(self):
        for i in range(blockNum):
            if self.fat[i] == -2:
                return i
        return -1

    def write(self, data, disk):
        start = -1
        cur = -1

        while data != "":
            newLoc = self.findBlank()
            if newLoc == -1:
                raise Exception(print('磁盘空间不足!'))
                return
            if cur != -1:
                self.fat[cur] = newLoc
            else:
                start = newLoc
            cur = newLoc
            data = disk[cur].write(data)
            self.fat[cur] = -1

        return start

    def delete(self, start, disk):
        if start == -1:
            return

        while self.fat[start] != -1:
            disk[start].clear()
            las = self.fat[start]
            self.fat[start] = -2
            start = las

        self.fat[start] = -2
        disk[start].clear()

    def update(self, start, data, disk):
        self.delete(start, disk)
        return self.write(data, disk)

    def read(self, start, disk):
        data = ""
        while self.fat[start] != -1:
            data += disk[start].read()
            start = self.fat[start]
        data += disk[start].read()
        return data

    def get_usage_percentage(self):
        used_blocks = sum(1 for block in self.fat if block != -2)
        total_blocks = len(self.fat)
        return (used_blocks / total_blocks) * 100