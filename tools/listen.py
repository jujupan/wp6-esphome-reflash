import sys, time, serial

port, baud, window = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
s = serial.Serial(port, baud, timeout=0.2)
print(f"listening at {baud} baud for {window:.0f}s", flush=True)
buf = b""
end = time.time() + window
while time.time() < end:
    chunk = s.read(4096)
    if chunk:
        print(f"[{time.strftime('%H:%M:%S')}] {len(chunk)} bytes: {chunk!r}", flush=True)
        buf += chunk
s.close()
print(f"total bytes: {len(buf)}")
print("text:", buf.decode("utf-8", "replace"))
