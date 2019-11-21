#!/usr/bin/env python
#This function is publishing PoseStamped type messages 
import rospy
#import math
#import tf
import geometry_msgs.msg
import move_base_msgs.msg
#import std_msgs.msg
#from math import atan2, pi

class Controller:
    
    def __init__(self):
        #publisher to publish this pose
        self.publisher = rospy.Publisher('/move_base/goal', move_base_msgs.msg.MoveBaseActionGoal, queue_size=1,  latch='true')
       ##Listener for the current pose
        ##rospy.Subscriber('/amcl_pose',  geometry_msgs.msg.PoseStamped, self.callback)
    
    def publishGoal(self, x, y, z, ortx, orty, ortz, ortw):
        
        goal = move_base_msgs.msg.MoveBaseActionGoal()
        
        goal.header.seq = 1
        goal.header.stamp = rospy.Time.now()
        goal.header.frame_id = "map"
        
        goal.goal_id.stamp = rospy.Time.now()
        goal.goal_id.id = "Goal 1"
        
        #Making a pose to publish(Goal)
        p1 = geometry_msgs.msg.PoseStamped()
        p1.header.frame_id = "map"    
        p1.header.stamp = rospy.Time.now()
        p1.pose.position.x = x
        p1.pose.position.y = y
        p1.pose.position.z = z
        p1.pose.orientation.x = ortx
        p1.pose.orientation.y = orty
        p1.pose.orientation.z = ortz
        p1.pose.orientation.w = ortw
        
        goal.goal.target_pose = p1

        self.publisher.publish(goal)

    def callback(self,  data):
        self.current_pose = data
        
if __name__ == '__main__':
    rospy.init_node('path_controller')
    C = Controller()
    C.publishGoal(0, 0, 0, 0, 0, 0, 1)
    rospy.spin()
