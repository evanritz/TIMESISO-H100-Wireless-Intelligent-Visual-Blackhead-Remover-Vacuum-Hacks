'''

File Name: display_pore_vacuum_video.py

Description: This script issues a "start receiving video" command and reads in the JPEG/JFIF encoded frames of the video feed over TCP.

Usage: python3 display_pore_vacuum_video.py <pore_vacuum_ip>

'''

import numpy as np
import socket
import time
import copy
import cv2
import sys


# Each marker consists of two bytes: 
# An FF byte followed by a byte which is not equal to 00 or FF and specifies the type of the marker.
# Only care about the SOI (Start Of Image) marker and EOI (End Of Image)
JFIF_SEGMENTS = {
    'SOI':  b'\xFF\xD8',
    # 'SOF0': b'\xFF\xC0',
    # 'SOF2': b'\xFF\xC2',
    # 'DHT':  b'\xFF\xC4',
    # 'DQT':  b'\xFF\xD8',
    # 'DRI':  b'\xFF\xDD',
    # 'SOS':  b'\xFF\xDA',
    # 'RST0': b'\xFF\xD0',
    # 'RST1': b'\xFF\xD1',
    # 'RST2': b'\xFF\xD2',
    # 'RST3': b'\xFF\xD3',
    # 'RST4': b'\xFF\xD4',
    # 'RST5': b'\xFF\xD5',
    # 'RST6': b'\xFF\xD6',
    # 'RST7': b'\xFF\xD7',
    # 'APP0': b'\xFF\xE0',
    # 'APP1': b'\xFF\xE1',
    # 'APP2': b'\xFF\xE2',
    # 'APP3': b'\xFF\xE3',
    # 'APP4': b'\xFF\xE4',
    # 'APP5': b'\xFF\xE5',
    # 'APP6': b'\xFF\xE6',
    # 'APP7': b'\xFF\xE7',
    # 'APP8': b'\xFF\xE8',
    # 'APP9': b'\xFF\xE9',
    # 'APPA': b'\xFF\xEA',
    # 'APPB': b'\xFF\xEB',
    # 'APPC': b'\xFF\xEC',
    # 'APPD': b'\xFF\xED',
    # 'APPE': b'\xFF\xEE',
    # 'APPF': b'\xFF\xEF',
    # 'COM':  b'\xFF\xFE',
    'EOI':  b'\xFF\xD9'
}

PORE_VACUUM_PORT = 10005

CONNECTION_TIMEOUT = 5

CHUNK_SIZE = 1024 # in bytes

START_RECEIVING_VIDEO_COMMAND = b'\xee\xff\xee\xff\x0a' + 11 * b'\x00' # Commands seem to to be 16 bytes long

def getMarkerIndex(marker, buffer, bufferOffset):
    global JFIF_SEGMENTS
    return buffer.find(JFIF_SEGMENTS[marker], bufferOffset)

def getFrame(sock, buffer):
    # Search for SOI marker in stream data
    startIndex = getMarkerIndex('SOI', buffer, 0)
    while startIndex == -1:
        buffer += sock.recv(CHUNK_SIZE)
        startIndex = getMarkerIndex('SOI', buffer, 0)
    
    # Found SOI marker - Now find EOI marker in stream data
    endIndex = getMarkerIndex('EOI', buffer, startIndex+2)
    while endIndex == -1:
        buffer += sock.recv(CHUNK_SIZE)
        endIndex = getMarkerIndex('EOI', buffer, startIndex+2)

    # Found SOI and EOI markers - Cut out frame
    frameBuffer = copy.deepcopy(buffer[startIndex:endIndex+2])
    #print('getFrame:', len(frameBuffer), len(buffer), '(', startIndex, endIndex, ')')
    # Skip past found frame
    buffer = buffer[endIndex+2:]
    
    return frameBuffer

def main(ip):

    fpsTextFont = cv2.FONT_HERSHEY_SIMPLEX
    newFrameTime, prevFrameTime = 0, 0
    numberOfFrames, numberOfCorruptedFrames = 0, 0
    streamBuffer = b''

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(CONNECTION_TIMEOUT)
    
    print('Spawning Pore Vacuum View window...')
    cv2.namedWindow("Pore Vacuum View", cv2.WINDOW_NORMAL)

    print(f'Connecting to Pore Vacuum ({ip}:{PORE_VACUUM_PORT})...')
    sock.connect((ip, PORE_VACUUM_PORT))

    sock.send(START_RECEIVING_VIDEO_COMMAND)
    print(f'Sent Start Receiving Video Command: {START_RECEIVING_VIDEO_COMMAND}')

    while True:
        try:
            newFrameTime = time.time()
            fps = 1 / (newFrameTime - prevFrameTime)
            prevFrameTime = newFrameTime

            frameBuffer = getFrame(sock, streamBuffer)
        
            frame = cv2.imdecode(np.frombuffer(frameBuffer, np.uint8), -1)
            if not frame is None:
                numberOfFrames += 1
                cv2.putText(frame, str(int(fps)), (7, 70), fpsTextFont, 1, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.imshow("Pore Vacuum View", frame)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                numberOfCorruptedFrames += 1

            print(f'Frames: {numberOfFrames}, Corrupted Frames: {numberOfCorruptedFrames}', end='\r')

        except KeyboardInterrupt:
            break

    sock.close()
    cv2.destroyAllWindows()
    print('\nClosing Pore Vacuum View window...')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Must provide an ip address!')
        sys.exit(1)
    main(sys.argv[1])
