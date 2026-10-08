# AGENTS.md - Project Instructions for actif (Agentic Cyber Threats Intelligence Flow)

## 1. Project Overview & Identity
- **Project Name:** `actif` (Agentic Cyber Threats Intelligence Flow).
- **Core Purpose:** Ekosistem pertahanan aktif (Active Defense & Deception) multi-layer (L4–L7) yang terintegrasi dengan **CrewAI Multi-Agent System** untuk memenuhi konsep **AI-Powered Cyber Threat Intelligence (SOC-Grade)**.
- **Repository Root:** `c:\Users\Windows 11 Pro\Documents\joe\n0z0` (`git@github.com:n0z0/actif.git`).

---

## 2. Multi-Repository Architecture & Git Topology
Repositori ini mengorkestrasi 5 sub-proyek independen dan 1 modul AI Orchestrator:
1. **`cachedb/`** (`git@github.com:n0z0/cachedb.git`):
   - In-memory threat correlation bus (gRPC `:50051`).
   - Menyimpan dossier aktor, dynamic port-knock derivation, token ownership table.
2. **`synwatcher/`** (`git@github.com:n0z0/synwatcher.git`):
   - Sensor L4 Npcap sniffer untuk mendeteksi SYN scan secara non-blocking.
   - Menghitung TCP SYN Fingerprint MD5, scan velocity, rDNS deduplication cache.
3. **`scp/`** (`git@github.com:n0z0/scp.git`):
   - Interactive SSH/SFTP honeypot (`:60606`) dengan knock auth berbasis data `synwatcher`.
   - File forensics worker pool (SHA-256, docx/pdf author, EXIF GPS, PDB).
4. **`ClassRoot/`** (`git@github.com:n0z0/ClassRoot.git`):
   - WebRTC meeting room decoy (`:8443`) yang membongkar IP LAN fisik penyerang di balik VPN (ICE candidate `typ host`), GPU WebGL renderer, dan credential harvester.
5. **`lemes/`** (`git@github.com:n0z0/lemes.git`):
   - Honeybeacon HTTP (`:50505`), generator dokumen umpan (.docx, .xlsx via `CONTENT.csv`, .pdf, .url), dan de-anonymization attribution sink dengan SOAR webhook dispatcher.
6. **`agentic_cti/`** (Bagian dari repo `actif`):
   - Modul orkestrasi Python **CrewAI** yang mengerahkan 5 agen otonom untuk menganalisis dan mengkorelasikan seluruh data sensor secara otomatis.

> [!IMPORTANT]
> Kelima folder aplikasi di atas (`cachedb`, `synwatcher`, `scp`, `ClassRoot`, `lemes`) adalah repositori git mandiri dan **di-ignore** oleh `.gitignore` pada root `actif`. Jangan menghapus atau mengubah konfigurasi `.gitignore` untuk kelima folder ini.

---

## 3. Aturan Coding & Konkurensi (Non-Negotiable Guidelines)
Jika Anda (AI Agent) diminta memodifikasi kode pada salah satu dari 5 sensor Go:
1. **Non-Blocking Architecture:** Semua operasi I/O (kriptografi hash, DNS lookup, RPC gRPC ke cachedb, disk writing JSONL, dan webhook dispatch) **WAJIB 100% asinkron** menggunakan Go routine (`go func()`) dan buffer channel (`chan`). Handler interaksi penyerang harus merespons sub-milidetik (<1ms).
2. **Reverse DNS Deduplication:** Gunakan `sync.Map` in-memory cache untuk query rDNS agar tidak membanjiri OS resolver saat terjadi port scan masif.
3. **Testing & Build Integrity:** Selalu jalankan `go test ./...` dan `go build` di direktori aplikasi yang dimodifikasi sebelum melakukan commit/push.

---

## 4. Startup Sequence & Port Matrix
Eksekusi portabel (setelah menjalankan `.\install-all.ps1`):
```powershell
1. cachedb -port 50051 -ttl 36000           (:50051 gRPC)   <-- WAJIB PERTAMA
2. synwatcher -logfile synwatcher_cti.jsonl (L4 Sniff Npcap)
3. scp                                      (:60606 SFTP)
4. lemes -port :50505 -ctilog lemes_cti.jsonl (:50505 HTTP)
5. classroot                                (:8443 WebRTC)
```

---

## 5. Menjalankan Modul AI-Powered CTI (`agentic_cti`)
- Direktori: `agentic_cti/`
- Dependensi: `uv pip install -r requirements.txt` atau `pip install -r requirements.txt`
- Konfigurasi: Salin `.env.example` ke `.env` dan tentukan API LLM (Cloud API: `OPENAI_API_KEY` / `GEMINI_API_KEY`, atau Local / Custom Endpoint: `LLM_BASE_URL=http://localhost:11434/v1` untuk Ollama).
- Eksekusi Triage: `python main.py run --ip <TARGET_IP>` atau `python main.py demo`.
- Output: Laporan eksekutif di `agentic_cti/reports/latest_cti_incident_report.md`, `firewall_blocklist.txt`, dan `stix_incident_bundle.json`.

---

## 6. Referensi Sumber Kebenaran (Ground Truth)
- Ringkasan umum & quickstart: [README.md](./README.md)
- Spesifikasi teknis CTI lengkap & SOP SOC: [CTI_BRIEF.md](./CTI_BRIEF.md)
- Modul CrewAI: [agentic_cti/README.md](./agentic_cti/README.md)
