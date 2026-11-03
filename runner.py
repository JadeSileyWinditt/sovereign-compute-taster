"""
Taster: delay-tolerant job runner.
Self-contained. Demonstrates k-of-n placement, kill, and resume.
Full dual-ledger and production transport are not included.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List


class TasterRunner:
    """Minimal in-memory placement with persistence."""

    def __init__(self, path: str = "data/state.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.nodes: Dict[str, dict] = {}
        self.jobs: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                self.nodes = data.get("nodes", {})
                self.jobs = data.get("jobs", {})
            except Exception:
                pass

    def _save(self):
        self.path.write_text(json.dumps({"nodes": self.nodes, "jobs": self.jobs}, indent=2))

    def add_node(self, node_id: str, tier: str = "T0", max_delay_sec: float = 1.0):
        self.nodes[node_id] = {"tier": tier, "max_delay_sec": max_delay_sec, "alive": True}
        self._save()

    def submit(self, job_name: str, k: int = 2, n: int = 3) -> dict:
        alive = [nid for nid, n in self.nodes.items() if n["alive"]]
        if len(alive) < k:
            return {"status": "insufficient_nodes", "placed_on": []}
        placed = alive[:n]
        qid = hashlib.sha256(job_name.encode()).hexdigest()[:16]
        self.jobs[qid] = {"name": job_name, "placed_on": placed, "status": "running"}
        self._save()
        return {"status": "running", "placed_on": placed, "q_commitment": qid}

    def kill(self, node_id: str) -> dict:
        if node_id in self.nodes:
            self.nodes[node_id]["alive"] = False
        affected = [jid for jid, j in self.jobs.items() if node_id in j.get("placed_on", [])]
        self._save()
        return {"affected_jobs": affected}

    def resume(self, q_commitment: str) -> dict:
        if q_commitment not in self.jobs:
            return {"status": "not_found"}
        self.jobs[q_commitment]["status"] = "resumed"
        self._save()
        return {"status": "resumed"}

    def node_count(self) -> int:
        return len(self.nodes)


if __name__ == "__main__":
    print("=== Sovereign Compute Taster ===")
    runner = TasterRunner()
    print(f"Nodes loaded: {runner.node_count()}")

    if runner.node_count() == 0:
        runner.add_node("node-a", tier="T0")
        runner.add_node("node-b", tier="T1", max_delay_sec=5.0)
        runner.add_node("node-c", tier="T2", max_delay_sec=30.0)
        print("Added 3 nodes")

    result = runner.submit("demo-job", k=2, n=3)
    print(f"Submitted: {result['status']} on {result.get('placed_on')}")

    if result["status"] == "running":
        killed = result["placed_on"][0]
        kill = runner.kill(killed)
        print(f"Killed {killed}: {len(kill['affected_jobs'])} jobs affected")
        resume = runner.resume(result["q_commitment"])
        print(f"Resume: {resume['status']}")

    print(f"Final nodes: {runner.node_count()}")
    print("State saved to data/state.json")
    print("=== Done (taster — full source under license) ===")
