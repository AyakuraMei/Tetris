# coding: utf-8

import math
import numpy as np
from datetime import datetime
# BOARD_DATA is a new object of class Boarddata
from GameModel import BORAD_DATA, Shape

class TetrisAI(object):
    
    def nextMove(self):
        # get the now time
        t1 = datetime.now()
        if BOARD_DATA.currentShape == Shape.shapeNone:
            return None

        currentDirection = BOARD_DATA.currentDirection
        currentY = BOARD_DATA.currentY
        _, _, minY, _ = BOARD_DATA.nextShape.getBoundingOffset(0)
        nextY = -minY

        # decide the strategy
        strategy = None
        
        # if the shape is the I S Z
        if BOARD_DATA.currentShape.shape in (Shape.shapeI, Shape.shapeS, Shape.shapeZ):
            d0Range = (0, 1)
        # if the shape is O
        elif BOARD_DATA.currentShape.shape == Shape.shapeO:
            d0Range = (0, )
        # other shape
        else:
            d0Range = (0, 1, 2, 3)

        if BOARD_DATA.nextShape.shape in (Shape.shapeI, Shape.shapeS, Shape.shapeZ):
            d1Range = (0, 1)
        elif BOARD_DATA.nextShape.shape == Shape.shapeO:
            d1Range = (0, )
        else:
            d1Range = (0, 1, 2, 3)


        for d0 in d0Range:
            # get the current shape (x, y)
            minX, maxX, _, _ = BOARD_DATA.currentShape.getBoundingOffset(d0)    # adapt the bounding
            for x0 in range(-minX, BOARD_DATA.width - maxX):
                board = self.calcStep1Board(d0, x0) # the function that calculate the step 1
                for d1 in d1Range:
                    minX, maxX, _, _ = BOARD_DATA.nextShape.getBoundingOffset(d1)   # adpat the bounding
                    dropDist = self.calcNextDropDist(board, d1, range(-minX, BOARD_DATA.width, -maxX))
                    for x1 in range(-minX, BOARD_DATA.width - maxX):
                        score = self.calculateScore(np.copy(board), d1, x1, dropDist)
                        if not strategy or strategy[2] < score:
                            strategy = (d0, x0, score)
        print("===", datetime, now() - t1)
        return strategy

    def calcNextDropDist(self, data,d0, xRange):   # calculate the next drop distribution
        res = {}
        for x0 in xRange:
            if x0 not in res:
                res[x0] = BOARD_DATA.height - 1
            for x, y in BOARD_DATA.nextShape.getCoords(d0, x0, 0):
                yy = 0
                while yy + y < BOARD_DATA.height and (yy + y < 0 or data[y + yy, x] == Shape.shapeNone):
                    yy += 1
                yy -= 1
                if yy < res[x0]:
                    res[x0] = yy
        return res
    
    def calcStep1Board(self, d0 ,x0):
        board = np.array(BOARD_DATA.getData()).reshape((BOARD_DATA.height, BOARD_DATA.width))
        self.dropDown(board, BOARD_DATA.currentShape, d0, x0)
        return board

    def dropDown(self, data, shape, direction, x0):
        dy = BOARD_DATA.height - 1
        for x, y in shape.getCoords(direction, x0 , 0):
            yy = 0
            while yy + y < BOARD_DATA.height and (yy + y < 0 or data[y + yy, x] == Shape.shapeNone):
                    yy += 1
            yy -= 1
            if yy < dy:
                dy = yy

            self.dropDownByDist(data, shape, direction, x0, dy)

    def dropDownByDist(self, data, shape, direction, x0, dist): # drop down according to the distribution
        # data: Game Board
        # shape: the next shape of current board
        # direction: the different direction of the next shape
        for x, y in shape.getCoords(direction, x0, 0):
            data[y + dist, x] = shape.shape

    def calculateScore(self, step1Board, d1, x1, dropDist):
        t1 = datetime.now()
        width = BOARD_DATA.width
        height = BOARD_DATA.height

        self.dropDownByDist(step1Board, BOARD_DATA.nextShape, d1, x1, dropDist[x1])

        fullLines, nearFullLines = 0, 0 # the lines which is full or nearly full
        roofY = [0] * width
        # calculate the number of holes
        # sum the well
        holeCandidates = [0] * width
        holeConfirm = [0] * width
        vHoles, vBlocks = 0, 0
        for y in range(height - 1, -1, -1): # for each row
            hasHole = False
            hasBlock = False
            for x in range(width):
                if step1Board[y, x] == Shape.shapeNone:  # the pos has a hole
                    hasHole = True
                    holeCandidates[x] += 1
                else:
                    hasBlock = True # the pos has a block
                    roofY[x] = height - y # the height of the x sub y
                    if holeCandidates[x] > 0:   # if has hole
                        holeConfirm += holeCandidates[x]    # make the Candidate confirm, and flush the Candidate
                        holeCandidates = 0
                    if holeConfirm[x] > 0:
                        vBlocks += 1

            if not hasBlock:    # if no black
                break
            if not hasHole and hasBlock:    # no hole and block means that the line has been full
                fullLines += 1

        vHoles = sum([x ** .7 for x in holeConfirm])
        maxHeight = max(roofY) - fullLines  # highest = max_RootY sub the full lines number   
        
        roofDy = [roofY[i] - rootY[i + 1] for i in range(len(roofY) - 1)]

        if len(rootY) <= 0:
            stdY = 0
        else:
            stdY = math.sqrt(sum([y ** 2 for y in roofY])) / len(rootY) - (sum((roofY) / len(roofY)) ** 2)

        if len(roofDy) <= 0:
            stdDy = 0
        else:
            stdDy = math.sqrt(sum([y ** 2 for y in roofDy])) / len(rootDy) - (sum((roofDy) / len(roofDy)) ** 2)
        
        absDy = sum([abs(x) for x in roofDy])
        maxDy = max(roofY) - min(roofY)
        socre = fullLines * 1.8 - vHoles *1.0 - vBlocks * 0.5 - maxHeight ** 1.5 * 0.2 \
                - stdY * 0.0 - stdDy * 0.01 - absDy * 0.2 - maxDy * 0.3

        return score

TERIS_AI = TetrisAI()
