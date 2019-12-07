#!/usr/bin/env python
import tf
import rospy
import geometry_msgs.msg
from sensor_msgs.msg import PointCloud
from geometry_msgs.msg import Point32
from geometry_msgs.msg import Transform

class weedMap:
    weedMap = []
    
    def __init__(self):
        #myTF test
        #print(self.myTF([1, 0, 0], [10, 10, 10], [0, 0, 0, 1]))
        #Transformer to store a transform
        #self.trans = tf.TransformerROS(True, rospy.Duration(10.0))
        #Listening to last point cloud published by weedDetection node
        self.pcSub = rospy.Subscriber("/thorvald_001/last_frame_points", PointCloud, self.newPointsProcessing)
        #Listening to a transform looked up at time of picture apture and published by weedDetection node
        self.transSub = rospy.Subscriber("/thorvald_001/capture_time_transform", Transform, self.updateTransformer)
        #Publishing a point cloud of all weeds detected
        self.weedMapPub = rospy.Publisher("/thorvald_001/weedMap",  PointCloud,  queue_size = 1,  latch='true')
    
    
    def newPointsProcessing(self, data):
        #get time stamp of when the picture used for processing was stamped
        #print("callback")
        #stamp = data.header.stamp
        for point in data.points:
            #print(point)
#            p1 = geometry_msgs.msg.PoseStamped()
#            p1.header.frame_id = "thorvald_001/kinect2_rgb_optical_frame"
#            p1.header.stamp = stamp
#            p1.pose.orientation.w = 1.0  # Neutral orientation 
#            p1.pose.position.x = point.x
#            p1.pose.position.y = point.y
#            p1.pose.position.z = 0
            #print(p1)
            #p_map = self.trans.transformPose("/thorvald_001/corner1", p1)
            p = [point.x, point.y,  point.z]
            p = self.myTF(p, self.transform.translation, self.transform.rotation)
            dummy = Point32()
            dummy.x = p[0]
            dummy.y = p[1]
            dummy.z = p[2]
            self.weedMap.append(dummy)
        #print(self.weedMap)
        #print("Time to publish")
        self.publishMap()
        
    


    def publishMap(self):
        pc = PointCloud()
        pc.header.stamp = rospy.Time()
        pc.header.frame_id = "map"
        pc.points = self.weedMap
        self.weedMapPub.publish(pc)


    def updateTransformer(self, data):
        self.transform = data


    def myTF(self,  point,  trans,  rot):
        #translation
        point[0] = point[0] - trans.x
        point[1] = point[1] - trans.y
        point[2] = point[2] - trans.z
        point = [point[0], point[1], point[2], 0]
        #rotation
        rot = [rot.x, rot.y, rot.z, rot.w]
        ans = self.quaternionMultiplication(rot, point)
        rot_inv = [-rot[0], -rot[1], -rot[2], rot[3] ]
        return self.quaternionMultiplication(ans, rot_inv)
        
    def quaternionMultiplication(self, q1, q2):
        x1, y1, z1, w1 = q1
        x2, y2, z2, w2 = q2
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
        z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
        return  x, y, z, w

if __name__ == '__main__':  
    rospy.init_node('weed_map_node')
    WM = weedMap()
    rospy.spin()
    
    
    
    
