'''

File Name: send_pore_vacuum_command.py

Description: This script issues a given command value and receives the command response.

Usage: python3 send_pore_vacuum_command.py <pore_vacuum_ip> <command_value>

'''

import socket
import sys

PORE_VACUUM_PORT = 10005

CONNECTION_TIMEOUT = 5 # in seconds

CHUNK = 8192

def main(ip, commandValue):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        commandMessage = bytes.fromhex(commandValue)
        sock.settimeout(CONNECTION_TIMEOUT)
        sock.connect((ip, PORE_VACUUM_PORT))
        sock.send(commandMessage)
        commandResponse = sock.recv(CHUNK)
        
        commandResponseInASCII = ''.join([chr(b) for b in commandResponse])
        print(f'Sent Command Message: {commandMessage}')
        print(f'Received Command Response {commandResponseInASCII}')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Must provide an ip address and command value!')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])