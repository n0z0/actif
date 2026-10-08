# Cyber Threat Intelligence (CTI) Operational Runbook & Ecosystem Brief
**Repository / Workspace:** `n0z0`  
**Ecosystem Components:** `cachedb`, `synwatcher`, `scp`, `lemes`, `ClassRoot`  
**Date:** Oktober 2026  
**Document Version:** 1.0.0

---

## 1. Executive Summary

Ecosystem ini mengimplementasikan siklus **Cyber Threat Intelligence (CTI) & Deception Defense-in-Depth** berbasis arsitektur multi-layer (L4 hingga L7). Seluruh sensor bekerja secara independen namun saling terhubung melalui **`cachedb`** sebagai *in-memory high-speed threat bus / correlation engine* dengan TTL 10 jam.

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

## 2. Peran & Spesifikasi 5 Aplikasi

| No | Aplikasi | Layer / Port | Fungsi Utama & Peran CTI |
|---|---|---|---|
| 1 | **`cachedb`** | L7 gRPC `:50051` | **Threat Cache & Correlation Engine**. Menyimpan relasi IP penyerang, target port hasil sniffing, metadata sesi, dan token canary. Default TTL: **10 Jam (36.000 detik)**. |
| 2 | **`synwatcher`** | L4 Npcap Sniffer | **Early Warning L4 Sensor**. Mendeteksi probe reconnaissance (SYN scan), memfilter traffic, lalu mendaftarkan `attacker_ip -> probed_port` ke `cachedb` secara real-time. |
| 3 | **`scp`** | L7 SSH/SFTP `:60606` | **Interactive Honeypot & File Audit**. Menggunakan dynamic authentication berbasis `cachedb` (hanya IP yang pernah scan yang punya password valid). Merekam audit transfer file (upload/download/rm) dengan pemetaan MITRE ATT&CK. |
| 4 | **`lemes`** | L7 HTTP `:50505` | **Honeybeacon & Canary Decoy**. Menyediakan tracking pixel, lure bait document, decoy admin portal, dan fingerprinting browser mendalam (Canvas, WebGL, GPU Renderer, AudioContext). |
| 5 | **`ClassRoot`** | L7 WebRTC `:8443` | **WebRTC Decoy, Client Telemetry & LAN De-anonymizer**. Ruang meeting palsu dengan auto HTTPS (self-signed). Dilengkapi sensor JS client (`cti-telemetry.js`) untuk memanen kredensial (Username & Password), User-Agent, GPU Renderer, dan menembus VPN via WebRTC ICE candidate (`typ host`). |

---

## 3. Urutan Menjalankan (Startup Runbook)

> [!IMPORTANT]
> Urutan eksekusi sangat penting: **`cachedb` harus selalu dijalankan pertama kali** agar sensor L4 dan L7 lainnya dapat langsung terhubung ke gRPC endpoint `:50051`.

### Terminal 1: Inisialisasi CacheDB (Threat State Bus)
Jalankan `cachedb` dengan TTL 10 jam (36000 detik):
```powershell
cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\cachedb
go run main.go -port 50051 -ttl 36000
```
*Output sukses: `[INFO] Server CacheDB berjalan di port :50051 dengan default TTL 36000 detik (10 jam)`*

---

### Terminal 2: Inisialisasi synwatcher (L4 Early Warning Sensor)
Pastikan Npcap telah terpasang. Jalankan `synwatcher` untuk mendengarkan aktivitas SYN probe:
```powershell
cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\synwatcher
# Untuk memilih interface otomatis:
go run . -cti syn_cti.jsonl
# Atau jika ingin menentukan interface spesifik:
# go run . -iface "\Device\NPF_{...}" -cti syn_cti.jsonl
```
*Status: `[*] CTI Logging aktif -> syn_cti.jsonl`, `[*] Connected to cacheDB at 127.0.0.1:50051`.*

---

### Terminal 3: Inisialisasi scp (L7 SFTP Honeypot)
Jalankan server SSH/SFTP perangkap:
```powershell
cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\scp
go run .
```
*Status: Berjalan pada port `0.0.0.0:60606`. Menghubungkan ke `cachedb` di `:50051` dan siap mengaudit sesi ke `scp_cti.jsonl`.*

---

### Terminal 4: Inisialisasi lemes (L7 Honeybeacon & Decoy Portal)
Jalankan decoy web portal & canary generator:
```powershell
cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\lemes
go run . -port :50505 -cti lemes_cti.jsonl
# Opsional: sertakan flag -tunnel untuk ekspos ke publik via Cloudflare Tunnel
# go run . -port :50505 -tunnel
```
*Endpoint aktif:*
- Dashboard Lure Generator: `http://localhost:50505/lure`
- Decoy Login Portal: `http://localhost:50505/login`
- Tracking Pixel: `http://localhost:50505/track.png`

---

### Terminal 5: Inisialisasi ClassRoot (WebRTC Decoy & LAN Unmasker)
Jalankan portal video room ClassRoot dengan auto self-signed HTTPS:
```powershell
cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\ClassRoot
go run .
```
*Status: Otomatis me-load atau men-generate cert & key (`cert.pem`, `key.pem`) dan melayani HTTPS pada `https://localhost:8443` (atau IP LAN `https://10.x.x.x:8443`). Username & Password wajib diisi.*

---

## 4. End-to-End Attack Scenario & Correlation Walkthrough

Berikut adalah tahapan simulasi dari awal penyerang melakukan profiling hingga identitas aslinya terungkap secara utuh:

### Fase 1: Network Reconnaissance (Recon $\to$ L4 Detection)
1. Penyerang melakukan port scan menggunakan Nmap:
   ```bash
   nmap -sS -p 22,80,443,8080,60606 192.168.1.100
   ```
2. **`synwatcher`** menangkap paket TCP SYN pada port probe (misal port 8080).
3. `synwatcher` memvalidasi bahwa IP penyerang bukan IP whitelisted, lalu mengirimkan:
   ```go
   cdc.Set("192.168.1.55", "8080") // Disimpan ke cachedb
   ```
4. Event dicatat di `syn_cti.jsonl` dengan teknik **MITRE T1046 (Network Service Scanning)**.

---

### Fase 2: Initial Access & Trap Verification (SCP Honeypot)
1. Penyerang melihat port open `60606` dan mencoba menghubunginya via SSH/SFTP:
   ```bash
   sftp -P 60606 192.168.1.55@192.168.1.100
   ```
2. **`scp`** memeriksa kredensial ke **`cachedb`**:
   - Username penyerang (`192.168.1.55`) dicocokkan dengan IP asal.
   - Password yang dimasukkan (`8080`) dicocokkan dengan nilai yang disimpan oleh `synwatcher`.
3. Jika cocok, penyerang berhasil masuk ke lingkungan sandbox virtual.
4. Ketika penyerang mengunggah file (exploit, script, atau webshell):
   - `scp` mengaudit aksi `UPLOAD` dengan teknik **MITRE T1105 (Ingress Tool Transfer)**.
   - Ukuran file, jalur target, IP, client SSH version dicatat ke `scp_cti.jsonl`.

