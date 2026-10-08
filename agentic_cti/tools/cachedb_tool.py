import os
import shutil
import subprocess
import json
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class CacheDBInput(BaseModel):
    action: str = Field(..., description="Action to perform: 'actor', 'actors', 'ping', 'blocklist'")
    ip: Optional[str] = Field(None, description="IP address when querying a specific threat actor dossier")

class CacheDBInspectorTool(BaseTool):
    name: str = "cachedb_inspector"
    description: str = (
        "Inspects active threat intelligence dossiers, dynamic knock credentials, and actor telemetry "
        "stored in the high-speed n0z0 CacheDB in-memory bus. Actions: 'actors' (list all), "
        "'actor' (get 360-degree dossier for specific IP), 'ping' (liveness check)."
    )
    args_schema: Type[BaseModel] = CacheDBInput

    def _run(self, action: str, ip: Optional[str] = None) -> str:
        # 1. Prioritaskan binary 'cachedb' yang terpasang di PATH sistem (hasil install-all.ps1)
        global_cachedb = shutil.which("cachedb")
        cachedb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "cachedb"))
        cachedb_exe = os.path.join(cachedb_dir, "cachedb.exe")

        cmd = []
        exec_cwd = None

        if global_cachedb:
            cmd = [global_cachedb]
        elif os.path.isfile(cachedb_exe):
            cmd = [cachedb_exe]
            exec_cwd = cachedb_dir
        else:
            # Fallback ke go run jika binary belum di-compile
            cmd = ["go", "run", "main.go"]
            exec_cwd = cachedb_dir

        if action == "ping":
            cmd.append("-ping")
        elif action == "actors":
            cmd.append("-actors")
        elif action == "actor":
            if not ip:
                return "Error: IP address parameter is required for 'actor' action."
            cmd.extend(["-actor", ip])
        elif action == "blocklist":
            cmd.append("-blocklist")
        else:
            return f"Error: Unknown action '{action}'. Valid actions: 'actor', 'actors', 'ping', 'blocklist'."

        try:
            res = subprocess.run(
                cmd,
                cwd=exec_cwd,
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            output = res.stdout.strip()
            if res.returncode == 0 and output:
                return output
            elif res.stderr:
                return f"[CacheDB Notice] {res.stderr.strip()}\n{output}"
            else:
                return f"[CacheDB Notice] No output returned or service offline. Command: {' '.join(cmd)}"
        except Exception as e:
            # Graceful fallback jika server CacheDB belum dinyalakan di environment pengujian
            return (
                f"[CacheDB Offline/Fallback] Tidak dapat menghubungi CacheDB daemon secara langsung ({e}). "
                f"Jika daemon belum dijalankan, mohon analisa data dari log JSONL."
            )
