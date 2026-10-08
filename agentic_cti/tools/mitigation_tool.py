import os
import json
import datetime
from typing import Type, Optional, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class FirewallBlockInput(BaseModel):
    ip_list: List[str] = Field(..., description="List of malicious IP addresses to block")
    reason: str = Field(..., description="Justification and incident description for blocking")
    output_file: Optional[str] = Field("firewall_blocklist.txt", description="Output blocklist file path")

class FirewallEnforcerTool(BaseTool):
    name: str = "firewall_enforcer"
    description: str = (
        "Enforces perimeter network defense by exporting or adding malicious IP addresses to the firewall blocklist. "
        "Useful for blocking high-risk threat actors (Risk Score >= 70)."
    )
    args_schema: Type[BaseModel] = FirewallBlockInput

    def _run(self, ip_list: List[str], reason: str, output_file: Optional[str] = "firewall_blocklist.txt") -> str:
        if not ip_list:
            return "Error: Daftar IP kosong."

        try:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            existing_ips = set()
            if os.path.isfile(output_file):
                with open(output_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            existing_ips.add(line)

            added = []
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"\n# Rule Added at {timestamp} - Reason: {reason}\n")
                for ip in ip_list:
                    ip = ip.strip()
                    if ip and ip not in existing_ips:
                        f.write(f"{ip}\n")
                        existing_ips.add(ip)
                        added.append(ip)

            return (
                f"[FirewallEnforcer] Berhasil memperbarui '{output_file}'. "
                f"Total IP baru yang diblokir: {len(added)} ({', '.join(added) if added else 'Semua IP sudah terdaftar'})."
            )
        except Exception as e:
            return f"Error saat memperbarui blocklist firewall: {e}"


class STIXExporterInput(BaseModel):
    bundle_json: str = Field(..., description="Valid STIX 2.1 JSON string or structured CTI bundle representation")
    output_file: Optional[str] = Field("stix_incident_bundle.json", description="Target JSON file path")

class STIXExporterTool(BaseTool):
    name: str = "stix_exporter"
    description: str = (
        "Saves and exports structured Cyber Threat Intelligence data into an official STIX 2.1 JSON bundle file "
        "for integration with SIEM, MISP, OpenCTI, or TAXII servers."
    )
    args_schema: Type[BaseModel] = STIXExporterInput

    def _run(self, bundle_json: str, output_file: Optional[str] = "stix_incident_bundle.json") -> str:
        try:
            parsed = json.loads(bundle_json)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)
            return f"[STIXExporter] Berhasil mengekspor STIX 2.1 bundle ke '{output_file}'."
        except json.JSONDecodeError:
            # Jika teks bukan JSON mentah, simpan sebagai dokumen CTI terstruktur
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(bundle_json)
            return f"[STIXExporter] Dokumen CTI berhasil disimpan ke '{output_file}'."
        except Exception as e:
            return f"Error saat mengekspor STIX bundle: {e}"
