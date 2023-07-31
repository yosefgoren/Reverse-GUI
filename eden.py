import ctypes
import subprocess

# Replace 'command_to_run' with the actual command you want to execute
process = subprocess.Popen(['command_to_run', 'arg1', 'arg2'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Get the PID of the new process
pid = process.pid

PROCESS_ALL_ACCESS = 0x1F0FFF

# Open the process with read permissions
handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

if handle:
    address = 0x12345678  # Replace this with the memory address you want to read
    buffer = ctypes.create_string_buffer(1024)  # Create a buffer to hold the read data
    bytesRead = ctypes.c_ulong(0)  # Variable to store the number of bytes read

    # Read the memory from the target process
    ctypes.windll.kernel32.ReadProcessMemory(handle, address, buffer, ctypes.sizeof(buffer), ctypes.byref(bytesRead))

    # Convert the buffer to Python string (assuming it contains text data)
    data = buffer.value.decode('utf-8')
    
    print(data)

    # Close the handle to the process
    ctypes.windll.kernel32.CloseHandle(handle)
else:
    print(f"Failed to open process with PID {pid}")


def print_board(square_size):
    board = []

    letters = [l[-1] for l in data_dump.split("\n")]

    for i in range(10):
        for j in range(10):
            print(letters[i*10+j], end = " ")
        print()

print_board(10)