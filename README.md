# Face_recognition-Access_Control

This project implements a real-time face recognition system that integrates with an ESP32 microcontroller to control an LED and a servo motor based on recognized faces. The system captures video input from a webcam, processes the frames to detect faces, and compares them against stored face encodings retrieved from a MySQL database. When a recognized face is detected, the system sends a signal to the ESP32 to activate or deactivate the connected devices.

Features

-Real-time face detection and recognition using the face_recognition library.

-Serial communication with an ESP32 microcontroller for controlling hardware components (LED and servo).

-Database integration with MySQL to store and retrieve student data and face encodings.
User-friendly interface using Tkinter for file dialog interactions.

Why This Project is Useful

-Access Control: This system can be utilized in educational institutions or workplaces for secure access control. Only recognized individuals can gain access to restricted areas or systems, enhancing security.

-Attendance Tracking: The project can automate attendance tracking by recognizing students as they enter a classroom, reducing the need for manual roll calls.

-Interactive Learning: By integrating physical components like LEDs and servos, this project can be expanded into interactive learning tools, making education more engaging.

-Prototyping Platform: It serves as an excellent foundation for developers and hobbyists interested in building IoT applications that involve facial recognition and hardware control.

-Skill Development: Working on this project provides valuable experience in various areas such as computer vision, machine learning, database management, and embedded systems programming.
