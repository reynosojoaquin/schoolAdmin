#!/bin/bash
set -e

SERVER="joaquin@192.168.60.3"
REMOTE_BASE="/srv/centro/schooladmin"
SERVICE="schooladmin"
VENV="/srv/centro/schooladmin/venv"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMIT=$(git -C "$SCRIPT_DIR" rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RELEASE="${TIMESTAMP}-${COMMIT}"
TARFILE="$SCRIPT_DIR/.release-${COMMIT}.tar.gz"

echo "=== SchoolAdmin Deploy ==="
echo "Commit: ${COMMIT}"
echo "Release: ${RELEASE}"
echo ""

echo "[1/7] Creando tarball..."
git -C "$SCRIPT_DIR" archive --format=tar.gz -o "$TARFILE" HEAD
echo "OK"

echo "[2/7] Subiendo al servidor..."
scp "$TARFILE" "${SERVER}:/tmp/schooladmin-release.tar.gz"
echo "OK"

echo "[3/7] Extrayendo release..."
ssh "$SERVER" bash -s <<REMOTE
set -e
sudo mkdir -p ${REMOTE_BASE}/releases/${RELEASE}
sudo tar -xzf /tmp/schooladmin-release.tar.gz -C ${REMOTE_BASE}/releases/${RELEASE}
echo ${RELEASE} | sudo tee ${REMOTE_BASE}/releases/${RELEASE}/RELEASE_COMMIT > /dev/null
rm -f /tmp/schooladmin-release.tar.gz
REMOTE
echo "OK"

echo "[4/7] Creando symlink..."
ssh "$SERVER" "sudo ln -sfn ${REMOTE_BASE}/releases/${RELEASE} ${REMOTE_BASE}/current"
echo "OK"

echo "[5/7] Migraciones..."
ssh "$SERVER" "sudo bash -c 'cd ${REMOTE_BASE}/current && ${VENV}/bin/python manage.py migrate --noinput'"
echo "OK"

echo "[6/7] Static files..."
ssh "$SERVER" "sudo bash -c 'cd ${REMOTE_BASE}/current && ${VENV}/bin/python manage.py collectstatic --noinput 2>&1 | tail -1'"
echo "OK"

echo "[7/7] Reiniciando servicio..."
ssh "$SERVER" "sudo systemctl restart ${SERVICE} && sudo systemctl status ${SERVICE} --no-pager | head -8"
echo ""

rm -f "$TARFILE"
echo "=== Deploy completado: ${RELEASE} ==="
