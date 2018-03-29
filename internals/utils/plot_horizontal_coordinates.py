#!/usr/bin/env python3

import cv2
import math

img = cv2.imread('template.JPG')
lines = open('horizontal_coordinates.txt').readlines()

cx = img.shape[1] // 2
cy = img.shape[0] // 2

coordinates = []
for line in lines:
	line = line.replace(' ', '').strip()
	line = line.split(',')

	coordinates.append((int(line[0]), int(line[1])))

for sx, sy in coordinates:
	cv2.circle(img, (cx, cy), round(math.sqrt((sx - cx) ** 2 + (sy - cy) ** 2)), (0, 255, 255), 3)

for sx, sy in coordinates:
	cv2.circle(img, (sx, sy), 12, (0, 0, 255), 24)

#img = cv2.resize(img, (img.shape[1] // 6, img.shape[0] // 6))
cv2.imwrite("plot.png", img)
print("Image saved as plot.png")
