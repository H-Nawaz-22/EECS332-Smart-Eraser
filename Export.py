# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 14:41:09 2020

@author: Haroon Nawaz
"""
import cv2
video = cv2.VideoCapture("Original.avi")

totalFrames = video.get(7)

frames = [50, 100, 150, 200]
for i in frames:
    video.set(1, i)
    ret, frame = video.read()
    cv2.imwrite("Original"+str(i)+".png",frame)
