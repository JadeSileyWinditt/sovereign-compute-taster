#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
echo "=== Chaos: packet drops ==="
python -c "
from transport import LoopbackTransport
t = LoopbackTransport(port=9710, drop_rate=0.5)
sent = sum(1 for i in range(10) if t.send({'i': i}))
recv = sum(1 for _ in range(sent) if t.recv(0.2))
t.close()
print(f'drop_rate=0.5 sent={sent} received={recv}')
assert recv < sent
print('chaos passed')
"
echo "=== Done ==="