---

### Fase 3: Deception & Lateral Movement Bait (Lemes Lure)
1. Di dalam direktori sandbox `scp`, penyerang menemukan file dokumen jebakan (lure) yang dibuat via **`lemes`** (misal: `backup_credentials_internal.docx` atau link ke `internal-portal.company.local`).
2. Penyerang membuka tautan tersebut atau mengunduh dokumen yang memiliki *embedded tracking pixel*.
3. Request masuk ke **`lemes`** (`:50505`):
   - Fingerprinting client mengekstrak User-Agent, Bahasa OS, Resolusi Layar, GPU WebGL Renderer (misal: `NVIDIA GeForce RTX 4070 Laptop GPU`).
   - `lemes` memverifikasi IP penyerang di `cachedb`, menghubungkan aktivitas web dengan aktivitas scan L4 dan upload SFTP sebelumnya.
   - Event dicatat di `lemes_cti.jsonl` (**MITRE T1204 - User Execution** & **T1078 - Valid Accounts**).

---

### Fase 4: De-anonymization & Credential Capture (ClassRoot WebRTC & Telemetry)
1. Penyerang diarahkan ke link konferensi internal di **`ClassRoot`** (`https://10.x.x.x:8443/group/ops-meeting`).
2. Penyerang menggunakan VPN komersial (Tor / Mullvad / NordVPN) untuk menyamarkan IP publiknya.
3. Saat halaman dimuat di browser penyerang:
   - Sensor frontend **`cti-telemetry.js`** langsung mengeksekusi *pre-auth reconnaissance beacon* ke `/api/telemetry`.
   - Mengambil **User-Agent**, **Resolusi Layar**, **Timezone**, dan **Kartu Grafis GPU asli** via WebGL (misal: `NVIDIA GeForce RTX 4070 Laptop GPU`).
4. Saat penyerang mengetik dan menekan tombol Join / Connect:
   - **`cti-telemetry.js`** menangkap `Username` dan `Password` secara instan, menyinkronkannya ke `cachedb` (`actor:classroot:user:<IP>` dan `actor:classroot:pass:<IP>`).
   - Browser penyerang menginisialisasi WebRTC `RTCPeerConnection` untuk handshake audio/video.
   - Browser mengirimkan ICE candidate lokal (`typ host`).
5. **`ClassRoot` CTI Engine** menangkap paket candidate ini dan mencatat:
   - **Public IP (VPN):** `185.220.101.5`
   - **Actual Private LAN IP:** `192.168.1.142` (bocor di balik tunnel VPN!)
   - **Internal Network Gateway / Subnet:** `192.168.1.0/24`
   - **User-Agent & Hardware GPU:** Lengkap tercatat di log JSONL dan `cachedb`.
6. Profil CTI lengkap terbentuk: dari port scan L4, SSH tool upload & file metadata, GPU fingerprint, username/password yang dicoba, hingga IP fisik internal penyerang.

---

## 5. Pemetaan MITRE ATT&CK Matrix

| Tactic | Technique ID | Technique Name | Sensor Pelapor | Bukti Forensik |
|---|---|---|---|---|
| **Reconnaissance** | `T1595` | Active Scanning | `synwatcher` | Pola probe IP dan sequence SYN |
| **Discovery** | `T1046` | Network Service Scanning | `synwatcher` | Target port & timestamp probe |
| **Initial Access** | `T1110.001` | Password Guessing / Brute Force | `scp` | Percobaan login gagal di port 60606 |
| **Initial Access** | `T1078` | Valid Accounts (Trapped) | `scp` / `lemes` | Login sukses dengan port-derived password |
| **Command & Control** | `T1105` | Ingress Tool Transfer | `scp` | File upload via SFTP handler |
| **Discovery** | `T1083` | File and Directory Discovery | `scp` | SFTP `ls`, `stat`, `readlink` |
| **Collection** | `T1005` | Data from Local System | `scp` | SFTP download file |
| **Execution** | `T1204` | User Execution | `lemes` | Trigger tracking pixel / canary token |
| **Defense Evasion** | `T1036` | Masquerading | `scp` | Rename / upload dengan ekstensi ganda |
| **Reconnaissance** | `T1016` | System Network Configuration Discovery | `ClassRoot` | WebRTC Host candidate (Private LAN IP) |

---

## 6. Analisis & Usulan: Integrasi Metadata Parser di `scp`

### Pertanyaan Evaluasi:
> *"Kalo misal di `scp` kita pasang meta parser gimana? Jadi misal yang masuk upload file apakah itu docx, pdf atau file gambar, kita bisa ambil meta datanya untuk bisa melakukan identifikasi juga, gimana menurutmu?"*

### Jawaban Pakar CTI:
**Sangat direkomendasikan dan bernilai intelijen sangat tinggi (High-Value CTI Capability).**

Dalam investigasi Threat Intelligence dan Digital Forensics (DFIR), penyerang sering kali berhati-hati menyembunyikan IP mereka (menggunakan VPN/Tor), tetapi **sangat sering ceroboh dalam membersihkan metadata file** yang mereka upload ke server korban atau staging box.

### Mengapa Ini Bernilai Sangat Tinggi?

1. **DOCX / Office Documents (`.docx`, `.xlsx`, `.pptx`)**:
   - Format OpenXML adalah arsip ZIP yang menyimpan `docProps/core.xml` dan `docProps/app.xml`.
   - **Data yang dapat diekstrak:**
     - `dc:creator`: Username akun Windows/Linux pembuat dokumen (misal: `ivan_dev`, `admin-pc`).
     - `cp:lastModifiedBy`: Akun yang terakhir mengubah file.
     - `dcterms:created` & `dcterms:modified`: Timestamp pembuatan file yang mengindikasikan **Timezone (Zona Waktu)** asli penyerang.
     - `Application`: Versi Office (misal: *Microsoft Office Word 16.0*, *WPS Office*, *LibreOffice*).
     - Full path template lokal yang kerap membocorkan struktur direktori penyerang (`C:\Users\<username>\...`).

2. **PDF Documents (`.pdf`)**:
   - Menyimpan *Document Information Dictionary* dan *XMP Metadata*.
   - **Data yang dapat diekstrak:**
     - `Author`, `Creator`, `Producer` (aplikasi pembuat PDF/exploit builder).
     - `CreationDate` format `D:YYYYMMDDHHmmSS+HH'mm'` membongkar offset timezone pasti (contoh: `+03'00'` untuk zona waktu Moskow/Riyadh, `+07'00'` untuk Indonesia/Vietnam).

3. **Gambar / Citra (`.jpg`, `.jpeg`, `.png`, `.tiff`)**:
   - **EXIF Data:**
     - `Camera Make / Model`: Tipe HP atau kamera penyerang (misal: *Apple iPhone 15 Pro*, *Samsung SM-S918B*).
     - `GPS Latitude & Longitude`: **Koordinat lokasi fisik riil** jika foto diambil tanpa menghapus geotag.
     - `Software`: Aplikasi editing (misal: *Adobe Photoshop 2024*, *GIMP 2.10*).

