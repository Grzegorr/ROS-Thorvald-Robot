#!/usr/bin/env python
import rospy
import std_msgs.msg
from sensor_msgs.msg import Image
from sensor_msgs.msg import PointCloud
from geometry_msgs.msg import Point32
from geometry_msgs.msg import Transform
from cv_bridge import CvBridge
import cv2
import numpy
import math
import tf

class GreenMask:
    detectionMode = "OFF"
    
    #init CV bridge, subscribers, publishers
    def __init__(self):
        #initialize CV Bridge, this links ROS and OpenCV picture formats
        self.bridge = CvBridge()
        #publisher for the mask if needed
        #self.publisher = rospy.Publisher("/thorvald_001/green_masked_camera",  Image,  queue_size = 1)
        #publisher for transform computed at time of capturing a frame
        self.transPub = rospy.Publisher("/thorvald_001/capture_time_transform",  Transform,  queue_size = 1,  latch='true')
        #publisher for pointcloud
        self.pcPub = rospy.Publisher("/thorvald_001/last_frame_points",  PointCloud,  queue_size = 1,  latch='true')
        #Subscribe to an topica carring an image
        self.image_sub = rospy.Subscriber("/thorvald_001/kinect2_camera/hd/image_color_rect", Image, self.callback)
        #Subscribe to a camera mode topic
        self.camera_sub = rospy.Subscriber("/camera_mode", std_msgs.msg.String, self.callback2)
        #tf listener
        self.tfListener = tf.TransformListener()
    
    
    #callback to handle next frame
    def callback(self, data):
        #Get last frame timestamp
        self.last_frame_stamp = data.header.stamp
        #try to lookup transform to "map" frame at a tome of picture captue, if cant drop the frame
        try:
            (trans,  rot) = self.tfListener.lookupTransform('thorvald_001/kinect2_rgb_optical_frame',  "map", self.last_frame_stamp)
        except (tf.ExtrapolationException):
            print("Frame droped due to unknown tf at time of picture timestamp.")
            return
        #publish transform
        transform_to_send = Transform()
        transform_to_send.translation.x = trans[0]
        transform_to_send.translation.y = trans[1]
        transform_to_send.translation.z = trans[2]
        transform_to_send.rotation.x = rot[0]
        transform_to_send.rotation.y = rot[1]
        transform_to_send.rotation.z = rot[2]
        transform_to_send.rotation.w = rot[3]
        self.transPub.publish(transform_to_send)
        #transfer image from ROS file system to openCV file
        cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        if self.detectionMode == "Young Lettice":
            self.detectionYoungLettice(cv_image)
        if self.detectionMode == "Grown Lettice":
            self.detectionGrownLettice(cv_image)
        if self.detectionMode == "Anion":
            self.detectionAnion(cv_image)
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

    
    #detection for first two rows from the left
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
    
        #Boundries and masking for cabbage only
        lower_cabbage = numpy.array([35,120,20])
        upper_cabbage = numpy.array([65,255,255])
        cabbageMask = cv2.inRange(hsv_image, lower_cabbage, upper_cabbage)
    
        #Dilaute to make safe zone for lettice
        kernel = numpy.ones((5,5),numpy.uint8)
        cabbageMask = cv2.dilate(cabbageMask,kernel,iterations = 3)
    
        #This is just for storing and output for now
        weedMask = allGreenMask
        #Do logic on mask and display final mask
        cabbageMask = cv2.bitwise_not(cabbageMask)
        cv2.bitwise_and(cabbageMask, allGreenMask, weedMask )
        kernel = numpy.ones((3,3),numpy.uint8)
        weedMask = cv2.erode(weedMask,kernel,iterations =1)
        weedMask = cv2.dilate(weedMask,kernel,iterations =2)
    
        #Colour masked areas red
        indices = numpy.where(weedMask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        
        #convert mask to pointcloud and display results
        self.whereToSpray(weedMask, cv_image)
        
    
    #runs blob detection on the mask
    def whereToSpray(self, final_mask, final_image):    
        # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()
        # Filter by colour.
        params.filterByColor = True
        params.blobColor = 255
        # Filter by Area.
        params.filterByArea = True
        params.minArea = 200
        # Filter by Circularity
        params.filterByCircularity = False
        # Filter by Convexity
        params.filterByConvexity = False
        # Filter by Inertia
        params.filterByInertia = False
        # Set up the detector with new parameters
        detector = cv2.SimpleBlobDetector_create(params)
 
        # Detect blobs.
        keypoints = detector.detect(final_mask)
        #print(keypoints[0])
        points	=	cv2.KeyPoint_convert(keypoints)
        #These will be points with int values
        publishable_points = []
        for point in points:
            x = int(point[0])
            y = int(point[1])
            publishable_points.append([x, y])
            final_image	=	cv2.circle(final_image, (x, y), 10,(200, 0, 200),  thickness = -1)
        cv2.imshow("Final Output. Red - weed belief mask, purple - points to spray.",  final_image)
        self.publishPointCloud(publishable_points)
        
    #construct and publish the point cloud
    def publishPointCloud(self, points):
        points2 = []
        for point in points:
            #convert from pixel number to meters
            x = point[0]
            y = point[1]
            x = (x - 990)*0.00044
            y = (y - 540)*0.00044
            dummy = Point32()
            dummy.x = x
            dummy.y = y
            dummy.z = 0.5
            points2.append(dummy)
        
        if len(points) !=0:
            pc = PointCloud()
            pc.header.stamp = self.last_frame_stamp
            pc.header.frame_id = "thorvald_001/kinect2_rgb_optical_frame"
            pc.points = points2
            self.pcPub.publish(pc)
        
  
    #detection algorithm for two rows on the left of the map
    def detectionAnion(self,  cv_image):
        #blur and convert to hsv colour space
        cv_image = cv2.blur(cv_image,  (5, 5))
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        
        #mask for color removing some weeds
        lower_green = numpy.array([30,20,20])
        upper_green = numpy.array([50,255,255])
        colour_removed_weed = cv2.inRange(hsv_image, lower_green, upper_green)
        kernel = numpy.ones((5,5),numpy.uint8)
        colour_removed_weed = cv2.dilate(colour_removed_weed,kernel,iterations = 1)
        colour_removed_weed = cv2.erode(colour_removed_weed,kernel,iterations = 3)
        
        #mask for green, but leaving out some weeds which can be colour separated with block of code above
        lower_green = numpy.array([50,20,20])
        upper_green = numpy.array([200,100,255])
        selectiveGreenMask = cv2.inRange(hsv_image, lower_green, upper_green)
        

        #Detect very long lines and draw first of them with a large thickness
        lines = cv2.HoughLines(selectiveGreenMask, 1 , numpy.pi / 180, 900, 0, 0, 0, 0.2)    
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
                cv2.line(selectiveGreenMask, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
                cv2.line(colour_removed_weed, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
        else:
            #probably just getting on the field so drop the frame(detection would not work properly)
            print("Weed Detection: 1st row of anions was not found. Probably entering the field, no weeds will be detected.")
            cv2.imshow("Final Output. Red - weed belief mask, purple - points to spray.",  cv_image)
            return
        
        #same operation with hough line detection for 2nd row
        lines = cv2.HoughLines(selectiveGreenMask, 1 , numpy.pi / 180, 800, 0, 0, 0, 0.2)
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
                cv2.line(selectiveGreenMask, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
                cv2.line(colour_removed_weed, pt1, pt2, (0,0,0), 250, cv2.LINE_AA)
        else:
            #probably just getting on the field so drop the frame(detection would not work properly)
            print("Weed Detection: 2nd row of anions was not found. Probably entering the field, no weeds will be detected.")
            cv2.imshow("Final Output. Red - weed belief mask, purple - points to spray.",  cv_image)
            return
        
        #get rid of some noise
        kernel = numpy.ones((5,5),numpy.uint8)
        selectiveGreenMask = cv2.erode(selectiveGreenMask,kernel,iterations = 1)
        selectiveGreenMask = cv2.dilate(selectiveGreenMask,kernel,iterations = 1)
        
        #erosion in horizontal direction only to save anions going verticalt-ish out of the rows
        kernel2 = numpy.array([[0, 0, 0, 0, 0, 0, 0], 
                        [0, 0, 0, 0, 0, 0, 0], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [0, 0, 0, 0, 0, 0, 0], 
                        [0, 0, 0, 0, 0, 0, 0]], dtype = numpy.uint8)
        selectiveGreenMask = cv2.erode(selectiveGreenMask,kernel2,iterations = 3)

        
        #just making an array for new masks
        ultimate_mask = colour_removed_weed
        cv2.bitwise_or(colour_removed_weed, selectiveGreenMask , ultimate_mask)
        indices = numpy.where(ultimate_mask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
        
        #blob detection on the resulting mask
        self.whereToSpray(ultimate_mask, cv_image)
    
    def detectionGrownLettice(self,  cv_image):
        #Bluring the image
        cv_image = cv2.blur(cv_image,  (5, 5))
        #changing to HSV colourspace
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    
        #detecting all plants as green colour
        lower_green = numpy.array([35,20,20])
        upper_green = numpy.array([65,255,255])
        allGreenMask = cv2.inRange(hsv_image, lower_green, upper_green)
    
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
    
        #This is just for storing and output for now
        weedMask = allGreenMask
        #Do logic on mask and display final mask
        cabbageMask = cv2.bitwise_not(cabbageMask)
        cv2.bitwise_and(cabbageMask, allGreenMask, weedMask )
        kernel = numpy.ones((3,3),numpy.uint8)
        weedMask = cv2.erode(weedMask,kernel,iterations =1)
        weedMask = cv2.dilate(weedMask,kernel,iterations =2)
    
        #Colour masked areas red
        indices = numpy.where(weedMask==255)
        cv_image[indices[0], indices[1], :] = [0, 0, 255]
    
        self.whereToSpray(weedMask,  cv_image)

if __name__ == '__main__':
    #init a node
    rospy.init_node('weed_detection')
    #Get object of a class above
    GM = GreenMask()
    rospy.spin()
    
    cv2.destroyAllWindows()
