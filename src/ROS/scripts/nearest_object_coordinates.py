#!/usr/bin/env python
import rospy
#for listening for the laser scan
from sensor_msgs.msg import LaserScan
#for sending movment information
import geometry_msgs.msg
from math import cos,  sin
class Controller:
    def __init__(self):
        #Publishing pose of an object to other nodes
        self.publisher = rospy.Publisher('laser_closest_pose', geometry_msgs.msg.PoseStamped, queue_size=1)
        #Listening to information laser scanner
        rospy.Subscriber("/thorvald_001/scan",  LaserScan,  self.callback)
     
    #This callback will calculate coordinates of closest object in scanner frame of reference
    def callback(self,  data):
        #Getting minimum distance from the scanner
        min_dist = min(data.ranges)
        #Getting index of position of this minimum range in an array
        ind = data.ranges.index(min_dist)
        #Getting angle of the minimum distance point
        angle = data.angle_min + ind * data.angle_increment
        #conversion to cartesian coordinates
        x = min_dist * cos(angle)
        y = min_dist * sin(angle)
         #Composing a pose which can be then published
        p1 = geometry_msgs.msg.PoseStamped()
        p1.header.frame_id = "thorvald_001/velodyne"
        p1.pose.orientation.w = 1.0  # Neutral orientation 
        p1.pose.position.x = x
        p1.pose.position.y = y
        p1.pose.position.z = 0
        #publish the pose
        self.publisher.publish(p1)
        #Print to terminal
        print ("Position of the closest object in cartesian:")
        print (p1)
 
if __name__ == '__main__' :
    rospy.init_node('cartesian_scan_laser')
    Controller()
    rospy.spin()


