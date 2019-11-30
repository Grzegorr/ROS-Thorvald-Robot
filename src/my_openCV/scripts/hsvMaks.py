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

    def __init__(self):
        #initialize CV Bridge, this links ROS and OpenCV picture formats
        self.bridge = CvBridge()
        self.publisher = rospy.Publisher("/thorvald_001/green_masked_camera",  Image,  queue_size = 1)
        #Subscribe to an topica carring an image
        self.image_sub = rospy.Subscriber("/thorvald_001/kinect2_camera/hd/image_color_rect", Image, self.callback)
    
##    #Makes a mask which removes pixels with red above threshold
##    def highRedRemoval(self,  image, threshold,  ifOpenWindow,  filtNum):
##        #boundries for a mask in BGR format
##        lower = numpy.array([0,  30, threshold],  dtype = "uint8")
##        upper = numpy.array([255,  255,  255],  dtype = "uint8")
##        #making a mask argumets are in BGR format
##        image = cv2.blur(image, (10, 10))
##        output = self.maskAfterContrasts(image, lower, upper,  "True", 43)
##        if (ifOpenWindow == "True"):
##            namedWindow("highRedRemoval" + str(filtNum))
##            cv2.imshow("highRedRemoval" + str(filtNum), output)
##
##    def maskAfterContrasts(self, cv_image, lower,  upper, ifOpenWindow,  filtNum):
##        lower = numpy.array(lower,  dtype = "uint8")
##        upper = numpy.array(upper,  dtype = "uint8")
##        b, g, r = cv2.split(cv_image)
##        g_contrast = cv2.equalizeHist(g)
##        r_contrast = cv2.equalizeHist(r)
##        b_contrast = cv2.equalizeHist(b)
##        image = cv2.merge([b_contrast, g_contrast, r_contrast])
##        mask_img = cv2.inRange(image, lower, upper)
##        if (ifOpenWindow == "True"):
##            namedWindow("Specific Mask " + str(filtNum))
##            cv2.imshow("Specific Mask " + str(filtNum), mask_img)
##        return mask_img
##        
##    def mask(self, cv_image, lower,  upper, ifOpenWindow,  filtNum):
##        lower = numpy.array(lower,  dtype = "uint8")
##        upper = numpy.array(upper,  dtype = "uint8")
##        mask_img = cv2.inRange(cv_image, lower, upper)
##        if (ifOpenWindow == "True"):
##            namedWindow("Specific Mask " + str(filtNum))
##            cv2.imshow("Specific Mask " + str(filtNum), mask_img)
##        return mask_img
##        
##            
##    def dilute(self, int, image, ifOpenWindow,  filtNum):
##        kernel = numpy.ones((int,int),numpy.uint8)
##        image = cv2.dilate(image,kernel,iterations = 1)
##        if (ifOpenWindow == "True"):
##            namedWindow("Dilution " + str(filtNum))
##            cv2.imshow("Dilution " + str(filtNum), image)
##        return image
##        
##    def erode(self, int, image, ifOpenWindow,  filtNum):
##        kernel = numpy.ones((int,int),numpy.uint8)
##        image = cv2.erode(image,kernel,iterations = 1)
##        if (ifOpenWindow == "True"):
##            namedWindow("Erode " + str(filtNum))
##            cv2.imshow("Erode " + str(filtNum), image)
##        return image
##    
##    def youngSaladDetection(self,  cv_image):
##        #image = cv2.blur(image,  (80, 80))
##        image = self.maskAfterContrasts(cv_image, [0, 180, 0], [100, 255, 150], "True", 1)
##        image = self.erode(5, image, "False",  1)
##        image = self.dilute(11, image, "False",  1)
##        image = self.dilute(11, image, "False",  2)
##        image = self.dilute(11, image, "False",  3)
##        image = self.dilute(40, image, "True",  3)
##        image = self.erode(20, image, "True",  3)
##        return image
##        
##    def youngSaladWhereToSpray(self, image, filtNum, ifOpenWindow):
##        saladMask = self.youngSaladDetection(image)
##        #Revert that mask
##        saladMask = cv2.bitwise_not(saladMask)
##        greenMask = self.allGreenDetection(image)
##        weedMask = cv2.bitwise_and(saladMask, greenMask, saladMask )
##        if (ifOpenWindow == "True"):
##            namedWindow("Weeds " + str(filtNum))
##            cv2.imshow("Weeds " + str(filtNum), weedMask)
##
##    
##    def allGreenDetection(self,  cv_image):
##        return self.maskAfterContrasts(cv_image, [0, 100, 0], [100, 255, 180], "True", 99)
##    
##
##        
    def callback(self, data): 
        #transfer image from ROS file system to openCV file
        cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        self.youngLetticeDetection(cv_image)
    
    def youngLetticeDetection(self, cv_image):
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
        
    #For diagnosic reasonsonly
        h, s, v = cv2.split(hsv_image)
        namedWindow("H")
        cv2.imshow("H",  h)
        namedWindow("S")
        cv2.imshow("S",  s)
        namedWindow("V")
        cv2.imshow("V",  v)
        
    def grownLetticeDetection(self, cv_image):
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
        
    #For diagnosic reasonsonly
        h, s, v = cv2.split(hsv_image)
        namedWindow("H")
        cv2.imshow("H",  h)
        namedWindow("S")
        cv2.imshow("S",  s)
        namedWindow("V")
        cv2.imshow("V",  v)
