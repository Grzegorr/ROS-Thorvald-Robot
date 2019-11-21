#!/usr/bin/env python  
import rospy
#import math
import tf
import geometry_msgs.msg
#from math import atan2, pi
#This function puts the scan frame of reference into odometry frame(middle of the room)
if __name__ == '__main__':
    rospy.init_node('scan_to_odom_tf')
    listener = tf.TransformListener()
    pose_pub = rospy.Publisher('pose', geometry_msgs.msg.PoseStamped, queue_size=1)
    rate = rospy.Rate(10.0)
    
    while not rospy.is_shutdown():

        try:
            # look up the transform, i.e., get the transform from 2nd argument to 1st. 
            # This transform will allow us to transfer 
            (trans, rot) = listener.lookupTransform("thorvald_001/odom", "thorvald_001/kinect2_depth_optical_frame", rospy.Time())
            
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rate.sleep()
            continue
        
        # This is a point at the orgin of scan frame. This will be transformed to odometry frame.
        p1 = geometry_msgs.msg.PoseStamped()
        p1.header.frame_id = "thorvald_001/kinect2_depth_optical_frame"
        p1.pose.orientation.w = 1.0  # Neutral orientation 
        p1.pose.position.z = 0
        # we publish this so we can see it in rviz:   
        pose_pub.publish(p1)

        # here we directly transform the pose into another pose for the given frame of reference:
        p_in_odom = listener.transformPose("thorvald_001/odom", p1)
        print ("Position of the object in the odometry frame of reference:")
        print (p_in_odom)
        
        rate.sleep()
