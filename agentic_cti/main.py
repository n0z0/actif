import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Muat environment variables dari .env
load_dotenv()

def ensure_dirs():
    os.makedirs("reports", exist_ok=True)

def run_investigation(target_ip: str):
    """Menjalankan investigasi multi-agent CTI terhadap IP penyerang tertentu."""
    print("=" * 70)
    print("🚀 [ACTIF] Memulai Orkestrasi AI-Powered Cyber Threat Intelligence")
    print(f"🎯 Target Investigasi IP: {target_ip}")
    print("=" * 70)

    from crew import ActifCTICrew

    inputs = {
        "target_ip": target_ip,
    }

    crew_instance = ActifCTICrew()
    result = crew_instance.crew().kickoff(inputs=inputs)

    print("\n" + "=" * 70)
    print("✅ [ACTIF] Investigasi Multi-Agent Selesai!")
    print(f"📄 Laporan tersimpan di: reports/latest_cti_incident_report.md")
    print("=" * 70)
    print(result)

def demo_mode():
    """Menjalankan demo investigasi menggunakan simulasi target IP."""
    target_ip = "198.51.100.25"
    print("🧪 [DEMO MODE] Menjalankan simulasi skenario serangan end-to-end:")
    print("   1. L4 SYN Port Scan (synwatcher)")
    print("   2. L7 SFTP Authentication & File Upload (scp)")
    print("   3. L7 WebRTC LAN IP Leak (ClassRoot)")
    print("   4. L7 Canary Document Beacon & Token Attribution (lemes)")
    run_investigation(target_ip)

def main():
    ensure_dirs()

    parser = argparse.ArgumentParser(
        description="Actif - AI-Powered Cyber Threat Intelligence Multi-Agent Orchestrator (CrewAI)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Perintah yang tersedia")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Jalankan investigasi terhadap IP tertentu")
    run_parser.add_argument("--ip", required=True, help="IP target penyerang untuk diinvestigasi")

    # Command: demo
    subparsers.add_parser("demo", help="Jalankan demonstrasi simulasi skenario serangan")

    args = parser.parse_args()

    if args.command == "run":
        run_investigation(args.ip)
    elif args.command == "demo":
        demo_mode()
    else:
        # Default jika tanpa argumen: tampilkan help
        parser.print_help()

if __name__ == "__main__":
    main()
