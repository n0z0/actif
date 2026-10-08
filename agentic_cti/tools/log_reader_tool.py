import os
import json
from typing import Type, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class LogReaderInput(BaseModel):
    sensor: str = Field(
        ...,
        description="Sensor to read logs from: 'synwatcher', 'scp', 'classroot', 'lemes', or 'all'"
    )
    ip: Optional[str] = Field(
        None,
        description="Optional filter by attacker IP address"
    )
    limit: int = Field(
        20,
        description="Maximum number of log events to retrieve (default: 20)"
    )

class LogReaderTool(BaseTool):
    name: str = "log_reader"
    description: str = (
        "Reads and parses structured JSON Lines (JSONL) CTI logs from the 4 deception sensors: "
        "'synwatcher' (L4 SYN probes), 'scp' (L7 SFTP knock & file forensics), "
        "'classroot' (L7 WebRTC LAN leak & GPU credentials), and 'lemes' (L7 Honeybeacon & de-anonymization). "
        "Supports filtering by IP and limiting results."
    )
    args_schema: Type[BaseModel] = LogReaderInput

    def _resolve_log_paths(self) -> Dict[str, str]:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        central_dir = os.getenv("N0Z0_LOG_DIR", "C:\\ProgramData\\n0z0\\logs")

        # Map lokasi default file log
        paths = {
            "synwatcher": os.path.join(root_dir, "synwatcher", "synwatcher_cti.jsonl"),
            "scp": os.path.join(root_dir, "scp", "scp_cti.jsonl"),
            "classroot": os.path.join(root_dir, "ClassRoot", "classroot_cti.jsonl"),
            "lemes": os.path.join(root_dir, "lemes", "lemes_cti.jsonl"),
        }

        # Cek jika ada di central directory
        for sensor, default_p in paths.items():
            central_p = os.path.join(central_dir, f"{sensor}_cti.jsonl")
            if os.path.isfile(central_p):
                paths[sensor] = central_p

        return paths

    def _parse_jsonl(self, filepath: str, filter_ip: Optional[str], limit: int) -> List[Dict[str, Any]]:
        events = []
        if not os.path.isfile(filepath):
            return events

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                # Baca dari baris paling baru (reverse)
                for line in reversed(lines):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        # Filter IP jika diminta
                        if filter_ip:
                            record_str = json.dumps(record)
                            if filter_ip not in record_str:
                                continue
                        events.append(record)
                        if len(events) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

        return events

    def _run(self, sensor: str, ip: Optional[str] = None, limit: int = 20) -> str:
        paths = self._resolve_log_paths()
        sensor = sensor.lower().strip()

        target_sensors = []
        if sensor == "all":
            target_sensors = list(paths.keys())
        elif sensor in paths:
            target_sensors = [sensor]
        else:
            return f"Error: Sensor '{sensor}' tidak dikenal. Pilihan: 'synwatcher', 'scp', 'classroot', 'lemes', 'all'."

        results = {}
        total_found = 0

        for s in target_sensors:
            p = paths[s]
            evts = self._parse_jsonl(p, filter_ip=ip, limit=limit)
            results[s] = {
                "filepath": p,
                "file_exists": os.path.isfile(p),
                "matched_events": len(evts),
                "events": evts
            }
            total_found += len(evts)

        if total_found == 0:
            return (
                f"[LogReader] Tidak ditemukan log event untuk filter sensor='{sensor}' dan ip='{ip}'. "
                f"File log mungkin masih kosong atau target belum pernah berinteraksi."
            )

        return json.dumps(results, indent=2, ensure_ascii=False)