##        
##        
##        
##        
##        namedWindow("Image window")
##        imshow("Image window", cv_image)
##
##
##        #cv_image = cv2.blur(cv_image,  (40, 40))
##        self.youngSaladWhereToSpray(cv_image, 55, "True")
##
##        #RGB split
##        b, g, r = cv2.split(cv_image)
##        namedWindow("green")
##        cv2.imshow('green', g)
##        namedWindow("blue")
##        cv2.imshow("blue", b)
##        namedWindow("red")
##        cv2.imshow("red", r)
###        
##        #        #Contrast Increases
##        g_contrast = cv2.equalizeHist(g)
##        namedWindow("g_contrast")
##        cv2.imshow("g_contrast", g_contrast)
##        
##        r_contrast = cv2.equalizeHist(r)
##        namedWindow("r_contrast")
##        cv2.imshow("r_contrast", r_contrast)
##        
##        b_contrast = cv2.equalizeHist(b)
##        namedWindow("b_contrast")
##        cv2.imshow("b_contrast", b_contrast)
##        
##
##
##        #self.maskAfterContrasts(cv_image, [20, 0, 20], [100,  255, 100], "True", 100)
###        
###        #self.maskAfterContrasts(cv_image, [0, 180, 0], [100, 255, 100], "True", 1)
###        #self.maskAfterContrasts(cv_image, [0, 180, 0], [255, 255, 100], "True", 2)
###        
##
###        
###        green_contrasted = cv2.merge([b, g_contrast, r])
###        namedWindow("green_contrasted ")
###        cv2.imshow("green_contrasted ", green_contrasted )
###        
###        redgreen_contrasted = cv2.merge([b, g_contrast, r_contrast])
###        namedWindow("redgreen_contrasted ")
###        cv2.imshow("redgreen_contrasted ", redgreen_contrasted )
###        
##        self.highRedRemoval(cv_image, 10, "True", 1)
##        self.highRedRemoval(cv_image, 20, "True", 2)
##        self.highRedRemoval(cv_image, 25, "True", 3)
##        self.highRedRemoval(cv_image, 30, "True", 4)
##        self.highRedRemoval(cv_image, 220, "True", 5)
##        self.highRedRemoval(cv_image, 240, "True", 6)
###        
###        
###        #boundries for a mask in BGR format
###        lower = numpy.array([0,  180, 0],  dtype = "uint8")
###        upper = numpy.array([255,  255,  60],  dtype = "uint8")
###        #making a mask argumets are in BGR format
###        mask_img = cv2.inRange(redgreen_contrasted, lower, upper)
###        #kernel = numpy.ones((5,5),numpy.uint8)
###        #mask_img = cv2.morphologyEx(mask_img, cv2.MORPH_CLOSE, kernel)
###        namedWindow("mask_before_blur")
###        imshow("mask_before_blur",  mask_img)
###        mask_img = cv2.medianBlur(mask_img,7)
###        #mask the image
###        masked_img = cv2.bitwise_and(cv_image, cv_image , mask=mask_img)
###        #Display images
##       # imshow("Image window", cv_image)
###        imshow("mask",  mask_img)
###        imshow("masked", masked_img)
###        
###        
###        
###        
###        
###        
####        #Increased Contrast
####        bgr = cv_image
####        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)  
####        lab_planes = cv2.split(lab)
####        clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8, 8))
####        lab_planes[0] = clahe.apply(lab_planes[0])
####        lab = cv2.merge(lab_planes)
####        bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
####        namedWindow("bgr")
####        cv2.imshow("bgr", bgr)
####        cv_image = bgr
###        
###        
###        
###        #convert picture back to ROS, so it is can be published on a topic
###        image_message = self.bridge.cv2_to_imgmsg(masked_img, encoding="passthrough")
###        self.publisher.publish(image_message)
        waitKey(1)

startWindowThread()
#init a node
rospy.init_node('hsv_mask')
#Get object of a class above
GM = GreenMask()
rospy.spin()

destroyAllWindows()