4. **Executable & Binaries (`.exe`, `.dll`, `.elf`)**:
   - **PE Debug Directory:** Path file PDB (Program Database) yang sering membocorkan username & folder project penyerang (misal: `C:\Users\John\source\repos\stealer\x64\Release\payload.pdb`).
   - Arsitektur compiler, hash SHA-256 otomatis, dan build timestamp.

---

### Rancangan Arsitektur Metadata Parser di `scp` (High-Concurrency Go Routine Engine)

Pemasangan parser tidak boleh memperlambat respons SFTP ke penyerang (harus **Zero Latency** bagi client agar tidak mencurigakan). Oleh karena itu, kita memanfaatkan **Goroutine Pipeline & Bounded Worker Pool Pattern**:

```
[Attacker SFTP Upload Selesai]
            |
            v
   trackingWriter.Close()   <--- Langsung return SUCCESS ke attacker (<1ms)!
            |
            +---> [Non-Blocking Dispatch via Buffered Channel]
                        jobsChan <- ForensicsJob{FilePath, ClientIP, Meta}
                                       |
                                       v
                     +------------------------------------+
                     |  High-Concurrency Worker Pool      |
                     |  (Misal: 8-16 Goroutine Workers)   |
                     +-----------------+------------------+
                                       |
           +---------------------------+---------------------------+
           | (Worker 1)                | (Worker 2)                | (Worker N)
           v                           v                           v
     [Safe Goroutine]            [Safe Goroutine]            [Safe Goroutine]
     - defer recover()           - defer recover()           - defer recover()
     - SHA-256 / Hash            - SHA-256 / Hash            - SHA-256 / Hash
     - Magic Byte Sniff          - Magic Byte Sniff          - Magic Byte Sniff
     - Fast XML/EXIF/PDF         - Fast XML/EXIF/PDF         - Fast XML/EXIF/PDF
           |                           |                           |
           +---------------------------+---------------------------+
                                       |
                                       v
                +-----------------------------------------------+
                | Dispatch Asinkron Hasil Analisis CTI:         |
                | 1. go ctiLogger.LogEvent(forensicsEvent)      |
                | 2. go cdc.Set("meta:author:...", author, db)  |
                +-----------------------------------------------+
```

#### Keunggulan Pendekatan Goroutine & Worker Pool:
1. **Zero-Latency Deception**: Attacker melihat upload selesai instan tanpa delay parsing.
2. **Proteksi DoS / File Bomb**: Menggunakan *bounded channel* dan *worker pool* (bukan *unbounded goroutine `go func()`* liar) mencegah memory exhaustion jika attacker meng-upload ribuan file sekaligus atau zip-bomb.
3. **Panic-Proof (Crash Resilient)**: Parsing file yang rusak/malformed dibungkus `recover()` di dalam goroutine worker sehingga daemon `scp` tetap 100% stabil.
4. **Non-blocking CacheDB Push**: Pengiriman metadata ke `cachedb` dan penulisan log JSONL juga berjalan asinkron di goroutine terpisah.

---

### Format Schema JSON Tambahan pada `SCPCTIEvent`

```json
{
  "timestamp": "2026-10-08T14:15:30Z",
  "event_type": "SFTP_FILE_FORENSICS",
  "client_ip": "192.168.1.55",
  "username": "192.168.1.55",
  "file_activity": {
    "action": "UPLOAD",
    "path": "invoice_october.docx",
    "size_bytes": 48210
  },
  "file_forensics": {
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "author": "victim_finance_corp",
    "last_modified_by": "apt_operator_01",
    "created_time": "2026-10-08T06:12:00Z",
    "software": "Microsoft Office Word 16.0",
    "detected_timezone": "UTC+3",
    "confidence_score": "HIGH",
    "parse_duration_ms": 2.4
  },
  "mitre_attack": {
    "tactic": "Persistence",
    "technique": "Upload Malware / Tools",
    "technique_id": "T1105"
  }
}
```

---

## 7. Status Ekosistem & Peningkatan Konkurensi

1. Seluruh 5 komponen (`cachedb`, `synwatcher`, `scp`, `lemes`, `ClassRoot`) kini telah terintegrasi penuh dalam satu siklus CTI multi-layer (L4–L7).
2. **Metadata Forensics Parser & Goroutine Worker Pool** pada `scp` telah aktif: mem-parsing dokumen DOCX, PDF, EXIF gambar (koordinat GPS), dan PDB binary secara instan (< 1ms SFTP response time) tanpa resiko crash (panic-safe).
3. **`ClassRoot` Client Telemetry, Peripheral & Credential Harvesting** telah aktif: sensor `cti-telemetry.js` memanen Username & Password saat login, mengungkap kartu grafis (GPU) asli penyerang via WebGL, mengekstrak model hardware fisik kamera/webcam & microphone (`T1125`/`T1123`), mendeteksi koneksi jaringan fisik (WiFi vs Ethernet & RTT) via Network API, memeriksa modul Bluetooth, dan mengekspos IP LAN private di balik VPN lewat WebRTC ICE leak (`T1016`).
4. **`lemes` Multi-Format Lure Engine & Dual-Beacon** telah aktif: menyediakan generator dokumen umpan Word (.docx), Excel (.xlsx), PDF (.pdf), dan Windows shortcut (.url) dengan pemuatan konten terpusat dari `content/CONTENT.md` serta Dual-Beacon (Cloudflare Domain + IP LAN).

---

## 8. Panduan Teknis Pembuatan Dokumen Jebakan (Bait & Canary Documents)

Untuk memancing penyerang agar membuka file di mesin lokalnya sendiri (workstation asli), kita memanfaatkan dokumen jebakan yang disisipi **External Relationship Target** pada format Microsoft Office OpenXML (**`.docx`** & **`.xlsx`**), **Adobe PDF (`.pdf`)**, serta **Windows Internet Shortcut (`.url`)**.

### A. Format 1: Microsoft Word Canary (.docx)
* **Mekanisme:** Office OpenXML External Relationship Target tanpa macro.
* **File Target:** `word/_rels/document.xml.rels`
* **Sintaks Relasi:**
  ```xml
  <Relationship Id="rIdPixel" 
                Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" 
                Target="http://<LEMES_HOST>:50505/beacon/pixel.png?token=finance_leak_01&amp;file=gaji_direksi.docx" 
                TargetMode="External"/>
  ```
* **Drawing di Body (`word/document.xml`):** Merujuk `rIdPixel` via `<a:blip r:link="rIdPixel"/>`.
* **Perilaku:** Saat dibuka di MS Word, WPS, atau LibreOffice, software otomatis melakukan HTTP GET ke `lemes` membocorkan IP publik, User-Agent Word, dan Accept-Language OS penyerang.

---

### B. Format 2: Microsoft Excel Canary Spreadsheet (.xlsx)
* **Mekanisme:** OpenXML Drawing External Relationship Target.
* **File Target:** `xl/drawings/_rels/drawing1.xml.rels`
* **Sintaks Relasi:**
  ```xml
  <Relationship Id="rIdPixel" 
                Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" 
                Target="http://<LEMES_HOST>:50505/beacon/pixel.png?token=salary_audit_01&amp;file=payroll_2026.xlsx" 
                TargetMode="External"/>
  ```
