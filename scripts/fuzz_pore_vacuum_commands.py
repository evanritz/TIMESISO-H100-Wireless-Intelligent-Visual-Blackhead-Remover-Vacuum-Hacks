'''

File Name: fuzz_pore_vacuum_commands.py

Description: This script is a basic fuzzer for determining commands for controlling the pore vacuum.

All commands and command responses start with \xee\xff\xee\xff

Usage: python3 fuzz_pore_vacuum_commands.py <pore_vacuum_ip> <csv_file_with_commands_and_responses>

'''

import socket
import time
import sys

PORE_VACUUM_PORT = 10005

CONNECTION_TIMEOUT = 5 # in seconds

COMMAND_HEADER = b'\xee\xff\xee\xff'
COMMAND_LENGTH = 16

CSV_HEADER = 'Test Case Number, Command Message, Command Response\n'

CHUNK = 4096

def main(ip, fileName):
    print('Starting fuzz_pore_vacuum_commands.py...')

    testCaseNumber = 0
    file = open(fileName, 'w')
    file.write(CSV_HEADER)
    print(CSV_HEADER, end='')

    for i in range(0xFF+1):
        commandInBytes = i.to_bytes(COMMAND_LENGTH - len(COMMAND_HEADER), 'little')
        commandMessageInBytes = COMMAND_HEADER + commandInBytes

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(CONNECTION_TIMEOUT)
        s.connect((ip, PORE_VACUUM_PORT))
        s.send(commandMessageInBytes)
        commandResponseInBytes = s.recv(CHUNK)
        s.close()

        testCase = f'{testCaseNumber}, {commandMessageInBytes.hex()}, {commandResponseInBytes.hex()}\n'
        testCaseNumber += 1
        file.write(testCase)
        print(testCase, end='')

        time.sleep(1)
    
    file.close()

    print('Done!')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Must provide an ip address and file to save results to!')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
