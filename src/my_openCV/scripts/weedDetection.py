#!/usr/bin/env python
import rospy
import std_msgs.msg
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy
import math

class GreenMask:
    detectionMode = "OFF"
    
    #init CV bridge, subscribers, publishers
    def __init__(self):
        #initialize CV Bridge, this links ROS and OpenCV picture formats
        self.bridge = CvBridge()
        self.publisher = rospy.Publisher("/thorvald_001/green_masked_camera",  Image,  queue_size = 1)
        #Subscribe to an topica carring an image
        self.image_sub = rospy.Subscriber("/thorvald_001/kinect2_camera/hd/image_color_rect", Image, self.callback)
        #Subscribe to a camera mode topic
        self.camera_sub = rospy.Subscriber("/camera_mode", std_msgs.msg.String, self.callback2)
    
    #callback to handle next frame
    def callback(self, data):
        #transfer image from ROS file system to openCV file
        cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        if self.detectionMode == "Young Lettice":
            self.detectionYoungLettice(cv_image)
        if self.detectionMode == "Grown Lettice":
            self.detectionGrownLettice(cv_image)
        if self.detectionMode == "Anion":
            self.theMonsterBookOfMonsters(cv_image)
        if self.detectionMode == "OFF":
            self.OFF(cv_image)
        cv2.waitKey(1)
    
    #Callback to handle change of detection mode
    def callback2(self, data):
        if data.data != self.detectionMode:
            print(data)
            cv2.destroyAllWindows()
            self.detectionMode = data.data
     
    #Just showing original image when detection is off
    def OFF(self, cv_image):
        cv2.imshow("Original - detection OFF",  cv_image)

    
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
#        cv2.namedWindow("HSVgreen")
#        cv2.imshow("HSVgreen",  allGreenMask)
    
        #Boundries and masking for cabbage only
        lower_cabbage = numpy.array([35,120,20])
        upper_cabbage = numpy.array([65,255,255])
        cabbageMask = cv2.inRange(hsv_image, lower_cabbage, upper_cabbage)
    
        #Dilaute to make safe zone for lettice
        kernel = numpy.ones((5,5),numpy.uint8)
        cabbageMask = cv2.dilate(cabbageMask,kernel,iterations = 3)
        #Display the mask if wanted
#        cv2.namedWindow("HSVcabbage")
#        cv2.imshow("HSVcabbage",  cabbageMask)
        
        #Display original image
#        cv2.namedWindow("Original")
#        cv2.imshow("Original",  cv_image)
    
        #This is just for storing and output for now
        weedMask = allGreenMask
        #Do logic on mask and display final mask
        cabbageMask = cv2.bitwise_not(cabbageMask)
        cv2.bitwise_and(cabbageMask, allGreenMask, weedMask )
        kernel = numpy.ones((3,3),numpy.uint8)
        weedMask = cv2.erode(weedMask,kernel,iterations =1)
        weedMask = cv2.dilate(weedMask,kernel,iterations =2)
