import os, sys, time, serial

port, baud, window = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
deadline = time.time() + 90

# Wait for the port to disappear (unplug), then reappear (replug).
seen_gone = False
while time.time() < deadline:
    exists = os.path.exists(port)
    if not exists:
        if not seen_gone:
            print("port gone (unplugged)", flush=True)
        seen_gone = True
    elif seen_gone:
        break
    time.sleep(0.02)
else:
    print("timeout: no unplug/replug seen" if not seen_gone else "timeout: port did not come back")
    sys.exit(1)

t0 = time.time()
for _ in range(100):
    try:
        s = serial.Serial(port, baud, timeout=0.2)
        break
    except Exception:
        time.sleep(0.02)
print(f"opened at {baud} baud after {time.time()-t0:.2f}s", flush=True)

buf = b""
end = time.time() + window
while time.time() < end:
    buf += s.read(4096)
s.close()
print(f"bytes received: {len(buf)}")
print("text:", buf.decode("utf-8", "replace"))
print("raw :", buf[:400])
