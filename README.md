# Description 

This is a project in which I use Raspberry Pi 3 Model B+, SIM7600X module and web camera to detect suspicious behavior in abandoned buildings.

How it works? A person croses close to an ultrasonic sensor in a distance less then 200cm, the camera is activated and with OpenCV a video is maid and csv file with date and timestamp of movements. Then it's send via the cellular network with the help of SIM7600X module from one email address(the abandoned building) to the police headquarters(the receiving email address), where it will be analyzed.

 
