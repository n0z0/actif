# Actif Agentic CTI (CrewAI Orchestrator)
> **AI-Powered Cyber Threat Intelligence Orchestrator for the n0z0 Deception Ecosystem**

Modul ini mengimplementasikan sistem multi-agent **CrewAI** yang mengorkestrasi, mengkorelasikan, dan menganalisis seluruh data telemetri yang dihasilkan oleh kelima sensor deception `n0z0`:
- **`synwatcher`**: L4 SYN Reconnaissance, TCP SYN Fingerprint MD5, Passive OS.
- **`scp`**: L7 SFTP Authentication, Dynamic Knock Verification, File Forensics (EXIF, OpenXML, PDB).
- **`ClassRoot`**: L7 WebRTC ICE Candidate (LAN IP Leak), GPU Renderer, Credential Harvesting.
- **`lemes`**: L7 Canary Token Activation, De-anonymization Attribution, SOAR Webhooks.
- **`cachedb`**: L7 In-Memory Threat State Bus & 360-Degree Actor Dossier.

---

## 👥 5 Agen AI Spesialis dalam Tim CTI

| Nama Agen | Peran & Tanggung Jawab | Sumber Data / Tool |
|---|---|---|
| **`l4_recon_specialist`** | Menganalisis pola scanning, scan velocity (`BURST`/`STEADY`), passive OS, dan rDNS untuk membedakan scanner otomatis vs targeted attack. | `synwatcher_cti.jsonl`, `cachedb` |
| **`dfir_file_specialist`** | Membedah berkas upload/download: SHA-256, nama author dokumen Office, GPS foto EXIF, build compiler, dan jejak artefak penyerang. | `scp_cti.jsonl`, `cachedb` |
| **`attribution_hunter`** | Membongkar penyamaran VPN/Tor dengan mengkorelasikan WebRTC private LAN IP leak, GPU WebGL hardware, dan token mismatch. | `classroot_cti.jsonl`, `lemes_cti.jsonl` |
| **`threat_intel_strategist`** | Mengkorelasikan temuan ke matriks MITRE ATT&CK Enterprise Framework, menghitung Composite Threat Score (0-100), dan motivasi ancaman. | Matriks ATT&CK, `cachedb` |
| **`soc_incident_commander`** | Menyusun Executive Incident Brief resmi, mengekspor format STIX 2.1 JSON, dan mengesahkan isolasi perimeter firewall. | `stix_exporter`, `firewall_enforcer` |

---

## 🚀 Panduan Instalasi & Penggunaan

### 1. Prasyarat
- Python 3.10+
- `uv` (sangat direkomendasikan) atau `pip`

### 2. Instalasi Dependensi
```powershell
cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\agentic_cti

# Menggunakan uv (sangat cepat):
uv pip install -r requirements.txt

# Atau menggunakan pip standar:
pip install -r requirements.txt
```

### 3. Konfigurasi Environment (`.env`)
Salin file konfigurasi contoh dan masukkan API key model AI pilihan Anda:
```powershell
Copy-Item .env.example .env
```
Edit berkas `.env` dan masukkan API Key:
```env
OPENAI_API_KEY=sk-...
# Atau menggunakan Google Gemini:
# GEMINI_API_KEY=AIza...
# OPENAI_MODEL_NAME=gemini/gemini-1.5-flash
```

---

## 💻 Menjalankan Investigasi

### 1. Menjalankan Triage Investigasi terhadap IP Tertentu:
```powershell
python main.py run --ip 198.51.100.25
```

### 2. Menjalankan Simulasi Demo:
```powershell
python main.py demo
```

---

## 📄 Artefak Hasil Investigasi (Outputs)

1. **Executive Incident Report:** `reports/latest_cti_incident_report.md`
   - Ringkasan eksekutif CTI resmi dalam Bahasa Indonesia yang siap diserahkan kepada pimpinan SOC/CISO.
2. **STIX 2.1 Threat Bundle:** `stix_incident_bundle.json`
   - Representasi terstruktur standar global untuk di-ingest ke MISP, OpenCTI, atau TAXII.
3. **Firewall Perimeter Blocklist:** `firewall_blocklist.txt`
   - Daftar IP berbahaya terkonfirmasi untuk langsung di-push ke edge firewall / IDS / IPS.
