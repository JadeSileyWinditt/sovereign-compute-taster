"""Minimal UDP loopback for the taster."""

import socket
import json
import time
import random
from typing import Optional


class LoopbackTransport:
    def __init__(self, port: int = 9700, drop_rate: float = 0.0, delay_sec: float = 0.0):
        self.port = port
        self.drop_rate = drop_rate
        self.delay_sec = delay_sec
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", port))
        self.sock.settimeout(0.5)

    def send(self, payload: dict, dest_port: int = None) -> bool:
        if random.random() < self.drop_rate:
            return False
        if self.delay_sec > 0:
            time.sleep(self.delay_sec)
        data = json.dumps(payload).encode()
        self.sock.sendto(data, ("127.0.0.1", dest_port or self.port))
        return True

    def recv(self, timeout: float = 1.0):
        self.sock.settimeout(timeout)
        try:
            data, _ = self.sock.recvfrom(65535)
            return json.loads(data.decode())
        except Exception:
            return None

    def close(self):
        self.sock.close()


if __name__ == "__main__":
    print("=== UDP Loopback (taster) ===")
    t = LoopbackTransport(port=9701, drop_rate=0.3, delay_sec=0.05)
    sent = sum(1 for i in range(5) if t.send({"seq": i}))
    received = sum(1 for _ in range(sent) if t.recv(0.5))
    print(f"Sent (not dropped): {sent}  Received: {received}")
    t.close()
    print("=== Done ===")
