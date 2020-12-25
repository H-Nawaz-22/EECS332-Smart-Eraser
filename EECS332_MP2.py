# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 00:18:24 2020

@author: Haroon Nawaz

In this Machine Problem 2, a series of morphological operators are implemented, namely:
    erosion, dilaton, opening, closing, and boundary. These operators were tested on
    images gun.bmp and palm.bmp.
"""

import cv2
import numpy as np

def erosion(img, SE):
    '''
    Returns an image with a pixel wherever SE exists in img.
    '''
    height, width = (len(img), len(img[0]))
    imgOut = np.zeros((height, width))
    for row in range(0, height):
        for col in range(0, width):
            included = True
            for pos in SE:
                checkY = pos[0] + row
                checkX = pos[1] + col
                if checkX < 0 or checkY < 0 or checkX >= width or checkY >= height: # Out of bounds
                    included = False
                    break
                if img[checkY][checkX] < 1:
                    included = False
                    break
            if included:
                imgOut[row][col] = 255
    return imgOut
                
def dilation(img, SE):
    '''
    Returns an image with SE placed wherever img has a pixel.
    '''
    height, width = (len(img), len(img[0]))
    imgOut = np.zeros((height, width))
    for row in range(0, height):
        for col in range(0, width):
            if img[row][col] > 0:
                for pos in SE:
                    try:
                        imgOut[pos[0]+row][pos[1]+col] = 255
                    except IndexError: # Out of image bounds
                        pass;
    return imgOut

def opening(img, SE1, SE2):
    '''
    Performs an erosion and then a dilation on img, with SE1 and SE2, respectively. Returns the resulting image.
    '''
    imgOut1 = erosion(img, SE1)
    imgOut = dilation(imgOut1, SE2)
    return imgOut
def closing(img, SE1, SE2):
    '''
    Performs a dilation and then an erosion on img, with SE1 and SE2, respectively. Returns the resulting image.
    '''
    imgOut1 = dilation(img, SE1)
    imgOut = erosion(imgOut1, SE2)
    return imgOut
def boundary(img, SE):
    imgEroded = erosion(img, SE)
    return img - imgEroded

def make_SE(img, center):
    '''
    Makes a structuring element out of a image file. Returns a list of coordinates that correspond to relative
    positions to a center pixel.
    '''
    SE = []
    height, width = (len(img), len(img[0]))
    centerX, centerY = (center[0], center[1])
    for row in range(0, height):
        for col in range(0, width):
            if img[row][col] > 0:
                pos = [row - centerX, col - centerY]
                SE.append(pos)
    return SE
            
if __name__ == '__main__':
    ''' Inputs '''
    filename = "gun.bmp" # Variable image filename
    fileExtension = ".bmp" 
    process = "dilation" # Morphological operator being performed
    filenameSE = "SE_3x3.bmp" # Filename of SE in .bmp format
    center1 = [1,1] # The center coordinates for filenameSE, needed for make_SE.
    
    #These two are only used for the closing and opening operations, when a second SE can be specified.
    filenameSE2 = "SE_circle7.bmp"
    center2 = [3,3]
    '''  '''
    
    img = cv2.imread(filename, 0) # Opens .bmp file
    imgSE1 = cv2.imread("SE/" + filenameSE, 0)  
    SE1 = make_SE(imgSE1, center1)
    arguments = (img, SE1)
    outputName = filename.split(".")[0] + "_" + process + "_" + filenameSE.split(".")[0]
    
    if process == "opening" or process == "closing":
        imgSE2 = cv2.imread("SE/" + filenameSE2, 0)
        SE2 = make_SE(imgSE2, center2)
        arguments = (img, SE1, SE2)  
        outputName = outputName + "_" + filenameSE2.split(".")[0]
        
    functions = {"erosion": erosion, "dilation": dilation, "opening": opening, "closing": closing, "boundary": boundary}
    
    imgOut = functions[process](*arguments)
    outputName = outputName + fileExtension
    cv2.imwrite(outputName, imgOut) # Writes .bmp file