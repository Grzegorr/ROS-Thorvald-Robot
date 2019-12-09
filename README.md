Introduction:  
The focus area is computer vision. The robot will go over all rows in a training area apply its detection mechanisms and publish a point cloud containing locations of detected weeds in rviz on topic "thorvald_001/weedMap". The point cloud is in frame "map". 
  
How to run:  
There are two launch files available, both in package named "ROS". First of them, called "BasicLaunch.launch" is running the gazebo simulation, amcl and move_base nodes. This is to be used for debugging and testing mainly. The full operation and rviz can be started with "FullLaunch.launch" file. On the top of rviz and nodes strated by basic launch file, it also starts up three following Nodes:
-weedMap.py("ROS" package) - this receives a pointcloud of points representing weed in camera frame and transform between camera frame and map frame at time on image capture. It processes the information and publishes a point clound in "map" frame for positions of all weeds detected since start.  
  
-PathController.py("ROS" package) - this is a top level controller with pre programmed waypoints and detection modes changing at waypoints. It also publishes a starting pose to amcl. 
  
-weedDetection.py("my_openCV" package) - this node subscribes to topics defining camera mode and to camera itself. It publishes a point cloud of weeds detected at the last frame in camera frame and transform beetween a camera frame and map frame at the time the image was capured.  
  

Additional feature:  
The transform is looked up before processing the picture from a camera, and is being looked up at the timestamp of image capture. Therefore, the accuracy of the map is independent of delay comming from processing the frame.



