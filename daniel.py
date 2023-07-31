import subprocess
import sys
import ctypes
from ctypes import wintypes

def read_bytes_from_virtual_memory(process_id, start_address, size):
    # Get handle to the target process
    process_handle = ctypes.windll.kernel32.OpenProcess(0x0010, False, process_id)

    # Allocate a buffer to store the read bytes
    buffer = ctypes.create_string_buffer(size)

    # Read the bytes from the target process's virtual memory
    bytes_read = wintypes.DWORD()
    ctypes.windll.kernel32.ReadProcessMemory(process_handle, start_address, buffer, size, ctypes.byref(bytes_read))

    # Close the process handle
    ctypes.windll.kernel32.CloseHandle(process_handle)

    # Convert the buffer to a list of bytes
    data = list(buffer.raw[:bytes_read.value])
    return data

def main(prog,start,end):
    # Replace "process_id" with the PID of the target process
    process_id = subprocess.Popen(prog)

    # Replace "start_address" and "size" with the desired memory range to read
    start_address = ctypes.c_void_p(start)  # Replace "address" with the starting address in hexadecimal format
    size = end-start  # Number of bytes to read

    # Read bytes from the target process's virtual memory
    bytes_read_list = read_bytes_from_virtual_memory(process_id, start_address, size)

    # Display the bytes read
    print("Bytes read:", bytes_read_list)

if __name__ == "__main__":
    main(sys.argv[0],sys.argv[1],sys.argv[2])