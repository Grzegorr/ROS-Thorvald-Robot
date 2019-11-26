#!/usr/bin/env python

import rospy
from cv2 import namedWindow, cvtColor, imshow
from cv2 import destroyAllWindows, startWindowThread
from cv2 import COLOR_BGR2GRAY, waitKey
from cv2 import blur, Canny
from numpy import mean
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy
from matplotlib import pyplot as plt



img_raw = cv2.imread("ziemia.png")
#mg_raw = cv2.cvtColor(img_raw,cv2.COLOR_BGR2HSV)
b, g, r = cv2.split(img_raw)

plt.figure(1)
plt.hist(b.ravel(),256,[0,256]); plt.show(block=False)
plt.figure(2)
plt.hist(g.ravel(),256,[0,256]); plt.show(block=False)
plt.figure(3)
plt.hist(r.ravel(),256,[0,256]); plt.show(block=False)

#plt.hist(img_raw.ravel(),256,[0,256]); plt.show()
namedWindow("Ziemia raw")
cv2.imshow("Ziemia raw", img_raw)

waitKey(0)










