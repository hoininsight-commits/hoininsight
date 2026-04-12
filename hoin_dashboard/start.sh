#!/bin/bash
# HOIN 운영자 대시보드 시작 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

PORT=${PORT:-8888}

echo "HOIN 운영자 대시보드 시작"
echo "  주소: http://localhost:$PORT"
echo "  종료: Ctrl+C"
echo ""

# 브라우저 자동 실행 (macOS)
sleep 1 && open "http://localhost:$PORT" &

cd "$PROJECT_ROOT"
PORT=$PORT python3 hoin_dashboard/server.py
