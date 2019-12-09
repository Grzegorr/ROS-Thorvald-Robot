#!/usr/bin/env python
#This function is publishing PoseStamped type messages 
#import std_srvs
import rospy
#import math
#import tf
import numpy
import std_msgs.msg
import geometry_msgs.msg
import move_base_msgs.msg
#import std_msgs.msg
#from math import atan2, pi
#import rosservice

class Controller:
    
    #Path points, robot will go trough them in this order
    #They are arguments for publishGoal, look there for reference
    waypoints = [  ]
    
    def __init__(self,  path):
        #publisher to publish this pose
        self.publisher = rospy.Publisher('/move_base/goal', move_base_msgs.msg.MoveBaseActionGoal, queue_size=1,  latch='true')
        #publisher to publish camera mode
        self.publisher2 = rospy.Publisher('/camera_mode', std_msgs.msg.String, queue_size=1,  latch='true')
        #publisher to publish starting amcl pose to avoid amcl stuck with non-zero rotation in a square map
        amclPub = rospy.Publisher('/initialpose',  geometry_msgs.msg.PoseWithCovarianceStamped,  queue_size = 1,  latch = "true")
        amclPose = self.buildAMCLPose()
        amclPub.publish(amclPose)
        
        #Load waypoints depending on a rout cose by the user
        if path == "Test Path":
            self.waypoints = [  
            [5, 5, 0, 0, 0, 0, 1, "OFF"], 
            [5, -5, 0, 0, 0, 0, 1, "OFF"], 
            [-5, -5, 0, 0, 0, 0, 1, "OFF"], 
            [-5, 5, 0, 0, 0, 0, 1, "OFF"], 
            [0, 0, 0, 0, 0, 0, 1, "OFF"]
            ]
            
        if path == "Full_Path":
            self.waypoints = [  
            [7, 0, 0, 0, 0, 0, 1,  "OFF"], 
            [7, -3.75, 0, 0, 0, 1, 0,  "Young Lettice"],
            [2, -3.75, 0, 0, 0, 1, 0,  "NoChange"], 
            [-2, -3.75, 0, 0, 0, 1, 0,  "NoChange"], 
            [-7, -3.75, 0, 0, 0, 1, 0,  "OFF"], 
            [-7, -2.75, 0, 0, 0, 0, 1,  "Young Lettice"], 
            [-2, -2.75, 0, 0, 0, 0, 1,  "NoChange"],
            [2, -2.75, 0, 0, 0, 0, 1,  "NoChange"],
            [7, -2.75, 0, 0, 0, 0, 1,  "OFF"], 
            [7, -0.75, 0, 0, 0, 1, 0,  "Grown Lettice"], 
            [2, -0.75, 0, 0, 0, 1, 0,  "NoChange"],
            [-2, -0.75, 0, 0, 0, 1, 0,  "NoChange"],
            [-7, -0.75, 0, 0, 0, 1, 0,  "OFF"], 
            [-7, 0.25, 0, 0, 0, 0, 1,  "Grown Lettice"], 
            [-2, 0.25, 0, 0, 0, 0, 1,  "NoChange"],
            [2, 0.25, 0, 0, 0, 0, 1,  "NoChange"],
            [7, 0.25, 0, 0, 0, 0, 1,  "OFF"], 
            [7, 2.25, 0, 0, 0, 1, 0,  "Anion"], 
            [2, 2.25, 0, 0, 0, 1, 0,  "NoChange"], 
            [-2, 2.25, 0, 0, 0, 1, 0, "NoChange"], 
            [-7, 2.25, 0, 0, 0, 1, 0,  "OFF"], 
            [-7, 3.25, 0, 0, 0, 0, 1,  "Anion"], 
            [-2, 3.25, 0, 0, 0, 0, 1,  "NoChange"], 
            [2, 3.25, 0, 0, 0, 0, 1,  "NoChange"], 
            [7, 3.25, 0, 0, 0, 0, 1,  "OFF"]
            ]
            
        if path == "Young Salad Test":
            self.waypoints = [   
            [7, -3.75, 0, 0, 0, 1, 0, "OFF"], 
            [-7, -3.75, 0, 0, 0, 1, 0, "OFF"]
            ]
            
        if path == "Salad Test":
            self.waypoints = [   
            [-7, 0.25, 0, 0, 0, 0, 1, "OFF"], 
            [7, 0.25, 0, 0, 0, 0, 1, "OFF"]
            ]
        
        
        if path == "Onion Test":           
            self.waypoints = [   
            [7, -3.75, 0, 0, 0, 1, 0, "Anion"], 
            [-7, -3.75, 0, 0, 0, 1, 0,  "Anion"]
            ]
            
    
    #publishes subsequent waypoins and camera modes
    def driveAround(self):
        #Number of wypoints
        n = len(self.waypoints)
        print("Path Controller: There is " + str(n) + " waypoints in the programmed route.")
        for i in range(0, n):
            print(i)
            self.publishGoal(self.waypoints[i][0], self.waypoints[i][1], self.waypoints[i][2], self.waypoints[i][3], self.waypoints[i][4], self.waypoints[i][5], self.waypoints[i][6],  i)
            print("Path Controller: Waiting to reach the goal.")
            rospy.wait_for_message('/move_base/result', move_base_msgs.msg.MoveBaseActionResult)
            if self.waypoints[i][7] != "NoChange":
                self.publisher2.publish(self.waypoints[i][7])
            print("Path Controller: Goal reached.")
            
            
    #publishes a pose which is tobe a goal of move_base
    def publishGoal(self, x, y, z, ortx, orty, ortz, ortw,  i):
        
        goal = move_base_msgs.msg.MoveBaseActionGoal()
        
        goal.header.seq = i
        goal.header.stamp = rospy.Time.now()
        goal.header.frame_id = "map"
        
        goal.goal_id.stamp = rospy.Time.now()
        goal.goal_id.id = "Goal " + str(i)
        
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
    
    #puts together pose, to be published as initial pose to amcl
    def buildAMCLPose(self):
        p = geometry_msgs.msg.PoseWithCovarianceStamped()
        p.header.stamp = rospy.Time()
        p.header.frame_id = "map"
        p.pose.covariance = numpy.zeros(36)
        p.pose.pose.position.x = 5
        p.pose.pose.position.y = 0
        p.pose.pose.position.z = 0
        p.pose.pose.orientation.w = 1
        return p

        
if __name__ == '__main__':
    rospy.init_node('path_controller')
    C = Controller("Full_Path")
    while(1):
        C.driveAround()
    rospy.spin()
    
    
    
    
