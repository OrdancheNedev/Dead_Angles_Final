# Description

Upgraded Suspicious Behavior Detection System for Abandoned Buildings

This project is an enhanced version of a previous surveillance system, now integrating a Raspberry Pi 3 Model B+, SIM7600X module, and a web camera to improve security in abandoned buildings.

How It Works:

🔹 When a person moves within 200 cm of an ultrasonic sensor, the system activates the camera.

🔹 OpenCV records a video of the detected movement and generates a CSV log with a timestamp.

🔹 The video and log file are sent via the cellular network (using the SIM7600X module) from a designated email address (representing the building) to the police headquarters for analysis.


Upgrades & Improvements:

✔ Enhanced Communication – Now uses the SIM7600X module for remote operation without Wi-Fi.

✔ Automated Detection – Ultrasonic sensor added for improved motion activation.

This upgraded system provides real-time surveillance in remote locations, making it a more advanced and effective security solution.

