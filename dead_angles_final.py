import cv2
import pandas as pd
import time
from datetime import datetime
import csv
import os
import yagmail
import RPi.GPIO as GPIO
import serial

TRIG_PIN = 23
ECHO_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)


SIM7600_PORT = '/dev/ttyS0'
BAUD_RATE = 115200


ser = serial.Serial(SIM7600_PORT, BAUD_RATE, timeout=5)


def initialize_sim7600():

    print("Activating SIM7600X")
    ser.write(b'AT\r\n')
    time.sleep(1)
    print(ser.read(ser.inWaiting()))

    print("Network response")
    ser.write(b'AT+CREG?\r\n')
    time.sleep(1)
    print(ser.read(ser.inWaiting()))

    print("Connecting to data network or LTE")
    ser.write(b'AT+CGATT=1\r\n')
    time.sleep(2)
    print(ser.read(ser.inWaiting()))

    print("IP address assigned from the network")
    ser.write(b'AT+CGPADDR\r\n')
    time.sleep(1)
    print(ser.read(ser.inWaiting()))


    print("Signal strength")
    ser.write(b'AT+CSQ\r\n')
    time.sleep(1)
    print(ser.read(ser.inWaiting()))



def measure_distance():
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.1)
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    pulse_start = time.time()
    pulse_end = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def data(csv_file):
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)
        return any(row for row in csv_reader)

def cam_activation():
    csv_file_path = '/home/pi/SIM7600X-4G-HAT-Demo/Raspberry/python/Email/movements.csv'
    video_file_path = '/home/pi/SIM7600X-4G-HAT-Demo/Raspberry/python/Email/file.avi'
    duration = 30
    start = time.time()
    static_back = None
    motion_list = [None, None]
    date = []
    df = pd.DataFrame(columns=["Start", "End"])
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        print("Error reading video file")
    frame_width = int(video.get(3))
    frame_height = int(video.get(4))
    size = (frame_width, frame_height)
    result = cv2.VideoWriter('file.avi', cv2.VideoWriter_fourcc(*'MJPG'), 10, size)
    while True:
        check, frame = video.read()
        motion = 0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if static_back is None:
            static_back = gray
            continue
        diff_frame = cv2.absdiff(static_back, gray)
        thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
        cnts, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cnts:
            if cv2.contourArea(contour) < 10000:
                continue
            motion = 1
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            result.write(frame)
        motion_list.append(motion)
        motion_list = motion_list[-2:]
        if motion_list[-1] == 1 and motion_list[-2] == 0:
            date.append(datetime.now())
        if motion_list[-1] == 0 and motion_list[-2] == 1:
            date.append(datetime.now())
        cv2.imshow("Color Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if motion == 1:
                date.append(datetime.now())
            break
        if time.time() - start > duration:
            if motion == 1:
                date.append(datetime.now())
            break
    for i in range(0, len(date), 2):
        df.loc[len(df)] = [date[i], date[i+1]]
    df.to_csv("movements.csv")
    video.release()
    result.release()
    cv2.destroyAllWindows()
    print("The video was successfully saved")
    time.sleep(5)
    if data(csv_file_path):
        print(f"The CSV file '{csv_file_path}' has more than just column names.")
        print("An email was sent")
        email_address = 'nedevordanche@gmail.com'
        email_password = 'fxix jeyo txbv oaeb'
        yag = yagmail.SMTP(email_address, email_password)
        to = 'ordanchenedev@gmail.com'
        subject = 'Motion detected'
        body = 'Video and CSV file of motion'
        att = [csv_file_path, video_file_path]
        yag.send(to, subject, body, att)
        yag.close()
        time.sleep(5)
        os.remove(csv_file_path)
        os.remove(video_file_path)
    else:
        print(f"The CSV file '{csv_file_path}' only contains column names.")
        time.sleep(3)
        os.remove(csv_file_path)
        print("The CSV file was deleted")
        os.remove(video_file_path)
        print("The Video file was deleted")

def main():
    initialize_sim7600()
    try:
        print("Ultrasonic Sensor Test")
        while True:
            dist = int(measure_distance())
            print(f"Distance: {dist} cm")
            if dist < 200:
                print("Something is in the building")
                cam_activation()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
        ser.close()

if __name__ == "__main__":
    main()
