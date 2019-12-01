#!/usr/bin/env python
import rospy
import std_msgs.msg
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy

class GreenMask:
    detectionMode = "Superpixels"

    def __init__(self):
        #initialize CV Bridge, this links ROS and OpenCV picture formats
        self.bridge = CvBridge()
        self.publisher = rospy.Publisher("/thorvald_001/green_masked_camera",  Image,  queue_size = 1)
        #Subscribe to an topica carring an image
        self.image_sub = rospy.Subscriber("/thorvald_001/kinect2_camera/hd/image_color_rect", Image, self.callback)
        #Subscribe to a camera mode topic
        self.camera_sub = rospy.Subscriber("/camera_mode", std_msgs.msg.String, self.callback2)
      
    def callback(self, data):
        #transfer image from ROS file system to openCV file
        cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        if self.detectionMode == "Diagnostics":
            self.diagnostics(cv_image)
        if self.detectionMode == "Young Lettice":
            self.detectionYoungLettice(cv_image)
        if self.detectionMode == "Grown Lettice":
            self.detectionGrownLettice(cv_image)
        if self.detectionMode == "Anion":
            self.detectionAnions(cv_image)
        if self.detectionMode == "Superpixels":
            self.superpixelsAnions(cv_image)
        if self.detectionMode == "OFF":
            self.OFF(cv_image)
        cv2.waitKey(1)
    
    def callback2(self, data):
        if data.data != self.detectionMode:
            print(data)
            cv2.destroyAllWindows()
            self.detectionMode = data.data
            
    
        
    def OFF(self, cv_image):
        cv2.namedWindow("Original")
        cv2.imshow("Original",  cv_image)
        
    def superpixelsAnions(self, cv_image):
#        pxl = cv2.ximgproc.createSuperpixelLSC(cv_image, 100, 0.1)
#        cv_image	=	pxl.getLabelContourMask(cv_image)
#        namedWindow("PXL")
#        cv2.imshow("PXL", cv_image)
        #Display original image
        cv2.namedWindow("Original")
        cv2.imshow("Original",  cv_image)

        canny_image = cv2.Canny(cv_image, 30,  30)
        cv2.namedWindow("Canny")
        cv2.imshow("Canny",  canny_image)
        
        
