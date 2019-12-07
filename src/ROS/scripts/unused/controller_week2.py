#!/usr/bin/env python
import rospy
#for listening for the laser scan
from sensor_msgs.msg import LaserScan
#for sending movment information
from geometry_msgs.msg import Twist
class Controller:
    def __init__(self):
        self.publisher = rospy.Publisher('/thorvald_001/nav_vel', Twist,  queue_size = 1)
        rospy.Subscriber("/thorvald_001/scan",  LaserScan,  self.callback)
        
    def callback(self,  data):
        min_dist = min(data.ranges)
        t = Twist()
        if min_dist < 3:
            t.angular.z = 1.0
        else:
            t.linear.x = 1.0
        self.publisher.publish(t)
 
if __name__ == '__main__' :
    rospy.init_node('controller')
    Controller()
    rospy.spin()












