---
name: actif-orchestrator
description: Orchestrates, operates, and troubleshoots the actif (Agentic Cyber Threats Intelligence Flow) ecosystem, coordinating the 5 deception Go daemons (cachedb, synwatcher, scp, ClassRoot, lemes) and the CrewAI multi-agent intelligence pipeline.
---

# Actif Orchestrator & Deception CTI Operations

Gunakan skill ini untuk mengoperasikan, mengorkestrasikan, dan melakukan troubleshooting terhadap ekosistem **`actif`** (Agentic Cyber Threats Intelligence Flow).

---

## 1. Navigasi & Peta Repositori

| Path | Bahasa / Framework | Fungsi & Peran |
|---|---|---|
| `cachedb/` | Go / gRPC (`:50051`) | In-memory Threat State Bus, correlation engine (TTL 10 jam), CLI inspection (`-actor`, `-actors`, `-ping`, `-blocklist`, `-export-stix`). |
| `synwatcher/` | Go / Npcap | L4 SYN sniffer, passive OS estimation, TCP SYN fingerprint hash MD5, scan velocity calculation, thread-safe rDNS cache. |
| `scp/` | Go / SSH (`:60606`) | Dynamic knock auth honeypot, forensic file worker pool (DOCX, PDF, EXIF GPS, PDB), pendaftaran unduhan lure ke `cachedb`. |
| `ClassRoot/` | Go / WebRTC (`:8443`) | WebRTC ICE candidate local IP leak (unmasking VPN/Tor), WebGL GPU renderer, camera/mic detection, harvested credentials capture. |
| `lemes/` | Go / HTTP (`:50505`) | Attribution de-anonymization sink, generator dokumen umpan (Word `.docx`, Excel `.xlsx` via `CONTENT.csv`, PDF `.pdf`), asynchronous SOAR/Webhook dispatcher. |
| `agentic_cti/` | Python / CrewAI | Modul orkestrasi 5 Agen AI otonom untuk analisis dan korelasi data telemetri seluruh sensor. |

---

## 2. Prosedur Pengecekan Kesiapan (Health Check)

Sebelum menjalankan atau mengevaluasi ekosistem, periksa kondisi sistem:

```powershell
# 1. Cek liveness CacheDB:
cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\cachedb
go run main.go -ping
# Ekspektasi: PONG

# 2. Cek ketersediaan port:
Get-NetTCPConnection -LocalPort 50051, 60606, 8443, 50505 -ErrorAction SilentlyContinue

# 3. Cek apakah ada aktor aktif di memori:
go run main.go -actors
```

---

## 3. Menjalankan 5 Sensor Deception (Urutan Wajib)

Buka 5 terminal terpisah dan jalankan sesuai urutan:

```powershell
# Terminal 1: In-Memory Threat State Bus (WAJIB PERTAMA)
cd .\cachedb
go run main.go -port 50051 -ttl 36000

# Terminal 2: Sensor Pengintaian L4 (Pastikan Npcap aktif)
cd .\synwatcher
go run . -cti synwatcher_cti.jsonl

# Terminal 3: Dynamic SFTP Honeypot & Forensik
cd .\scp
go run .

# Terminal 4: Honeybeacon & Alerting Webhook
cd .\lemes
go run . -port :50505 -ctilog lemes_cti.jsonl

# Terminal 5: WebRTC Decoy & LAN Unmasker
cd .\ClassRoot
go run .
```

---

## 4. Menjalankan AI-Powered CTI Orchestrator (CrewAI)

Modul `agentic_cti` mengerahkan 5 agen spesialis:
1. `l4_recon_specialist`: Analisis scan velocity, SYN fingerprint, passive OS.
2. `dfir_file_specialist`: Analisis author OpenXML, EXIF GPS, compiler PDB, SHA-256.
3. `attribution_hunter`: Unmasking VPN via WebRTC host ICE candidate & token mismatch.
4. `threat_intel_strategist`: Pemetaan MITRE ATT&CK & kalkulasi Composite Threat Score.
5. `soc_incident_commander`: Pembuatan Executive Brief, STIX 2.1 JSON, dan firewall blocklist.

### Cara Eksekusi:
```powershell
cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\agentic_cti

# 1. Pastikan virtual environment aktif dan dependensi terpasang:
uv pip install -r requirements.txt  # atau: pip install -r requirements.txt

# 2. Pastikan file .env memiliki API Key (OPENAI_API_KEY atau GEMINI_API_KEY)

# 3. Jalankan investigasi IP penyerang:
python main.py run --ip 198.51.100.25

# 4. Atau jalankan demonstrasi simulasi skenario end-to-end:
python main.py demo
```

---

## 5. Lokasi Log & Output Analisis

- Log L4: `synwatcher/synwatcher_cti.jsonl`
- Log SFTP: `scp/scp_cti.jsonl`
- Log WebRTC: `ClassRoot/classroot_cti.jsonl`
- Log Honeybeacon: `lemes/lemes_cti.jsonl`
- Laporan AI CTI: `agentic_cti/reports/latest_cti_incident_report.md`
- Daftar Blokir Firewall: `firewall_blocklist.txt`
- Berkas STIX 2.1: `stix_incident_bundle.json`
- Dokumentasi Operasional Lengkap: [CTI_BRIEF.md](../../CTI_BRIEF.md)