* **Drawing di Sheet (`xl/drawings/drawing1.xml`):** Ditanamkan dalam sel tersembunyi `oneCellAnchor` yang merujuk `rIdPixel`.
* **Perilaku:** Excel otomatis memuat pixel eksternal saat worksheet dibuka, sangat efektif untuk file bertema laporan keuangan, bonus eksekutif, dan data audit internal.

---

### C. Format 3: Adobe PDF Canary (.pdf)
* **Mekanisme:** PDF 1.4 Catalog `/OpenAction` URI dictionary.
* **Sintaks Objek PDF:**
  ```pdf
  1 0 obj
  <<
    /Type /Catalog
    /Pages 2 0 R
    /OpenAction 4 0 R
  >>
  endobj
  4 0 obj
  <<
    /Type /Action
    /S /URI
    /URI (http://<LEMES_HOST>:50505/beacon/pixel.png?token=pdf_leak_01&file=audit_report.pdf)
  >>
  endobj
  ```
* **Perilaku:** Ketika file dibuka di Adobe Acrobat Reader, Foxit, PDF-XChange, atau penampil PDF browser, aplikasi otomatis mengevaluasi aksi tautan dan memicu koneksi HTTP GET ke `lemes`.

---

### D. Format 4: Windows Internet Shortcut (.url)
* **Mekanisme:** Windows Shell Icon Cache Hunter.
* **Sintaks Berkas:**
  ```ini
  [InternetShortcut]
  URL=http://<LEMES_HOST>:50505/login
  IconIndex=0
  IconFile=http://<LEMES_HOST>:50505/beacon/pixel.png?token=shortcut_leak_01&file=portal.url
  ```
* **Perilaku:** Windows Explorer otomatis mengirimkan request HTTP GET untuk mengambil ikon file sesaat setelah folder atau file dilihat di direktori Windows pelaku.

---

### E. Cara Men-Generate Semua Format Secara Otomatis via `lemes`

Server `lemes` menyediakan generator bawaan untuk seluruh format non-HTML di atas:

#### 1. Melalui Browser (Dashboard Lemes):
1. Buka browser: `http://localhost:50505/lure`
2. Masukkan nama token dan nama file.
3. Klik tombol:
   * **Word (.docx)**
   * **Excel (.xlsx)**
   * **PDF (.pdf)**
   * **Shortcut (.url)**
   * **HTML (.html)**

#### 2. Melalui Terminal / Script Otomatis (curl):
```powershell
# 1. Generate Word Canary (.docx)
curl -o "Internal_VPN_Credentials.docx" "http://localhost:50505/lure/download/docx?token=sftp_leak_doc&file=Internal_VPN_Credentials.docx"

# 2. Generate Excel Canary (.xlsx)
curl -o "Executive_Payroll_2026.xlsx" "http://localhost:50505/lure/download/xlsx?token=sftp_leak_xls&file=Executive_Payroll_2026.xlsx"

# 3. Generate PDF Canary (.pdf)
curl -o "Confidential_Security_Report.pdf" "http://localhost:50505/lure/download/pdf?token=sftp_leak_pdf&file=Confidential_Security_Report.pdf"

# 4. Generate Windows Shortcut (.url)
curl -o "Corporate_Meeting_Portal.url" "http://localhost:50505/lure/download/url?token=sftp_leak_url&file=Corporate_Meeting_Portal.url"
```

Seluruh file umpan di atas diisi konten kredensial decoy yang memandu penyerang untuk login ke ruang pertemuan **`ClassRoot` (`https://<host>:8443/group/it-briefing`)**, sehingga menyempurnakan siklus intelijen ancaman multi-layer (L4-L7)!

---

### F. Pengelolaan Konten Terpusat (`content/CONTENT.md`) & Dual-Beacon Injection

Untuk menyederhanakan operasional di lapangan:

1. **Pengelolaan Konten Dinamis (`CONTENT.md` & `CONTENT.csv`):**
   * **Dokumen Naratif (`.docx`, `.pdf`, `.html`):** Menggunakan `lemes/content/CONTENT.md` (format heading, paragraf, dan bullet point).
   * **Spreadsheet Tabular (`.xlsx`):** Menggunakan `lemes/content/CONTENT.csv` (format tabel multi-kolom baris & sel Excel sungguhan, seperti daftar server, IP, port, dan kredensial decoy).
   * Tidak perlu melakukan re-compile binary `lemes` setiap kali ingin mengubah teks umpan atau kredensial rahasia! Cukup edit file `.md` atau `.csv` tersebut.

2. **Dual-Beacon Injection (Menjamin Keberhasilan Sinyal):**
   * Untuk memastikan alert CTI tetap berhasil terpicu, `lemes` menyuntikkan **dua URL target sekaligus** ke dalam setiap file:
     1. **Target 1 (Cloudflare Domain / Public URL):** Menangkap sinyal jika dokumen dibuka dari jaringan publik / internet di luar kantor.
     2. **Target 2 (IP LAN Lokal `http://<IP_LAN>:50505`):** Menangkap sinyal jika dokumen dibuka dari dalam subnet LAN / intranet kantor, atau jika koneksi tunnel mengalami kendala egress firewall.
   * Pada Word dan Excel, kedua relasi OpenXML dimasukkan sekaligus (`rIdPixel1` & `rIdPixel2`).
   * Pada PDF, tautan diikat menggunakan aksi berantai (`/OpenAction` dengan `/Next`).
   * Pada HTML, browser menembakkan beacon pasif dan telemetri hardware ke kedua endpoint secara bersamaan.

---

## 9. Arsitektur Advanced Cyber Threat Intelligence (SOC-Grade) & Multi-Goroutine Pipeline

Sistem `n0z0` mengimplementasikan arsitektur CTI berstandar **Tier-1 SOC / Enterprise Threat Intelligence Platform (TIP)** yang memanfaatkan keunggulan **Go Routine & Channel-Based Asynchronous Pipeline** untuk menjamin respons honeypot sub-milidetik (0ms blocking latency) serta data intelijen yang 100% lengkap dan siap dikonsumsi SIEM / SOAR.

### A. Dimensi Data 5W1H & Unified Cyber Kill Chain

