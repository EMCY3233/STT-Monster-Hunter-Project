"""Bounded arrow or mapped game-button input for one foreground Citra window.

No downloads, remapping, hooks, drivers, focus changes, or background input.
Windows SendInput/KEYBDINPUT reference:
https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-keybdinput
"""
import argparse
import ctypes as c
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import time
from datetime import datetime, timezone

ARROWS = {"left": (0x25, 0x4B), "up": (0x26, 0x48),
          "right": (0x27, 0x4D), "down": (0x28, 0x50)}
KEYS = {**ARROWS, "interact": (0x41, 0x1E), "cancel": (0x53, 0x1F), "menu": (0x4D, 0x32), "dash": (0x57, 0x11)}
MAX_SECONDS = 30


def validate_keys(keys):
    keys = tuple(keys)
    if not keys or len(keys) > 4 or len(set(keys)) != len(keys) or any(k not in KEYS for k in keys):
        raise ValueError('choose 1..4 distinct supported controls')
    if any(a in keys and b in keys for a,b in [('left','right'),('up','down')]):
        raise ValueError('opposite directions cannot be held together')
    return keys


def hold_keys(send, foreground_ok, sleep, clock, seconds, keys):
    """Release every attempted key even if another release or press fails."""
    keys = validate_keys(keys)
    attempted = []
    def group(up):
        if not up:
            for key in keys:
                if not foreground_ok():raise RuntimeError('foreground changed; hold aborted')
                attempted.append(key)
                send(key, False)
        else:
            errors = []
            for key in reversed(attempted):
                try:send(key, True)
                except BaseException as exc:errors.append(exc)
            if errors:raise RuntimeError('one or more key releases failed') from errors[0]
    return hold(group, foreground_ok, sleep, clock, seconds)


def event_flags(key, up):
    if key not in KEYS:raise ValueError('unsupported game control')
    return 0x8 | (1 if key in ARROWS else 0) | (2 if up else 0)


