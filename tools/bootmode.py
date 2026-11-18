import sys, time, serial

port = sys.argv[1]
s = serial.Serial(port, 74880, timeout=0.2)
print("listening at 74880, waiting for a reset...", flush=True)
buf = b""
end = time.time() + 90
seen_at = None
while time.time() < end:
    buf += s.read(4096)
    if seen_at is None and b"boot mode" in buf:
        seen_at = time.time()
    if seen_at and time.time() - seen_at > 1.5:
        break
s.close()
print("text:", buf.decode("utf-8", "replace"))
sys.exit(0 if seen_at else 1)
