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

class GreenMask:
    detectionMode = "Diagnostics"

    def __init__(self):
        #initialize CV Bridge, this links ROS and OpenCV picture formats
        self.bridge = CvBridge()
        self.publisher = rospy.Publisher("/thorvald_001/green_masked_camera",  Image,  queue_size = 1)
        #Subscribe to an topica carring an image
        self.image_sub = rospy.Subscriber("/thorvald_001/kinect2_camera/hd/image_color_rect", Image, self.callback)
      
    def callback(self, data):
        #transfer image from ROS file system to openCV file
        cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        if self.detectionMode == "Diagnostics":
            self.diagnostics(cv_image)
        if self.detectionMode == "Young Lettice":
            self.youngLetticeDetection(cv_image)
        if self.detectionMode == "Grown Lettice":
            self.detectionGroenLettice(cv_image)
        waitKey(1)
        
    def diagnostics(self, cv_image):
        
        #BGR space
        b, g, r = cv2.split(cv_image)
        namedWindow("green")
        cv2.imshow('green', g)
        namedWindow("blue")
        cv2.imshow("blue", b)
        namedWindow("red")
        cv2.imshow("red", r)
        
        #HSC space
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        namedWindow("H")
        cv2.imshow("H",  h)
        namedWindow("S")
        cv2.imshow("S",  s)
        namedWindow("V")
        cv2.imshow("V",  v)
        
        #LAB space
        lab_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab_image)
        namedWindow("L(lab)")
        cv2.imshow("L(lab)",  l)
        namedWindow("A(lab)")
        cv2.imshow("A(lab)",  a)
        namedWindow("B(lab)")
        cv2.imshow("B(lab)",  b)
        
        #Edge detection
        canny_image = cv2.Canny(cv_image,  20,  70)
        namedWindow("Canny")
        cv2.imshow("Canny",  canny_image)
        
        #Display original image
        namedWindow("Original")
        cv2.imshow("Original",  cv_image)
        
    def youngGrownLettice(self,  cv_image): 
        #Bluring the image
        cv_image = cv2.blur(cv_image,  (5, 5))
        #changing to HSV colourspace
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    
        #Boundriec for detecting all plants as green colour
        lower_green = numpy.array([35,20,20])
        upper_green = numpy.array([200,255,255])
    
        #applaying the green mask for all plants
        allGreenMask = cv2.inRange(hsv_image, lower_green, upper_green)
        namedWindow("HSVgreen")
        cv2.imshow("HSVgreen",  allGreenMask)
    
        #Boundries and masking for cabbage only
        lower_cabbage = numpy.array([35,120,20])
        upper_cabbage = numpy.array([65,255,255])
        cabbageMask = cv2.inRange(hsv_image, lower_cabbage, upper_cabbage)
    
        #Dilaute to make safe zone for lettice
        kernel = numpy.ones((5,5),numpy.uint8)
        cabbageMask = cv2.dilate(cabbageMask,kernel,iterations = 3)
        #Display the mask if wanted
        namedWindow("HSVcabbage")
        cv2.imshow("HSVcabbage",  cabbageMask)
        
        #Display original image
        namedWindow("Original")
        cv2.imshow("Original",  cv_image)
    
        #This is just for storing and output for now
        weedMask = allGreenMask
        #Do logic on mask and display final mask
        cabbageMask = cv2.bitwise_not(cabbageMask)
        cv2.bitwise_and(cabbageMask, allGreenMask, weedMask )
        kernel = numpy.ones((3,3),numpy.uint8)
        weedMask = cv2.erode(weedMask,kernel,iterations =1)
        weedMask = cv2.dilate(weedMask,kernel,iterations =2)
        namedWindow("weedMask")
        cv2.imshow("weedMask",  weedMask)
    
        #Colour masked areas red
        indices = numpy.where(weedMask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        namedWindow("FinalOutput")
        cv2.imshow("FinalOutput",  cv_image)
    
        #For diagnosic reasons only
        h, s, v = cv2.split(hsv_image)
        namedWindow("H")
        cv2.imshow("H",  h)
        namedWindow("S")
        cv2.imshow("S",  s)
        namedWindow("V")
        cv2.imshow("V",  v)
    
    
    def detectionGrownLettice(self,  cv_image):
        #Bluring the image
        cv_image = cv2.blur(cv_image,  (5, 5))
        #changing to HSV colourspace
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    
        #Boundriec for detecting all plants as green colour
        lower_green = numpy.array([35,20,20])
        upper_green = numpy.array([65,255,255])
    
        #applaying the green mask for all plants
        allGreenMask = cv2.inRange(hsv_image, lower_green, upper_green)
        namedWindow("HSVgreen")
        cv2.imshow("HSVgreen",  allGreenMask)
    
        #Boundries and masking for cabbage only
        lower_cabbage = numpy.array([35,120,20])
        upper_cabbage = numpy.array([65,255,255])
        cabbageMask = cv2.inRange(hsv_image, lower_cabbage, upper_cabbage)
    
        #Dilaute to conntect the body of lettice
        kernel = numpy.ones((5,5),numpy.uint8)
        cabbageMask = cv2.dilate(cabbageMask,kernel,iterations = 5)
        #erode even more to get rid of the noise
        kernel = numpy.ones((5,5),numpy.uint8)
        cabbageMask = cv2.erode(cabbageMask,kernel,iterations =6)
        #diluting even more more to conteract erosion and give safe space around crops
        kernel = numpy.ones((3,3),numpy.uint8)
        cabbageMask = cv2.dilate(cabbageMask,kernel,iterations = 25)
        #Display the mask if wanted
        namedWindow("HSVcabbage")
        cv2.imshow("HSVcabbage",  cabbageMask)
    
        #Display original image
        namedWindow("Original")
        cv2.imshow("Original",  cv_image)
    
        #This is just for storing and output for now
        weedMask = allGreenMask
        #Do logic on mask and display final mask
        cabbageMask = cv2.bitwise_not(cabbageMask)
        cv2.bitwise_and(cabbageMask, allGreenMask, weedMask )
        kernel = numpy.ones((3,3),numpy.uint8)
        weedMask = cv2.erode(weedMask,kernel,iterations =1)
        weedMask = cv2.dilate(weedMask,kernel,iterations =2)
        namedWindow("weedMask")
        cv2.imshow("weedMask",  weedMask)
    
        #Colour masked areas red
        indices = numpy.where(weedMask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        namedWindow("FinalOutput")
        cv2.imshow("FinalOutput",  cv_image)
    
        #For diagnosic reasons only
        h, s, v = cv2.split(hsv_image)
        namedWindow("H")
        cv2.imshow("H",  h)
        namedWindow("S")
        cv2.imshow("S",  s)
        namedWindow("V")
        cv2.imshow("V",  v)

#startWindowThread()
#init a node
rospy.init_node('hsv_mask')
#Get object of a class above
GM = GreenMask()
rospy.spin()

destroyAllWindows()