#        #lab_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
#        #pxl = cv2.ximgproc.createSuperpixelLSC(lab_image, 5, 0.1)
#        pxl = cv2.ximgproc.createSuperpixelLSC(canny_image, 10, 0.01)
#        pxl.iterate(4)
#        #pxl.enforceLabelConnectivity(3)
#        cv_image	=	pxl.getLabelContourMask()
#        namedWindow("PXL")
#        cv2.imshow("PXL", cv_image)
        
        
 
    def detectionAnions(self,  cv_image):
        #BGR space
        b, g, r = cv2.split(cv_image)
        cv2.namedWindow("green")
        cv2.imshow('green', g)
        cv2.namedWindow("blue")
        cv2.imshow("blue", b)
        cv2.namedWindow("red")
        cv2.imshow("red", r)
        
        #HSC space
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        cv2.namedWindow("H")
        cv2.imshow("H",  h)
        cv2.namedWindow("S")
        cv2.imshow("S",  s)
        cv2.namedWindow("V")
        cv2.imshow("V",  v)
        
        #LAB space
        lab_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab_image)
        cv2.namedWindow("L(lab)")
        cv2.imshow("L(lab)",  l)
        cv2.namedWindow("A(lab)")
        cv2.imshow("A(lab)",  a)
        cv2.namedWindow("B(lab)")
        cv2.imshow("B(lab)",  b)
        
        #cv_image = cv2.blur(cv_image,  (5, 5))
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        
        #Boundriec for detecting all plants as green colour
        lower_green = numpy.array([35,20,20])
        upper_green = numpy.array([200,255,255])
    
        #applaying the green mask for all plants
        allGreenMask = cv2.inRange(hsv_image, lower_green, upper_green)
        cv2.namedWindow("HSVgreen")
        cv2.imshow("HSVgreen",  allGreenMask)
    
        #Boundriec for detecting anion
        lower_anion = numpy.array([55,20,20])
        upper_anion = numpy.array([200,255,255])
    
        #applaying the anion mask
        anionMask = cv2.inRange(hsv_image, lower_anion, upper_anion)
        kernel = numpy.ones((5,5),numpy.uint8)
        anionMask = cv2.dilate(anionMask,kernel,iterations =1)
        cv2.namedWindow("HSVanion")
        cv2.imshow("HSVanion",  anionMask)
        
        #This is just for storing and output for now
        weedMask = allGreenMask
        #Do logic on mask and display final mask
        anionMask = cv2.bitwise_not(anionMask)
        cv2.bitwise_and(anionMask, allGreenMask, weedMask )
        kernel = numpy.ones((3,3),numpy.uint8)
        weedMask = cv2.erode(weedMask,kernel,iterations =1)
        cv2.namedWindow("weedMask")
        cv2.imshow("weedMask",  weedMask)
        
        #Display original image
        cv2.namedWindow("Original")
        cv2.imshow("Original",  cv_image)
        
        #Colour masked areas red
        indices = numpy.where(weedMask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        cv2.namedWindow("FinalOutput")
        cv2.imshow("FinalOutput",  cv_image)
        

        
        
    def diagnostics(self, cv_image):
        
        #BGR space
        b, g, r = cv2.split(cv_image)
        cv2.namedWindow("green")
        cv2.imshow('green', g)
        cv2.namedWindow("blue")
        cv2.imshow("blue", b)
        cv2.namedWindow("red")
        cv2.imshow("red", r)
        
        #HSC space
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        cv2.namedWindow("H")
        cv2.imshow("H",  h)
        cv2.namedWindow("S")
        cv2.imshow("S",  s)
        cv2.namedWindow("V")
        cv2.imshow("V",  v)
        
        #LAB space
        lab_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab_image)
        cv2.namedWindow("L(lab)")
        cv2.imshow("L(lab)",  l)
        cv2.namedWindow("A(lab)")
        cv2.imshow("A(lab)",  a)
        cv2.namedWindow("B(lab)")
        cv2.imshow("B(lab)",  b)
        
        #Edge detection
        canny_image = cv2.Canny(cv_image,  40,  100)
        cv2.namedWindow("Canny")
        cv2.imshow("Canny",  canny_image)
        
        
        
                #Display original image
        cv2.namedWindow("Original")
        cv2.imshow("Original",  cv_image)
        
        
        
        #Try Edge detector
        #kernel = numpy.ones((5,5),numpy.uint8)
        #canny_lines = cv2.dilate( canny_image, kernel)
        canny_lines = canny_image
        lines = cv2.HoughLinesP(canny_lines, 4, numpy.pi /180, 1500, None, 0, 0)
    
        if lines is not None:
            print(len(lines))
            for i in range(0, len(lines)):
                x1, y1, x2, y2 = lines[i][0]
                pt1 = (x1, y1)
                pt2 = (x2,  y2)
                cv2.line(cv_image, pt1, pt2, (0,0,255), 1, cv2.LINE_AA)
                
        
