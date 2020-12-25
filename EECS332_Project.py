# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 13:49:09 2020

@author: Haroon Nawaz
"""

import cv2
import numpy as np
import EECS332_MP2 as morph



def MakeMask(frame, SE, mark):
    frameHSV =cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if mark == "text":
        sample1 = frameHSV[150:222,16:298,:]
        minH = np.min(sample1[:,:,0])
        minS = np.min(sample1[:,:,1])
        minV = np.min(sample1[:,:,2])
        maxH = np.max(sample1[:,:,0])
        maxS = np.max(sample1[:,:,1])
        maxV = np.max(sample1[:,:,2])
        normalLow = np.array([minH,minS,minV])
        normalHigh = np.array([maxH,maxS,maxV])
    elif mark == "pointer":
        normalLow = np.array([0, 90, 30])
        normalHigh = np.array([20, 255, 255])

    maskNormal = cv2.inRange(frameHSV, normalLow, normalHigh)

    maskNoise = ~maskNormal
    maskNormal = np.zeros(maskNoise.shape,np.uint8)
    if mark == "text":
        maskNormal[67:129,55:293] = maskNoise[67:129,55:293]
        maskNormal = morph.opening(maskNormal, SE, SE)
    elif mark == "pointer":
        maskNormal = ~maskNormal
        maskNormal[0:55,:] = maskNoise[0:55,:]
        maskNormal = ~maskNormal  
    maskNormal = maskNormal.astype(int)
    return maskNormal

def SeparatingColumns(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    emptyCols = []
    numCols = len(gray[0])

    for col in range(numCols):
        total = sum(gray[50:240,col])
        if (col < 200 and total > 25200) or (col > 200 and total > 23300):
            emptyCols.append(col)  
    last = 0
    separatingCols = []
    blank = [0]
    for col in emptyCols:
        if col - last == 1:
            blank.append(col)
        else:
            middle = round(sum(blank)/len(blank))
            separatingCols.append(middle)
            blank = [col]
        last = col
    return separatingCols

def FindInpaintLocations(maskNormal, pointerCol):
    reference = {}
    for col in range(pointerCol,len(maskNormal[0])):
        rowLow = -1
        for row in range(0,len(maskNormal)):
            if maskNormal[row][col] > 1:
                if rowLow == -1:
                    rowLow = row
                rowHigh = row
        if rowLow != -1:
            for colSeparator in separatingCols:
                if col >= colSeparator:
                    colIndex = separatingCols.index(colSeparator)
                    colLow, colHigh= (separatingCols[colIndex], separatingCols[colIndex+1])
            reference[colHigh] = [rowLow,rowHigh,colLow,colHigh]
    return reference
def GetPointerLocation(frame, SE):
    marker = MakeMask(frame, SE, "pointer")
    coords = np.nonzero(marker)[1]
    count = 0
    total = 0
    for coord in coords:
        total += coord
        count +=1
    center = int(total/count)
    return center

if __name__ == '__main__':
    try:
        video = cv2.VideoCapture("Original.avi")
        check, frame = video.read()
        frameCopy = frame.copy()
        SE1 = cv2.imread("SE/SE_2x2.bmp",0)
        center1 = [0,0]
        SE1 = morph.make_SE(SE1, center1)
        

        maskNormal = MakeMask(frame, SE1, "text")
        
        separatingCols = SeparatingColumns(frame)
        blankCol = np.full((240, 3),255)
        separatingImg = frame.copy()
        for col in separatingCols:
            separatingImg[:,col,:] = blankCol
        cv2.imwrite("separatingCols.bmp", separatingImg)
        check = True
        leftmostPointerCol = 9999
        output = frame
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 15.0, (320,240))
        while(True):
            check, frame = video.read()
            if not check:
                cv2.imwrite("Final_Frame.png", output)
                cv2.destroyAllWindows()
                break

            fixedImg = frame.copy()
            pointerCol = GetPointerLocation(frame, SE1)
            if pointerCol > leftmostPointerCol:
                pointerCol = leftmostPointerCol
            leftmostPointerCol = pointerCol
            inpaintLocations = FindInpaintLocations(maskNormal, pointerCol)
            for col in inpaintLocations:
                if col >= pointerCol:
                    rowLow = inpaintLocations[col][0]
                    rowHigh = inpaintLocations[col][1]
                    colLow = inpaintLocations[col][2] if (inpaintLocations[col][2] >= pointerCol) else pointerCol
                    colHigh = inpaintLocations[col][3]
                    rowLow -= 1
                    rowHigh += 1
                    rowSize = rowHigh-rowLow
                    replace = frame[140:140+rowSize, colLow:colHigh,:]
                    frame[rowLow:rowHigh, colLow:colHigh,:] = replace
            output = frame
            
            scaling = 2.2
            width = int(output.shape[1] * scaling)
            height = int(output.shape[0] * scaling)
            dim = (width, height)
            #output = cv2.resize(output, dim, interpolation = cv2.INTER_AREA)
            out.write(output)
            cv2.imshow("Output", output)
            key = cv2.waitKey(1)
        
    except KeyboardInterrupt:
        cv2.destroyAllWindows()

    video.release()
    out.release()
    cv2.destroyAllWindows()
    