| Dimensi | Parameter Intelijen | Sumber Sensor & Layer |
|---|---|---|
| **WHO** | Attacker IP, Reverse DNS (PTR Hostname), Client Version/User-Agent, Fingerprints (TCP SYN Hash MD5, WebGL GPU Renderer, Canvas & Audio Hash), Harvested Credentials (Username/Password/JWT), Uploaded Document Author/Software. | `synwatcher` (L4), `scp` (L7), `ClassRoot` (L7), `cachedb` (Actor Registry) |
| **WHEN** | Timestamp presisi tinggi sub-milidetik (ISO 8601 UTC `RFC3339Nano`), Scan Velocity (`BURST`, `STEADY`, `SLOW_AND_LOW_STEALTH`), First Seen & Last Seen. | Seluruh sensor |
| **WHERE** | Sensor Hostname ID, Internal/Private vs Public IP Classification, WebRTC ICE Candidate (Local LAN IP Leak menembus VPN), Target Port/Service (SSH, SFTP, HTTP, WebRTC), Endpoint URI yang di-probe. | `ClassRoot`, `synwatcher`, `scp` |
| **WHAT** | Event Type, Status (`success`, `failed`, `captured`, `rejected_404`), Attack Pattern (`SQL_INJECTION`, `PATH_TRAVERSAL`, `COMMAND_INJECTION_OR_WEBSHELL`, `CROSS_SITE_SCRIPTING`, `SENSITIVE_FILE_SCANNING`, `BRUTEFORCE`), File Hash (SHA-256/MD5). | `ClassRoot`, `scp`, `synwatcher` |
| **WHY** | Dynamic Intent Category (`PORT_SWEEP_RECON`, `LATERAL_MOVEMENT_PROBE`, `INITIAL_ACCESS_EXPLOITATION`, `DATA_EXFILTRATION`), Risk Score Komposit (0-100), Severity Level (`INFORMATIONAL`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`). | Korelasi silang L4 -> L7 di `cachedb` |
| **HOW** | Pemetaan resmi taktik dan teknik **MITRE ATT&CK Enterprise Framework** (e.g. `T1595.001`, `T1595.002`, `T1190`, `T1110.001`, `T1078`, `T1016`, `T1083`, `T1059`, `T1056.001`, `T1125`). | Otomatis di-inject ke setiap log JSONL |

---

### B. Optimalisasi Ekstrem dengan Go Routine & Concurrency Patterns

Seluruh pemrosesan intelijen berat (kriptografi hash, DNS lookup, korelasi database gRPC, dan disk I/O) dipisahkan dari thread utama interaksi penyerang:

1. **Zero-Packet-Drop Worker Pool di `synwatcher`:**
   - Sniffer mendistribusikan paket masuk ke saluran berkapasitas besar (`buffer: 4096`) yang dilayani oleh worker pool `runtime.NumCPU() * 2` Goroutines.
   - Pcap loop tidak pernah terhambat oleh operasi penulisan atau korelasi.
2. **Asynchronous Reverse DNS (rDNS) Resolver:**
   - Di `synwatcher`, `scp`, dan `ClassRoot`, setiap IP penyerang di-resolve secara paralel di background goroutine dengan timeout ketat (350-400ms).
   - PTR hostname (seperti botnet VPS, Shodan, Censys, atau ASN scanner) disematkan ke log CTI dan disinkronkan ke `cachedb` tanpa menambah latensi koneksi.
3. **Cross-Layer Asynchronous Correlation (`ClassRoot` & `scp` ke `cachedb`):**
   - Saat attacker mencoba login SFTP di `scp` atau menembak endpoint di `ClassRoot`, Goroutine asinkron memanggil `cdc.GetActor(clientIP)` ke `cachedb`.
   - Jika ditemukan rekam jejak pengintaian L4 (dari `synwatcher`), profil ancaman L4 (`recon_profile`) langsung disematkan ke event L7, dan threat score penyerang dievaluasi ulang (naik menjadi CRITICAL/95+).
4. **Panic-Proof Bounded Worker Pool Forensik File di `scp`:**
   - Saat penyerang mengunggah berkas, `trackingWriter.Close()` langsung mengembalikan status sukses ke klien SFTP (<1ms).
   - Analisis mendalam (SHA-256, Magic Byte, EXIF, OpenXML, PDF parser) didelegasikan ke forensic worker pool yang dibungkus `defer recover()` agar daemon honeypot tahan terhadap berkas korup atau zip-bomb.
5. **Non-Blocking Buffered Channel Logger:**
   - Semua event CTI dikirimkan melalui channel buffer 4096. Jika terjadi lonjakan lalu lintas ekstrem, fallback sync goroutine dijalankan secara otomatis tanpa memblokir handler honeypot.

---

### C. Konsumsi Operasional Intelijen oleh Tim SOC / SIEM

Data intelijen yang dihasilkan siap dipakai secara instan oleh analis SOC dan platform SIEM:

```powershell
# 1. Menampilkan ringkasan seluruh Threat Actor aktif
cachedb.exe -actors

# 2. Investigasi Dossier Mendalam Penyerang Tertentu (360-degree CTI view)
cachedb.exe -actor 198.51.100.25

# 3. Ekspor otomatis daftar IP Jahat (Risk >= 70) ke Firewall Blocklist
cachedb.exe -blocklist -out firewall_blocklist.txt

# 4. Ekspor seluruh Dossier Ancaman ke Format Standar Global STIX 2.1 (JSON)
cachedb.exe -export-stix -out threat_bundle_stix21.json

# 5. Menjalankan lemes Honeybeacon dengan Alerting Webhook Real-time (Discord / Telegram / SIEM)
.\lemes.exe -webhook-url "https://discord.com/api/webhooks/xxx/yyy" -webhook-type discord
# Atau untuk Telegram Bot:
.\lemes.exe -webhook-url "https://api.telegram.org/bot<TOKEN>" -webhook-type telegram -telegram-chat-id "<CHAT_ID>"

# 6. Monitoring Real-time Log CTI JSONL (Ready for Splunk / Elastic / Wazuh)
Get-Content -Wait -Tail 20 .\lemes\lemes_cti.jsonl
Get-Content -Wait -Tail 20 .\ClassRoot\classroot_cti.jsonl
Get-Content -Wait -Tail 20 .\scp\scp_cti.jsonl
Get-Content -Wait -Tail 20 .\synwatcher\synwatcher_cti.jsonl
```

---

## 10. Distribusi Letak Lokasi Log & Topologi Penyimpanan (Log Distribution Architecture)

Ekosistem `n0z0` menghasilkan telemetri terstruktur dalam format **JSON Lines (`.jsonl`)** di masing-masing sub-komponen, serta penyimpanan state memori di `cachedb`. Setiap file dirancang agar dapat di-ingest secara independen maupun dikorelasikan secara terpusat oleh platform SIEM (Elasticsearch, OpenSearch, Wazuh, Splunk, Graylog, atau Microsoft Sentinel).

### A. Tabel Distribusi Berkas Log di Ekosistem

| Komponen | Berkas Log Default | Parameter / Flag CLI | Layer & Protokol | Jenis Telemetri & Data Intelijen |
|---|---|---|---|---|
| **`synwatcher`** | `synwatcher/synwatcher_cti.jsonl` | `-logfile <path>` atau `-cti <path>` | L4 Network (Npcap) | Reconnaissance IP, SYN Fingerprint MD5, scan velocity (`BURST`, `STEADY`), rDNS, passive OS estimation, port-sweep detection. |
| **`scp`** | `scp/scp_cti.jsonl` | Konfigurasi `CTI_LOG` / Flag `-cti <path>` | L7 SFTP / SSH (:60606) | Brute-force credentials, dynamic knock validation, file auditing (upload/download/rm), file forensics (SHA-256, EXIF GPS, docx/pdf author, PDB). |
| **`ClassRoot`** | `ClassRoot/classroot_cti.jsonl` | `-ctilog <path>` | L7 Web & WebRTC (:8443) | WebRTC ICE candidate leak (Private LAN IP unmasking VPN), GPU renderer, canvas/audio hash, harvested credentials, camera/mic detection, attack patterns (SQLi/XSS/RCE). |
| **`lemes`** | `lemes/lemes_cti.jsonl` | `-ctilog <path>` | L7 HTTP (:50505) | Canary token trigger, de-anonymization attribution (VPN vs Local Workstation IP), browser hardware fingerprinting, audit pengiriman webhook (Discord/Telegram/Slack/SIEM). |
| **`cachedb`** | `cachedb/cachedb.db` *(snapshot)* | `-snapshot <path>` & `-load <path>` | L7 In-Memory Bus (:50051) | In-memory gRPC threat state, active actor dossiers, port knock derivations, token-to-owner bindings. Disimpan ke disk sesuai kebutuhan snapshot. |

---

### B. Struktur Direktori Default di Lingkungan Workspace

Secara default, saat dijalankan dari folder masing-masing sub-aplikasi, log akan ditulis di folder kerja lokal aplikasi tersebut:

```
c:\Users\Windows 11 Pro\Documents\joe\n0z0\
├── cachedb\
│   └── cachedb.db                  <-- Berkas snapshot persistensi (opsional via -snapshot)
├── synwatcher\
│   └── synwatcher_cti.jsonl        <-- L4 Reconnaissance & Port Scan Telemetry
├── scp\
│   ├── scp_cti.jsonl               <-- L7 SFTP Authentication, Knock & File Forensics Log
│   └── sandbox\                    <-- Direktori file sandbox tempat attacker berinteraksi
├── ClassRoot\
│   └── classroot_cti.jsonl         <-- L7 WebRTC Telemetry, ICE Candidate Leak & Harvested Creds
└── lemes\
    ├── lemes_cti.jsonl             <-- L7 Canary Token Activation, De-anonymization & Webhook Audit
    └── content\
        ├── CONTENT.md              <-- Sumber teks umpan Word, PDF, dan HTML
        └── CONTENT.csv             <-- Sumber tabel spreadsheet multi-kolom Excel
```

---

### C. Praktik Terbaik Sentralisasi Log di Lingkungan Produksi (SOC Deployment)

Untuk server produksi atau integrasi SIEM terpusat, disarankan mengarahkan seluruh output log ke satu direktori sentral:
* **Windows Server:** `C:\ProgramData\n0z0\logs\`
* **Linux Server:** `/var/log/n0z0/`

#### Contoh Eksekusi Terpusat di Windows:
```powershell
# Buat folder log terpusat
New-Item -ItemType Directory -Force -Path "C:\ProgramData\n0z0\logs"

# 1. Jalankan cachedb
Start-Process -FilePath ".\cachedb\cachedb.exe" -ArgumentList "-port 50051 -ttl 36000"

# 2. Jalankan synwatcher (L4)
Start-Process -FilePath ".\synwatcher\synwatcher.exe" -ArgumentList "-logfile C:\ProgramData\n0z0\logs\synwatcher_cti.jsonl"

# 3. Jalankan scp (L7 SFTP)
Start-Process -FilePath ".\scp\scp.exe" -ArgumentList "-addr :60606 -cti C:\ProgramData\n0z0\logs\scp_cti.jsonl"

# 4. Jalankan ClassRoot (L7 WebRTC)
Start-Process -FilePath ".\ClassRoot\classroot.exe" -ArgumentList "-http :8443 -ctilog C:\ProgramData\n0z0\logs\classroot_cti.jsonl"

# 5. Jalankan lemes (L7 Honeybeacon & SOAR Webhook)
Start-Process -FilePath ".\lemes\lemes.exe" -ArgumentList "-port :50505 -ctilog C:\ProgramData\n0z0\logs\lemes_cti.jsonl -webhook-url https://discord.com/api/webhooks/xxx/yyy -webhook-type discord"
```

Dengan topologi sentralisasi ini, agen log forwarder (Filebeat/Vector/Fluentbit) cukup memantau satu direktori: `C:\ProgramData\n0z0\logs\*.jsonl`.

---

### D. Estimasi Volume Log & Manajemen Retensi Berkas

1. **Volume Log per Komponen:**
   * `synwatcher`: Menghasilkan volume tertinggi (tergantung intensitas scan internet). Rata-rata 1.000 event scan menghasilkan ~400 KB JSONL.
   * `scp`: Volume rendah hingga menengah. Rata-rata 1 sesi login dan upload file menghasilkan ~2 KB JSONL.
   * `ClassRoot`: Volume menengah. Rata-rata 1 interaksi browser menghasilkan ~3 KB JSONL (lengkap dengan hardware & WebRTC candidate).
   * `lemes`: Volume event-driven (saat token/pixel dibuka). Rata-rata 1 trigger menghasilkan ~1.5 KB JSONL.
2. **Strategi Rotasi Log (Log Rotation Best Practice):**
   * Di lingkungan Linux, gunakan `logrotate` harian dengan kompresi gzip.
   * Di lingkungan Windows, buat scheduled task PowerShell untuk mengarsipkan file log jika melebihi 100 MB:
     ```powershell
     # Contoh script rotasi berkala (run daily via Task Scheduler)
     Get-ChildItem "C:\ProgramData\n0z0\logs\*.jsonl" | Where-Object { $_.Length -gt 100MB } | ForEach-Object {
         $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
         $archiveName = "$($_.FullName).$timestamp.bak"
         Move-Item $_.FullName $archiveName
     }
     ```

---

## 11. Detail Tata Cara & Standard Operating Procedures (SOP) Operasional SOC

Bagian ini menyajikan panduan operasional standar (*Standard Operating Procedures*) bagi Security Analyst, Incident Responder, dan Honeypot Administrator.

---

### SOP 1: Pre-Flight Checklist & Verifikasi Kesiapan Sistem

Sebelum menyalakan ekosistem `n0z0`, operator wajib memastikan kondisi prasyarat berikut:

1. **Verifikasi Driver Npcap (Khusus Windows):**
   ```powershell
   Get-Service npcap
   ```
   *Status harus `Running`. Jika belum terpasang, unduh dari npcap.com dengan opsi "WinPcap API-compatible Mode".*
2. **Verifikasi Ketersediaan Port Jaringan:**
   Pastikan tidak ada service lain yang bertabrakan pada port berikut:
   ```powershell
   Get-NetTCPConnection -LocalPort 50051, 60606, 8443, 50505 -ErrorAction SilentlyContinue
   ```
   *(Harus kosong sebelum ekosistem dijalankan).*
3. **Verifikasi Probe Liveness CacheDB (`-ping`):**
   Pastikan binary `cachedb` merespons probe liveness:
   ```powershell
   cd .\cachedb
   go run main.go -ping
   # Output yang diharapkan: PONG
   ```

---

### SOP 2: Prosedur Menjalankan Ekosistem (Startup Sequence)

> [!CAUTION]
> **Kepatuhan Urutan Wajib Dipatuhi:** Sensor L4 dan L7 melakukan handshake gRPC ke `cachedb` saat startup. Oleh karena itu, `cachedb` **harus** aktif terlebih dahulu.

```
Langkah 1: cachedb  (:50051)  ---> Siap melayani in-memory bus & korelasi
Langkah 2: synwatcher (L4)    ---> Mulai sniffing paket SYN, hubungkan gRPC
Langkah 3: scp        (:60606)---> Buka dynamic SFTP honeypot, hubungkan gRPC
Langkah 4: lemes      (:50505)---> Buka portal umpan & webhook, hubungkan gRPC
Langkah 5: ClassRoot  (:8443) ---> Buka WebRTC decoy room & telemetry, hubungkan gRPC
```

#### Langkah-langkah Eksekusi:

1. **Terminal 1 - Jalankan CacheDB (Pusat State Ancaman):**
   ```powershell
   cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\cachedb
   go run main.go -port 50051 -ttl 36000
   ```
   *Indikator sukses:* `[INFO] Server CacheDB berjalan di port :50051 dengan default TTL 36000 detik (10 jam)`

2. **Terminal 2 - Jalankan synwatcher (Sensor Pengintaian L4):**
   ```powershell
   cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\synwatcher
   go run . -cti synwatcher_cti.jsonl
   ```
   *Indikator sukses:* `[*] Connected to cacheDB at 127.0.0.1:50051`, `[*] Listening on interface...`

3. **Terminal 3 - Jalankan scp (Interactive Honeypot SFTP):**
   ```powershell
   cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\scp
   go run .
   ```
   *Indikator sukses:* `[*] Server SFTP honeypot aktif pada port :60606`, `[*] Terhubung ke CacheDB di 127.0.0.1:50051`

4. **Terminal 4 - Jalankan lemes (Honeybeacon & SOAR Alerting):**
   ```powershell
   cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\lemes
   go run . -port :50505 -ctilog lemes_cti.jsonl -webhook-url "https://discord.com/api/webhooks/xxx/yyy" -webhook-type discord
   ```
   *Indikator sukses:* `[CTI] Terhubung ke cacheDB di 127.0.0.1:50051`, `[Webhook] Dispatcher aktif: type=discord`

5. **Terminal 5 - Jalankan ClassRoot (WebRTC Decoy & LAN Unmasker):**
   ```powershell
   cd c:\Users\Windows 11 Pro\Documents\joe\n0z0\ClassRoot
   go run .
   ```
   *Indikator sukses:* `[CTI] Terhubung ke cacheDB di 127.0.0.1:50051`, `Server listening on https://localhost:8443`

---

### SOP 3: Prosedur Monitoring Harian & Health Telemetry (Daily Triage)

Tim SOC Tier-1 / Tier-2 memantau aktivitas secara berkala menggunakan prosedur berikut:

#### 1. Live Multi-Log Streaming di Terminal SOC:
Buka PowerShell dan pantau stream event secara simultan:
```powershell
# Memantau seluruh aktivitas L4, SFTP, WebRTC, dan Honeybeacon secara live
Get-Content -Wait -Tail 10 .\synwatcher\synwatcher_cti.jsonl, .\scp\scp_cti.jsonl, .\ClassRoot\classroot_cti.jsonl, .\lemes\lemes_cti.jsonl
```

#### 2. Inspeksi Daftar Threat Actor Aktif di CacheDB:
Untuk melihat tabel seluruh entitas penyerang yang saat ini terdata di memori bus:
```powershell
cd .\cachedb
go run main.go -actors
```
*Kolom yang ditampilkan:* `IP Address`, `Target Port`, `Risk Score`, `First Seen`, `Last Seen`, `Reverse DNS`.

#### 3. Filter Event Berbahaya / Alert Kritis:
Filter event dengan tingkat keparahan tinggi menggunakan PowerShell:
```powershell
Get-Content .\ClassRoot\classroot_cti.jsonl | ConvertFrom-Json | Where-Object { $_.severity -eq "CRITICAL" -or $_.composite_threat_score -ge 80 } | Select-Object timestamp, client_ip, composite_threat_score, event_type
```

---

### SOP 4: Prosedur Respon Insiden & Triage Ancaman (Incident Response SOP)

Ketika webhook (Discord/Telegram) berbunyi atau SIEM mendeteksi alert de-anonymization:

```
[ALERT DITERIMA] ---> [INVESTIGASI DOSSIER] ---> [ANALISIS DE-ANONYMIZATION] ---> [EXPORT STIX 2.1] ---> [ISOLASI FIREWALL]
```

#### Tahap 1: Ekstraksi Dossier Lengkap Penyerang (360-Degree CTI Dossier)
Jalankan investigasi dossier terhadap IP pelaku:
```powershell
cd .\cachedb
go run main.go -actor <IP_PENYERANG>
```
*Hasil investigasi menyajikan:*
- **Jejak L4:** Kapan melakukan scan, port apa saja yang dicari, hash TCP SYN, rDNS hostname (misal: botnet scanner / ISP).
- **Jejak SFTP:** Kredensial yang dicoba, file yang diunduh atau diunggah, hash SHA-256 malware, nama author dokumen.
- **Jejak Hardware:** GPU Renderer penyerang, Canvas hash, model webcam/microphone fisik.
- **Kredensial:** Username dan password yang diketikkan di portal jebakan.

#### Tahap 2: Pembuktian De-Anonymization (VPN Bypass)
1. Cek log `lemes_cti.jsonl` atau `classroot_cti.jsonl`.
2. Periksa parameter:
   - `client_ip`: Alamat IP eksternal penyerang (sering kali exit node VPN, misal: `185.220.101.5`).
   - `webrtc_candidate.ip`: **Alamat IP LAN fisik penyerang** yang bocor (misal: `192.168.1.142`).
   - `deanonymized`: bernilai `true` jika file canary diunduh dari IP A tetapi dibuka dari IP B.
3. Catat kedua IP tersebut sebagai IoC primer.

#### Tahap 3: Ekspor Bukti Forensik ke Format Standar STIX 2.1
Ekspor seluruh temuan ke file STIX bundle resmi untuk dibagikan ke tim DFIR, MISP, atau OpenCTI:
```powershell
cd .\cachedb
go run main.go -export-stix -out "incident_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
```

#### Tahap 4: Penegakan Blokade Firewall Otomatis (Blocklist Enforcement)
Ekspor seluruh IP penyerang dengan skor risiko $\ge 70$:
```powershell
cd .\cachedb
go run main.go -blocklist -out firewall_blocklist.txt
```
*Terapkan daftar IP tersebut ke Windows Defender Firewall atau edge firewall:*
```powershell
# Contoh inject IP blocklist ke Windows Firewall
$ips = Get-Content .\firewall_blocklist.txt
New-NetFirewallRule -DisplayName "n0z0 Deception Blocklist" -Direction Inbound -Action Block -RemoteAddress $ips
```

---

### SOP 5: Prosedur Pembuatan & Distribusi Dokumen Umpan (Canary Lure Operations)

Operator dapat memperbarui atau menaruh file umpan baru ke dalam direktori sandbox SFTP agar penyerang tergiur mengunduhnya:

1. **Membuat Dokumen Umpan Baru:**
   Pastikan `lemes` aktif di port `:50505`. Jalankan curl untuk men-generate file:
   ```powershell
   # Dokumen Word (Kredensial VPN)
   curl -o "c:\Users\Windows 11 Pro\Documents\joe\n0z0\scp\sandbox\Corporate_VPN_Access.docx" "http://localhost:50505/lure/download/docx?token=vpn_leak_01&file=Corporate_VPN_Access.docx"

   # Spreadsheet Excel (Daftar Gaji / Payroll Direksi)
   curl -o "c:\Users\Windows 11 Pro\Documents\joe\n0z0\scp\sandbox\Executive_Payroll_2026.xlsx" "http://localhost:50505/lure/download/xlsx?token=payroll_01&file=Executive_Payroll_2026.xlsx"

   # Dokumen PDF (Laporan Keamanan Rahasia)
   curl -o "c:\Users\Windows 11 Pro\Documents\joe\n0z0\scp\sandbox\Security_Audit_Report.pdf" "http://localhost:50505/lure/download/pdf?token=audit_01&file=Security_Audit_Report.pdf"
   ```
2. **Kustomisasi Isi Konten Umpan:**
   - Untuk mengubah narasi Word & PDF: edit berkas `lemes/content/CONTENT.md`.
   - Untuk mengubah isi sel tabel Excel: edit berkas `lemes/content/CONTENT.csv`.
   - Dokumen baru yang digenerate otomatis menggunakan teks terbaru tanpa perlu me-restart service!
3. **Verifikasi Jalur Jebakan:**
   Ketika penyerang login ke SFTP `:60606` dan mengetik `get Executive_Payroll_2026.xlsx`:
   - `scp` otomatis mencatat kepemilikan file (`token:owner:Executive_Payroll_2026.xlsx = <IP_ATTACKER>`) di `cachedb`.
   - Saat penyerang membuka file tersebut di komputernya, `lemes` langsung memicu alert de-anonymization ke Webhook SOAR.

---

### SOP 6: Prosedur Shutdown & Maintenance Terkendali (Graceful Shutdown)

> [!IMPORTANT]
> Jangan mematikan proses menggunakan `kill -9` atau `Stop-Process -Force` secara mendadak. Seluruh sensor memiliki **buffered goroutine channel** untuk penulisan log. Penghentian normal (`Ctrl+C` atau `SIGTERM`) memastikan seluruh antrean event di-flush ke disk secara sempurna (*zero log drop*).

#### Urutan Shutdown yang Benar:
1. Hentikan sensor-sensor layer aplikasi terlebih dahulu:
   - Tekan `Ctrl+C` pada terminal **`ClassRoot`** (tunggu log shutdown complete).
   - Tekan `Ctrl+C` pada terminal **`lemes`** (tunggu drain event selesai).
   - Tekan `Ctrl+C` pada terminal **`scp`** (tunggu forensic worker pool selesai).
   - Tekan `Ctrl+C` pada terminal **`synwatcher`**.
2. Simpan snapshot data `cachedb` (opsional):
   ```powershell
   cd .\cachedb
   go run main.go -snapshot cachedb_backup.db
   ```
3. Terakhir, hentikan **`cachedb`** dengan menekan `Ctrl+C`.

---

## 12. Panduan Integrasi Log Shipper & SIEM Ingestion

Untuk menghubungkan seluruh log JSONL ekosistem `n0z0` ke platform SIEM enterprise, berikut adalah contoh konfigurasi shipper yang siap digunakan:

### A. Konfigurasi Filebeat (`filebeat.yml`)
Tambahkan input filebeat untuk memantau keempat berkas log secara live:

```yaml
filebeat.inputs:
  - type: filestream
    id: n0z0-synwatcher
    paths:
      - "C:/ProgramData/n0z0/logs/synwatcher_cti.jsonl"
    fields:
      event.dataset: "n0z0.synwatcher"
      event.category: "network"
    parsers:
      - ndjson:
          target: ""
          overwrite_keys: true

  - type: filestream
    id: n0z0-scp
    paths:
      - "C:/ProgramData/n0z0/logs/scp_cti.jsonl"
    fields:
      event.dataset: "n0z0.scp"
      event.category: "authentication"
    parsers:
      - ndjson:
          target: ""
          overwrite_keys: true

  - type: filestream
    id: n0z0-classroot
    paths:
      - "C:/ProgramData/n0z0/logs/classroot_cti.jsonl"
    fields:
      event.dataset: "n0z0.classroot"
      event.category: "web"
    parsers:
      - ndjson:
          target: ""
          overwrite_keys: true

  - type: filestream
    id: n0z0-lemes
    paths:
      - "C:/ProgramData/n0z0/logs/lemes_cti.jsonl"
    fields:
      event.dataset: "n0z0.lemes"
      event.category: "threat_intel"
    parsers:
      - ndjson:
          target: ""
          overwrite_keys: true

output.elasticsearch:
  hosts: ["https://siem-es.internal:9200"]
  index: "n0z0-cti-%{+yyyy.MM.dd}"
```

---

### B. Konfigurasi Vector.dev (`vector.yaml`)
Vector adalah log shipper berkinerja sangat tinggi berbasis Rust:

```yaml
sources:
  n0z0_logs:
    type: file
    include:
      - "C:/ProgramData/n0z0/logs/*_cti.jsonl"
    read_from: beginning

transforms:
  parse_json:
    type: remap
    inputs:
      - n0z0_logs
    source: |
      . = parse_json!(.message)
      .host.hostname = get_hostname!()
      .@timestamp = .timestamp

sinks:
  elasticsearch:
    type: elasticsearch
    inputs:
      - parse_json
    endpoint: "https://elasticsearch.company.internal:9200"
    mode: bulk
    index: "soc-deception-%Y.%m.%d"
```

---

### C. Ringkasan Eksekusi Cepat Analis SOC (Quick Cheat-Sheet)

```powershell
# 1. Tes koneksi CacheDB
.\cachedb.exe -ping

# 2. Lihat seluruh aktor aktif di memori
.\cachedb.exe -actors

# 3. Investigasi profil mendalam IP tertentu
.\cachedb.exe -actor 198.51.100.25

# 4. Generate daftar IP penyerang untuk firewall
.\cachedb.exe -blocklist -out blocklist.txt

# 5. Ekspor seluruh intelijen ke STIX 2.1 JSON
.\cachedb.exe -export-stix -out threat_stix21.json

# 6. Stream log CTI secara bersamaan
Get-Content -Wait -Tail 20 .\lemes\lemes_cti.jsonl, .\ClassRoot\classroot_cti.jsonl, .\scp\scp_cti.jsonl, .\synwatcher\synwatcher_cti.jsonl
```