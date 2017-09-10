#!/usr/bin/env python3

import cv2
import math

img = cv2.imread('IMG_9210.JPG')
lines = open('horizontal_coordinates.txt').readlines()
for line in lines:
	line = line.replace(' ', '').strip()
	line = line.split(',')
	cx = img.shape[1] // 2
	cy = img.shape[0] // 2
	sx = int(line[0])
	sy = int(line[1])
	cv2.circle(img, (sx, sy), 10, (0, 255, 255), 10)
	#cv2.circle(img, (cx, cy), round(math.sqrt((sx - cx) ** 2 + (sy - cy) ** 2)), (0, 255, 255), 2)
img = cv2.resize(img, (img.shape[1] // 6, img.shape[0] // 6))
cv2.imshow('Plot', img)
cv2.waitKey(0)
