#!/usr/bin/env python
#This function puts the any frame of reference into odometry frame(middle of the room)
import rospy
#import math
import tf
import geometry_msgs.msg
#from math import atan2, pi

class TF:
    def __init__(self):
        #subscribes to a topic with a pose, which is to be transformed
        rospy.Subscriber('laser_closest_pose', geometry_msgs.msg.PoseStamped, self.callback)
        #publisher to publish this pose
        self.publisher = rospy.Publisher('odom_pose', geometry_msgs.msg.PoseStamped, queue_size=1)
        #transform listener which looks up a transform
        self.listener = tf.TransformListener()
    
    def callback(self,  data):
        
        # This transform will allow us to transfer 
        (trans, rot) = self.listener.lookupTransform("thorvald_001/odom", data.header.frame_id, rospy.Time())
        
        # This is a point at the orgin of scan frame. This will be transformed to odometry frame.
        p1 = data

        # here we directly transform the pose into another pose for the given frame of reference:
        p_in_odom = self.listener.transformPose("thorvald_001/odom", p1)
        print ("Position of the object in the odometry frame of reference:")
        print (p_in_odom)
        
        #publish pose on a topic
        self.publisher.publish(p_in_odom)

        
if __name__ == '__main__':
    rospy.init_node('any_to_odom_tf')
    TF()
    rospy.spin()
