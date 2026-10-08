# actif
> **Agentic Cyber Threats Intelligence Flow (SOC-Grade Deception Ecosystem)**

`actif` adalah repositori sentral, orkestrasi, dan tata kelola operasional untuk ekosistem **Agentic Cyber Threats Intelligence Flow (Deception Defense-in-Depth)**. Sistem ini menghubungkan sensor-sensor perangkap multi-layer (L4 hingga L7) secara asinkron menggunakan performa tinggi Go Routine dan in-memory threat bus.

---

## 🏛️ Arsitektur Ekosistem 5 Komponen

```
                      +---------------------------------------+
                      |               ATTACKER                |
                      +-------------------+-------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
   [L4 SYN Probe / Port Scan]                             [L7 Social Engineering / Web]
                |                                                   |
                v                                                   v
         +--------------+                                    +--------------+
         |  synwatcher  | (L4 Network Sensor)                |  ClassRoot   | (L7 WebRTC Decoy)
         |  Npcap Sniff |                                    |  :8443 HTTPS |
         +------+-------+                                    +------+-------+
                | Set(IP, Port)                                     | WebRTC host ICE
                v                                                   | (Leaked LAN IP)
        +---------------+ <----------- Correlation Bus ------------ |
        |    cachedb    |                                           |
        |  :50051 gRPC  | <----------- Auth / Token Validation -----+
        +-------+-------+                                           |
                | Get(IP) -> expected port                          |
                v                                                   v
         +--------------+                                    +--------------+
         |     scp      | (L7 SSH/SFTP Decoy)                |    lemes     | (L7 Honeybeacon)
         | :60606 SFTP  |                                    | :50505 HTTP  |
         +--------------+                                    +--------------+
         - Dynamic Trap Auth                                 - Canary Token & Lures
         - Forensic File Auditing                            - WebGL/GPU Fingerprinting
         - File Metadata Extraction                          - Decoy Login Portal
```

---

## 📦 Komponen Repositori Terpisah

Setiap komponen aplikasi dikelola secara modular pada repositorinya masing-masing:

| Komponen | Repositori | Layer / Protokol | Peran Intelijen Utama |
|---|---|---|---|
| **`cachedb`** | [`n0z0/cachedb`](https://github.com/n0z0/cachedb) | L7 gRPC `:50051` | In-memory Threat State Bus, correlation engine (TTL 10 jam), CLI inspection (`-actor`, `-actors`, `-ping`, `-blocklist`, `-export-stix`). |
| **`synwatcher`** | [`n0z0/synwatcher`](https://github.com/n0z0/synwatcher) | L4 Npcap Sniffer | Passive OS estimation, TCP SYN fingerprint hash MD5, scan velocity calculation, thread-safe rDNS cache. |
| **`scp`** | [`n0z0/scp`](https://github.com/n0z0/scp) | L7 SFTP/SSH `:60606` | Dynamic knock authentication, panic-proof forensic file worker pool (DOCX, PDF, EXIF GPS, PDB), pendaftaran unduhan lure ke `cachedb`. |
| **`ClassRoot`** | [`n0z0/ClassRoot`](https://github.com/n0z0/ClassRoot) | L7 WebRTC `:8443` | WebRTC ICE candidate local IP leak (unmasking VPN/Tor), WebGL GPU renderer, camera/mic detection, harvested credentials capture. |
| **`lemes`** | [`n0z0/lemes`](https://github.com/n0z0/lemes) | L7 HTTP `:50505` | Attribution de-anonymization sink, generator dokumen jebakan (Word `.docx`, Excel `.xlsx` via `CONTENT.csv`, PDF `.pdf`), asynchronous SOAR/Webhook dispatcher (Discord, Telegram, Slack, SIEM). |

---

## 📖 Dokumentasi Lengkap & Standard Operating Procedures (SOP)

Seluruh spesifikasi arsitektur, skenario penyerangan, pemetaan MITRE ATT&CK, distribusi log, SOP harian SOC, hingga manifest Filebeat & Vector didokumentasikan secara rinci di:

👉 **[CTI_BRIEF.md](./CTI_BRIEF.md)**

### Daftar Isi `CTI_BRIEF.md`:
1. **Executive Summary & Arsitektur**
2. **Peran & Spesifikasi 5 Aplikasi**
3. **Urutan Menjalankan (Startup Runbook)**
4. **End-to-End Attack Scenario & Correlation Walkthrough**
5. **Pemetaan MITRE ATT&CK Matrix** (`T1595`, `T1046`, `T1110`, `T1078`, `T1105`, `T1083`, `T1005`, `T1204`, `T1016`, `T1125`)
6. **Metadata Forensics Parser & Concurrency Architecture**
7. **Status Ekosistem & Peningkatan Konkurensi**
8. **Panduan Teknis Pembuatan Dokumen Jebakan (.docx, .xlsx, .pdf, .url)**
9. **Arsitektur Advanced Cyber Threat Intelligence (SOC-Grade) & Multi-Goroutine Pipeline**
10. **Distribusi Letak Lokasi Log & Topologi Penyimpanan (JSON Lines)**
11. **Detail Tata Cara & Standard Operating Procedures (SOP) Operasional SOC**
    - *SOP 1: Pre-Flight Checklist & Verifikasi Kesiapan*
    - *SOP 2: Prosedur Menjalankan Ekosistem (Startup Sequence)*
    - *SOP 3: Prosedur Monitoring Harian & Health Telemetry (Daily Triage)*
    - *SOP 4: Prosedur Respon Insiden & Triage Ancaman (360-Degree Dossier)*
    - *SOP 5: Prosedur Pembuatan & Distribusi Dokumen Umpan (Canary Lures)*
    - *SOP 6: Prosedur Shutdown & Maintenance Terkendali (Graceful Drain)*
12. **Panduan Integrasi Log Shipper & SIEM Ingestion (Filebeat & Vector.dev)**

---

## ⚡ Quick Cheat-Sheet untuk Analis SOC

```powershell
# 1. Verifikasi liveness CacheDB
.\cachedb.exe -ping

# 2. Inspeksi daftar penyerang aktif di memori
.\cachedb.exe -actors

# 3. Investigasi dossier 360-derajat IP tertentu
.\cachedb.exe -actor 198.51.100.25

# 4. Generate daftar blokir IP jahat untuk firewall
.\cachedb.exe -blocklist -out firewall_blocklist.txt

# 5. Ekspor data intelijen ke format STIX 2.1 JSON
.\cachedb.exe -export-stix -out threat_stix21.json

# 6. Stream log telemetri CTI secara bersamaan
Get-Content -Wait -Tail 20 .\lemes\lemes_cti.jsonl, .\ClassRoot\classroot_cti.jsonl, .\scp\scp_cti.jsonl, .\synwatcher\synwatcher_cti.jsonl
```

---

## 📄 Lisensi
Apache License 2.0 / Internal Security Operations.
