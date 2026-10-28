"""
Starfield Native Game Launcher (Windows)
Runs Godot 4.3 Native Starfield with optimal desktop environment flags.
"""
import ctypes
from ctypes import wintypes
import sys
import os

class STARTUPINFO(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('lpReserved', wintypes.LPWSTR),
                ('lpDesktop', wintypes.LPWSTR), ('lpTitle', wintypes.LPWSTR),
                ('dwX', wintypes.DWORD), ('dwY', wintypes.DWORD),
                ('dwXSize', wintypes.DWORD), ('dwYSize', wintypes.DWORD),
                ('dwXCountChars', wintypes.DWORD), ('dwYCountChars', wintypes.DWORD),
                ('dwFillAttribute', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
                ('wShowWindow', wintypes.WORD), ('cbReserved2', wintypes.WORD),
                ('lpReserved2', ctypes.c_char_p), ('hStdInput', wintypes.HANDLE),
                ('hStdOutput', wintypes.HANDLE), ('hStdError', wintypes.HANDLE)]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [('hProcess', wintypes.HANDLE), ('hThread', wintypes.HANDLE),
                ('dwProcessId', wintypes.DWORD), ('dwThreadId', wintypes.DWORD)]

def main():
    k32 = ctypes.windll.kernel32
    base_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(base_dir, "builds")
    exe_path = os.path.join(build_dir, "StarfieldNative.exe")
    
    if not os.path.exists(exe_path):
        print(f"Executable not found at {exe_path}", file=sys.stderr)
        sys.exit(1)
        
    si = STARTUPINFO()
    si.cb = ctypes.sizeof(si)
    si.lpDesktop = r"WinSta0\Default"
    pi = PROCESS_INFORMATION()
    
    extra_args = " ".join(sys.argv[1:])
    cmd = f'"{exe_path}" {extra_args}'.strip()
    
    res = k32.CreateProcessW(None, cmd, None, None, False, 0, None, build_dir, ctypes.byref(si), ctypes.byref(pi))
    if not res:
        print(f"CreateProcess failed: {k32.GetLastError()}", file=sys.stderr)
        sys.exit(1)
        
    k32.WaitForSingleObject(pi.hProcess, 0xFFFFFFFF)
    exit_code = wintypes.DWORD()
    k32.GetExitCodeProcess(pi.hProcess, ctypes.byref(exit_code))
    k32.CloseHandle(pi.hProcess)
    k32.CloseHandle(pi.hThread)
    sys.exit(exit_code.value)

if __name__ == '__main__':
    main()
