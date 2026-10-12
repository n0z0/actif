#!/usr/bin/env bash
set -e

echo "=========================================================="
echo " ACTIF Ecosystem - Master Installer (5 Deception Daemons)"
echo "=========================================================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPS=("cachedb" "synwatcher" "scpd" "lemes" "ClassRoot")

for APP in "${APPS[@]}"; do
    INSTALLER="$ROOT_DIR/$APP/install.sh"
    if [ -f "$INSTALLER" ]; then
        echo -e "\n[*] Menjalankan installer $APP..."
        bash "$INSTALLER" || {
            echo "[!] Mencoba kompilasi lokal via go build..."
            cd "$ROOT_DIR/$APP" && go build -o "/usr/local/bin/$(echo "$APP" | tr '[:upper:]' '[:lower:]')" .
        }
    fi
done

echo -e "\n=========================================================="
echo " [SUKSES] Seluruh 5 Daemon Siap Digunakan Secara Global!"
echo "=========================================================="
echo "   1. cachedb -port 50051 -ttl 36000"
echo "   2. synwatcher -logfile synwatcher_cti.jsonl"
echo "   3. scpd"
echo "   4. lemes -port :50505 -ctilog lemes_cti.jsonl"
echo "   5. classroot"