def hold(send, foreground_ok, sleep, clock, seconds):
    """Always attempt key-up, including focus loss and partial input failure."""
    if not 0.1 <= seconds <= MAX_SECONDS:
        raise ValueError("duration must be 0.1..30 seconds")
    if not foreground_ok():
        raise RuntimeError("target is not foreground")
    start = clock()
    try:
        send(False)
        while clock() - start < seconds:
            if not foreground_ok():
                raise RuntimeError("foreground changed; hold aborted")
            sleep(min(0.01, max(0, seconds - (clock() - start))))
    finally:
        send(True)
    return clock() - start


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--window", type=int, required=True)
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--key", choices=KEYS, action="append", help="repeat for simultaneous controls; default: right")
    p.add_argument("--seconds", type=float, default=2)
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--execute", action="store_true", help="default validates only")
    a = p.parse_args()
    if os.name != "nt" or not 0.1 <= a.seconds <= MAX_SECONDS:
        p.error("requires Windows and duration 0.1..30")
    try: selected = validate_keys(a.key or ['right'])
    except ValueError as exc:p.error(str(exc))
    if a.exe.name.lower() != "citra-qt.exe":
        p.error("only citra-qt.exe is supported")
    # Reserve an exclusive receipt before any input, so evidence cannot overwrite.
    with a.receipt.open("x", encoding="utf-8") as out:
        result = {"utc": datetime.now(timezone.utc).isoformat(),
                  "keys": selected, "requested_seconds": a.seconds,
                  "executed": False, "movement_verified": False, "events": []}
        try:
            u = c.WinDLL("user32", use_last_error=True)
            k = c.WinDLL("kernel32", use_last_error=True)
            u.GetForegroundWindow.restype = w.HWND
            u.GetWindowThreadProcessId.argtypes = [w.HWND, c.POINTER(w.DWORD)]
            u.IsWindow.argtypes = [w.HWND]
            u.GetAsyncKeyState.argtypes = [c.c_int]
            u.GetAsyncKeyState.restype = c.c_short
            k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
            k.OpenProcess.restype = w.HANDLE
            k.QueryFullProcessImageNameW.argtypes = [w.HANDLE, w.DWORD, w.LPWSTR, c.POINTER(w.DWORD)]
            k.CloseHandle.argtypes = [w.HANDLE]
            pid = w.DWORD()
            if not u.IsWindow(a.window):
                raise RuntimeError("selected window no longer exists")
            u.GetWindowThreadProcessId(a.window, c.byref(pid))
            ph = k.OpenProcess(0x1000, False, pid.value)
            if not ph:
                raise c.WinError(c.get_last_error())
            try:
                path = c.create_unicode_buffer(32768)
                length = w.DWORD(len(path))
                if not k.QueryFullProcessImageNameW(ph, 0, path, c.byref(length)):
                    raise c.WinError(c.get_last_error())
                if os.path.normcase(os.path.realpath(path.value)) != os.path.normcase(str(a.exe.resolve(strict=True))):
                    raise RuntimeError("selected window executable does not match")
            finally:
                k.CloseHandle(ph)
            result["target_pid"] = pid.value
            def foreground_ok():
                current_pid = w.DWORD()
                u.GetWindowThreadProcessId(a.window, c.byref(current_pid))
                return u.GetForegroundWindow() == a.window and current_pid.value == pid.value
            if not foreground_ok():
                raise RuntimeError("Citra must already be foreground")
            # Avoid overlapping physical or synthetic held keys/modifiers.
            if any(u.GetAsyncKeyState(vk) & 0x8000 for vk in [0x10, 0x11, 0x12, 0x5B, 0x5C, *(k[0] for k in KEYS.values())]):
                raise RuntimeError("release arrows and modifiers before test")
            class KEYBDINPUT(c.Structure):
                _fields_ = [("wVk", w.WORD), ("wScan", w.WORD), ("dwFlags", w.DWORD), ("time", w.DWORD), ("dwExtraInfo", c.c_size_t)]
            class MOUSEINPUT(c.Structure):
                _fields_ = [("dx", w.LONG), ("dy", w.LONG), ("mouseData", w.DWORD), ("dwFlags", w.DWORD), ("time", w.DWORD), ("dwExtraInfo", c.c_size_t)]
            class HARDWAREINPUT(c.Structure):
                _fields_ = [("uMsg", w.DWORD), ("wParamL", w.WORD), ("wParamH", w.WORD)]
            class PAYLOAD(c.Union):
                _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]
            class INPUT(c.Structure):
                _fields_ = [("type", w.DWORD), ("payload", PAYLOAD)]
            assert c.sizeof(INPUT) == (40 if c.sizeof(c.c_void_p) == 8 else 28)
            u.SendInput.argtypes = [w.UINT, c.POINTER(INPUT), c.c_int]
            u.SendInput.restype = w.UINT
            def send(key, up):
                event = INPUT(type=1, payload=PAYLOAD(ki=KEYBDINPUT(0, KEYS[key][1], event_flags(key, up), 0, 0)))
                accepted = u.SendInput(1, c.byref(event), c.sizeof(INPUT))
                result["events"].append({"key": key, "event": "up" if up else "down", "monotonic": time.monotonic(), "accepted": accepted})
                if accepted != 1:
                    raise RuntimeError("SendInput did not accept the keyboard event")
            result["validated"] = True
            if a.execute:
                result["executed"] = True
                result["elapsed_seconds"] = hold_keys(send, foreground_ok, time.sleep, time.monotonic, a.seconds, selected)
            result["status"] = "completed" if a.execute else "validated_only"
        except BaseException as exc:
            result["status"] = "failed"
            result["error"] = str(exc)
            raise
        finally:
            json.dump(result, out, indent=2)
            out.write("\n")
            print(json.dumps(result))


if __name__ == "__main__":
    main()
