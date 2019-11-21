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
   

    def callback(self, data):
        #Create windows with names
        namedWindow("Image window")
        namedWindow("mask")
        namedWindow("masked")
        #transfer image from ROS file system to openCV file
        cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        
        #boundries for a mask in BGR format
        lower = numpy.array([0,  50, 0],  dtype = "uint8")
        upper = numpy.array([100,  255,  100],  dtype = "uint8")
        #making a mask argumets are in BGR format
        mask_img = cv2.inRange(cv_image, lower, upper)
        #mask the image
        masked_img = cv2.bitwise_and(cv_image, cv_image , mask=mask_img)
        #Display images
        imshow("Image window", cv_image)
        imshow("mask",  mask_img)
        imshow("masked", masked_img)
        #convert picture back to ROS, so it is can be published on a topic
        image_message = self.bridge.cv2_to_imgmsg(masked_img, encoding="passthrough")
        self.publisher.publish(image_message)
        waitKey(1)

startWindowThread()
#init a node
rospy.init_node('green_mask')
#Get object of a class above
GM = GreenMask()
rospy.spin()

destroyAllWindows()
