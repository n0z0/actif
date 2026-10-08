# Cyber Threat Intelligence (CTI) Briefing Notes

**Klasifikasi Dokumen:** `TLP:CLEAR`  
**Seri Briefing:** `CTI-FOUNDATIONS-2026`  
**Target Audiens:** SOC L1–L3, Threat Hunter, Security Leadership  
**Berkas Presentasi:**
- [CTI_Fundamentals_Presentation.pptx](file:///c:/Users/Windows%2011%20Pro/Documents/joe/n0z0/CTI_Fundamentals_Presentation.pptx)
- [CTI_Fundamentals_Presentation.pdf](file:///c:/Users/Windows%2011%20Pro/Documents/joe/n0z0/CTI_Fundamentals_Presentation.pdf)

---

## Ringkasan Struktur 12 Slide (Editorial & Practitioner-Standard)

### Slide 01: Formal Briefing Cover
- **Topik:** Cyber Threat Intelligence (CTI): Prinsip Operasional, Model Analisis, dan Ekosistem Pertahanan Berbasis Ancaman.
- **Tujuan:** Menetapkan standar pemahaman CTI dari sudut pandang penegakan keamanan praktis tanpa klise atau jargon kosong.

### Slide 02: Konteks Industri & Masalah Lapangan (The Asymmetric Dilemma)
- **Fakta Pertahanan Reaktif:**
  - *Median Dwell Time Tinggi:* Penyerang berada berminggu-minggu di dalam perimeter sebelum terdeteksi secara tidak sengaja.
  - *Alert Fatigue Kronis:* 5.000–15.000 alarm/hari membuat 60% indikator diabaikan.
  - *Kerugian Nyata:* Menunggu alarm SIEM berbunyi berarti kode berbahaya telah dieksekusi atau proses enkripsi ransomware telah berjalan.
- **Pergeseran ke Threat-Informed Defense:** Visibilitas eksternal, fokus prioritas pada TTPs yang relevan dengan sektor bisnis, dan intervensi sejak fase awal rantai serangan.

### Slide 03: Taksonomi & Definisi: Data Mentah vs Informasi vs CTI
- **Data Mentah:** Log atomik tanpa konteks (contoh: log koneksi firewall dari IP publik pada jam tertentu).
- **Informasi:** Data terstruktur yang menunjukkan pola teknis (contoh: pemindaian SYN ke 85 port dalam 3 detik dilanjutkan percobaan brute force).
- **Intelijen (CTI):** Temuan terverifikasi yang mengungkap pelaku, motif, kampanye, dan menuntun tindakan mitigasi langsung (contoh: IP merupakan exit-node APT29 yang aktif menyasar CVE tertentu pada sektor finansial).

### Slide 04: Empat Tingkatan Konsumen CTI (The 4 Tiers of Intelligence)
1. **Strategic CTI:** Untuk CISO & Direksi (tren risiko bisnis, motif geopolitik, alokasi anggaran keamanan).
2. **Operational CTI:** Untuk SOC Manager & Threat Hunter (profil kelompok ancaman/APT, kampanye aktif, jendela waktu operasi).
3. **Tactical CTI:** Untuk Detection Engineer & SOC L2/L3 (pemetaan taktik MITRE ATT&CK, aturan Sigma, dan rule YARA).
4. **Technical CTI:** Untuk SOC L1 & Admin Perimeter (IoC atomik: hash malware, domain C2, dan blacklist firewall).

### Slide 05: Metodologi Operasional: Siklus Hidup CTI 6 Tahap
1. **Planning & Direction:** Menetapkan *Priority Intelligence Requirements* (PIR) berdasarkan aset paling kritis organisasi.
2. **Collection:** Menarik data dari telemetri internal (honeypot, sensor L4, log proxy) dan eksternal (OSINT, ISAC, dark web).
3. **Processing:** Normalisasi data, kalkulasi checksum kriptografis, deduplikasi log, dan lookup rDNS.
4. **Analysis & Production:** Sintesis korelasi ancaman, verifikasi tingkat keyakinan (*confidence score*), dan penyusunan draf mitigasi.
5. **Dissemination:** Distribusi berkas terstruktur ke pihak yang tepat (STIX/TAXII ke SIEM/EDR, executive brief ke direksi).
6. **Feedback & Review:** Evaluasi akurasi mitigasi untuk mengkalibrasi ulang siklus berikutnya.
- *Catatan Praktisi:* 75% kegagalan program CTI terjadi karena organisasi langsung membeli feed mahal pada tahap Koleksi tanpa menetapkan PIR yang jelas pada tahap Planning.

### Slide 06: Model Analisis Ancaman: The Diamond Model of Intrusion
- **Aksioma Inti:** Setiap intrusi menghubungkan **Adversary (Pelaku)** yang mengerahkan **Capability (Alat/Senjata)** melalui **Infrastructure (Saluran/Jaringan)** terhadap sebuah **Victim (Sasaran/Korban)**.
- **Dua Sumbu Kontekstual:**
  - *Sumbu Sosial-Politik:* Menghubungkan motif pelaku dengan nilai aset korban.
  - *Sumbu Teknologi:* Menghubungkan kapabilitas exploit dengan infrastruktur command-and-control.

### Slide 07: Cyber Kill Chain & Titik Intervensi Defensif
- Mengurai 7 tahapan serangan: *Reconnaissance $\to$ Weaponization $\to$ Delivery $\to$ Exploitation $\to$ Installation $\to$ C2 Channel $\to$ Actions on Objectives*.
- **Prinsip Leverage Defensif:** Menggagalkan penyerang pada 1 tahap awal mana pun akan membatalkan seluruh operasi mereka dengan biaya mitigasi minimal. Sebaliknya, intervensi di tahap akhir berarti kerugian bisnis telah terjadi.

### Slide 08: Pyramid of Pain (David Bianco): Mengukur Biaya Hambatan Lawan
- **TTPs (Tough):** Memaksa penyerang merombak total metodologi peretasan dan melatih ulang personel.
- **Tools (Challenging):** Memaksa lawan merekayasa ulang exploit builder atau membeli software baru.
- **Artifacts (Annoying):** Membongkar nama author dokumen, PDB compilation path, atau pola User-Agent.
- **Domain Names (Simple):** Penyerang cukup mendaftarkan domain baru seharga beberapa dolar.
- **IP Addresses (Easy):** Penyerang cukup berganti node VPN atau server proxy sekali pakai.
- **Hash Values (Trivial):** Menambahkan 1 spasi pada kode malware langsung mengubah seluruh nilai hash tanpa usaha dari pihak lawan.

### Slide 09: Active Defense: Arsitektur Deception & Tripwire
- **Penyebaran Honeytoken:** Menempatkan kredensial palsu, dokumen umpan, dan port rahasia pada titik non-produksi.
- **Zero False Positive:** Tidak ada alasan bagi staf legal mengakses aset umpan. Akses apa pun 100% membuktikan keberadaan anomali atau intrusi.
- **Observasi In-Situ:** Memantau langsung perintah terminal dan taktik lawan di lingkungan terkontrol untuk menghasilkan IoC berkeyakinan tinggi (*high-fidelity*).

### Slide 10: Metodologi Atribusi & De-Anonymization
- **WebRTC Candidate Leak:** Mengekstrak host IP lokal di balik proxy/VPN penyerang melalui negosiasi sesi browser.
- **L4 SYN Stack Fingerprint:** Menghitung karakteristik TCP awal (TTL, Window Size, MSS, urutan options) untuk mengidentifikasi tipe OS dan tool scanning.
- **Artefak Dokumen & Binary:** Menganalisis metadata author dokumen Office, debugging paths (PDB), dan zona waktu.
- **Sinkronisasi Canary Beacon:** Memanfaatkan kesalahan operasional (OPSEC failure) ketika dokumen umpan dibuka tanpa VPN aktif.

### Slide 11: Interoperabilitas Industri: STIX 2.1 & TAXII
- **STIX 2.1 (Data Layer):** Format JSON graf objek (SDO dan SRO) yang memetakan hubungan antara Threat Actor, Attack Pattern, Indicator, dan Identity.
- **TAXII 2.1 (Transport Layer):** Protokol HTTPS REST API untuk pertukaran intelijen otomatis (Channel & Collection model) antar-organisasi, sektor finansial, dan badan siber nasional secara aman.

### Slide 12: Evolusi Operasional: Otomasi & Multi-Agent CTI (Human-in-the-Loop)
- **Komparasi Efisiensi Triage:**
  - *Tradisional:* Analis manual membuka berbagai tab OSINT, mencari korelasi, dan mengetik tiket (memakan waktu 2–4 jam per insiden).
  - *Multi-Agent Pipeline:* Agen spesialis (Recon, DFIR, Atribusi, Strategi) membedah dan mengkorelasikan seluruh artefak dalam waktu kurang dari 30 detik.
  - *Human-in-the-Loop:* Analis manusia memegang kendali validasi akhir sebelum aturan isolasi dan pemblokiran perimeter dieksekusi.