#        cv2.namedWindow("weedMask")
#        cv2.imshow("weedMask",  weedMask)
    
        #Colour masked areas red
        indices = numpy.where(weedMask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        cv2.namedWindow("FinalOutput")
        cv2.imshow("FinalOutput",  cv_image)
        
        
        # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()
         
#        # Change thresholds
#        params.minThreshold = 10;
#        params.maxThreshold = 200;
        
        # Filter by colour.
        params.filterByColor = True
        params.blobColor = 255
        
        # Filter by Area.
        params.filterByArea = True
        params.minArea = 200
         
        # Filter by Circularity
        params.filterByCircularity = False
        params.minCircularity = 0.1
         
        # Filter by Convexity
        params.filterByConvexity = False
        params.minConvexity = 0.87
         
        # Filter by Inertia
        params.filterByInertia = False
        params.minInertiaRatio = 0.01
        # Set up the detector with default parameters.
        detector = cv2.SimpleBlobDetector_create(params)
 
        # Detect blobs.
        keypoints = detector.detect(weedMask)
        #print(keypoints[0])
        points	=	cv2.KeyPoint_convert(keypoints)
        print(points[0])
        for point in points:
            x = int(point[0])
            y = int(point[1])
            cv_image	=	cv2.circle(cv_image, (x, y), 10,(150, 0, 150),  thickness = -1)
        cv2.imshow("Blobs",  cv_image)
    

   
  
    def theMonsterBookOfMonsters(self,  cv_image):
        
        cv_image = cv2.blur(cv_image,  (5, 5))
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        cv2.imshow("Original",  cv_image)
        
        #Boundriec for removing some weeds
        lower_green = numpy.array([50,20,20])
        upper_green = numpy.array([200,100,255])
    
        #applaying the green mask for all plants
        allGreenMask = cv2.inRange(hsv_image, lower_green, upper_green)
        cv2.namedWindow("HSVgreen")
        cv2.imshow("HSVgreen",  allGreenMask)
        
        #colour removed weeds
        lower_green = numpy.array([30,20,20])
        upper_green = numpy.array([50,255,255])
        weed = cv2.inRange(hsv_image, lower_green, upper_green)
        kernel = numpy.ones((5,5),numpy.uint8)
        weed = cv2.dilate(weed,kernel,iterations = 1)
        kernel = numpy.ones((5,5),numpy.uint8)
        weed = cv2.erode(weed,kernel,iterations = 3)
        cv2.imshow("ColourRemovedWeeds",  weed)
        
        
        
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        lines = cv2.HoughLines(allGreenMask, 1 , numpy.pi / 180, 900, None, 0, 0)
        #print(len(lines))
    
        if lines is not None:
            print("Lines 2: " + str(len(lines)))
            for i in [0]:
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a * rho
                y0 = b * rho
                pt1 = (int(x0 + 2000*(-b)), int(y0 + 2000*(a)))
                pt2 = (int(x0 - 2000*(-b)), int(y0 - 2000*(a)))
                cv2.line(allGreenMask, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
                cv2.line(gray, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
                cv2.line(weed, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
                
        lines = cv2.HoughLines(allGreenMask, 1 , numpy.pi / 180, 800, None, 0, 0)
        
    
        if lines is not None:
            for i in [0]:
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a * rho
                y0 = b * rho
                pt1 = (int(x0 + 2000*(-b)), int(y0 + 2000*(a)))
                pt2 = (int(x0 - 2000*(-b)), int(y0 - 2000*(a)))
                cv2.line(allGreenMask, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
                cv2.line(gray, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
                cv2.line(weed, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
        cv2.imshow("Line",  gray)
        
        kernel = numpy.ones((5,5),numpy.uint8)
        allGreenMask = cv2.erode(allGreenMask,kernel,iterations = 1)
        allGreenMask = cv2.dilate(allGreenMask,kernel,iterations = 1)
        
        
        cv2.imshow("New Green Mask", allGreenMask)
        
        masked_img = cv2.bitwise_and(cv_image, cv_image , mask=allGreenMask)
        cv2.imshow("Masked", masked_img)
        
        kernel2 = numpy.array([[0, 0, 0, 0, 0, 0, 0], 
                        [0, 0, 0, 0, 0, 0, 0], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [0, 0, 0, 0, 0, 0, 0], 
                        [0, 0, 0, 0, 0, 0, 0]], dtype = numpy.uint8)

        allGreenMask = cv2.erode(allGreenMask,kernel2,iterations = 3)
        cv2.imshow("Newest Green Mask", allGreenMask)
        
        #just making an array for new masks
        ultimate_mask = weed
        cv2.bitwise_or(weed, allGreenMask , ultimate_mask)
        indices = numpy.where(ultimate_mask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        cv2.namedWindow("FinalOutput")
        cv2.imshow("FinalOutput",  cv_image)
        #
        #
        
        
#         #BGR space
#        b, g, r = cv2.split(masked_img)
#        cv2.namedWindow("green")
#        cv2.imshow('green', g)
#        cv2.namedWindow("blue")
#        cv2.imshow("blue", b)
#        cv2.namedWindow("red")
#        cv2.imshow("red", r)
#        
        #HSV space
        #hsv_image = cv2.cvtColor(masked_img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        cv2.namedWindow("H")
        cv2.imshow("H",  h)
        cv2.namedWindow("S")
        cv2.imshow("S",  s)
        cv2.namedWindow("V")
        cv2.imshow("V",  v)
#        
#        #LAB space
#        lab_image = cv2.cvtColor(masked_img, cv2.COLOR_BGR2LAB)
#        l, a, b = cv2.split(lab_image)
#        cv2.namedWindow("L(lab)")
#        cv2.imshow("L(lab)",  l)
#        cv2.namedWindow("A(lab)")
#        cv2.imshow("A(lab)",  a)
#        cv2.namedWindow("B(lab)")
#        cv2.imshow("B(lab)",  b)
#        #Template Matching
#        path = os.path.dirname(os.path.abspath(__file__))
#        print(path)
#        template = cv2.imread(path + '/temp4.png',cv2.IMREAD_COLOR)
#        #cv2.imshow("Template", template)
#        template_shape = template.shape
#        #template = template.astype(numpy.uint8)
#        h,  w = (template_shape[0], template_shape[1])
#        image_for_matching = cv_image.copy()
#    
#        # Apply template Matching
#        res = cv2.matchTemplate(masked_img,template,cv2.TM_CCOEFF_NORMED)
#        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#        top_left = min_loc
#        bottom_right = (top_left[0] + w, top_left[1] + h)
#        cv2.rectangle(image_for_matching,top_left, bottom_right, 255, 2)
#    
#        cv2.imshow("Matching", image_for_matching)
        
    
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
#        cv2.namedWindow("HSVgreen")
#        cv2.imshow("HSVgreen",  allGreenMask)
    
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
#        cv2.namedWindow("HSVcabbage")
#        cv2.imshow("HSVcabbage",  cabbageMask)
    
        #Display original image
#        cv2.namedWindow("Original")
#        cv2.imshow("Original",  cv_image)
    
        #This is just for storing and output for now
        weedMask = allGreenMask
        #Do logic on mask and display final mask
        cabbageMask = cv2.bitwise_not(cabbageMask)
        cv2.bitwise_and(cabbageMask, allGreenMask, weedMask )
        kernel = numpy.ones((3,3),numpy.uint8)
        weedMask = cv2.erode(weedMask,kernel,iterations =1)
        weedMask = cv2.dilate(weedMask,kernel,iterations =2)
#        cv2.namedWindow("weedMask")
#        cv2.imshow("weedMask",  weedMask)
    
        #Colour masked areas red
        indices = numpy.where(weedMask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        cv2.namedWindow("FinalOutput")
        cv2.imshow("FinalOutput",  cv_image)
    
        #For diagnosic reasons only
        h, s, v = cv2.split(hsv_image)


if __name__ == '__main__':
    #init a node
    rospy.init_node('weedDetection')
    #Get object of a class above
    GM = GreenMask()
    rospy.spin()
    
    cv2.destroyAllWindows()