#        #FFT of Canny
#        f = numpy.fft.fft2(canny_image)
#        f_abs = numpy.abs(f)
#        f_mag = 20*numpy.log(f_abs)
#        fshift = numpy.fft.fftshift(f_mag)
#        rows = numpy.size(canny_image, 0) 
#        cols = numpy.size(canny_image, 1)
#        crow, ccol = rows/2, cols/2
#        
##        namedWindow("FFT")
##        cv2.imshow("FFT",  numpy.log10(f_abs))
##        print(numpy.log10(f_abs))
#        original = numpy.copy(canny_image)
#        fshift[crow-30:crow+30, ccol-30:ccol+30] = 0
#        f_ishift= numpy.fft.ifftshift(original - fshift)
#        img_back = numpy.fft.ifft2(f_ishift)
#        img_back = numpy.abs(img_back)
#        namedWindow("afterFFT")
#        cv2.imshow("afterFFT",  img_back)
        
        
        
        #Display original image
        cv2.namedWindow("Original2")
        cv2.imshow("Original2",  cv_image)
        
    def detectionYoungLettice(self,  cv_image): 
        #Bluring the image
        cv_image = cv2.blur(cv_image,  (5, 5))
        #changing to HSV colourspace
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    
        #Boundriec for detecting all plants as green colour
        lower_green = numpy.array([35,20,20])
        upper_green = numpy.array([200,255,255])
    
        #applaying the green mask for all plants
        allGreenMask = cv2.inRange(hsv_image, lower_green, upper_green)
        cv2.namedWindow("HSVgreen")
        cv2.imshow("HSVgreen",  allGreenMask)
    
        #Boundries and masking for cabbage only
        lower_cabbage = numpy.array([35,120,20])
        upper_cabbage = numpy.array([65,255,255])
        cabbageMask = cv2.inRange(hsv_image, lower_cabbage, upper_cabbage)
    
        #Dilaute to make safe zone for lettice
        kernel = numpy.ones((5,5),numpy.uint8)
        cabbageMask = cv2.dilate(cabbageMask,kernel,iterations = 3)
        #Display the mask if wanted
        cv2.namedWindow("HSVcabbage")
        cv2.imshow("HSVcabbage",  cabbageMask)
        
        #Display original image
        cv2.namedWindow("Original")
        cv2.imshow("Original",  cv_image)
    
        #This is just for storing and output for now
        weedMask = allGreenMask
        #Do logic on mask and display final mask
        cabbageMask = cv2.bitwise_not(cabbageMask)
        cv2.bitwise_and(cabbageMask, allGreenMask, weedMask )
        kernel = numpy.ones((3,3),numpy.uint8)
        weedMask = cv2.erode(weedMask,kernel,iterations =1)
        weedMask = cv2.dilate(weedMask,kernel,iterations =2)
        cv2.namedWindow("weedMask")
        cv2.imshow("weedMask",  weedMask)
    
        #Colour masked areas red
        indices = numpy.where(weedMask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        cv2.namedWindow("FinalOutput")
        cv2.imshow("FinalOutput",  cv_image)
    
        #For diagnosic reasons only
        h, s, v = cv2.split(hsv_image)
        cv2.namedWindow("H")
        cv2.imshow("H",  h)
        cv2.namedWindow("S")
        cv2.imshow("S",  s)
        cv2.namedWindow("V")
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
        cv2.namedWindow("HSVgreen")
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
        cv2.namedWindow("HSVcabbage")
        cv2.imshow("HSVcabbage",  cabbageMask)
    
        #Display original image
        cv2.namedWindow("Original")
        cv2.imshow("Original",  cv_image)
    
        #This is just for storing and output for now
        weedMask = allGreenMask
        #Do logic on mask and display final mask
        cabbageMask = cv2.bitwise_not(cabbageMask)
        cv2.bitwise_and(cabbageMask, allGreenMask, weedMask )
        kernel = numpy.ones((3,3),numpy.uint8)
        weedMask = cv2.erode(weedMask,kernel,iterations =1)
        weedMask = cv2.dilate(weedMask,kernel,iterations =2)
        cv2.namedWindow("weedMask")
        cv2.imshow("weedMask",  weedMask)
    
        #Colour masked areas red
        indices = numpy.where(weedMask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        cv2.namedWindow("FinalOutput")
        cv2.imshow("FinalOutput",  cv_image)
    
        #For diagnosic reasons only
        h, s, v = cv2.split(hsv_image)
        cv2.namedWindow("H")
        cv2.imshow("H",  h)
        cv2.namedWindow("S")
        cv2.imshow("S",  s)
        cv2.namedWindow("V")
        cv2.imshow("V",  v)

#startWindowThread()
#init a node
rospy.init_node('hsv_mask')
#Get object of a class above
GM = GreenMask()
rospy.spin()

cv2.destroyAllWindows()