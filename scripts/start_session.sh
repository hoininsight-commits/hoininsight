#!/bin/bash
# ============================================================
# HOIN Insight — 세션 시작 스크립트
# 사용법: bash scripts/start_session.sh
# 목적: git pull + 최신 HANDOFF 요약 출력으로 즉시 작업 준비
# ============================================================

set -e

# 색상 정의
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   HOIN Insight — 세션 시작 준비 중...           ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: 경로 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
echo -e "${CYAN}📂 프로젝트 경로: $PROJECT_ROOT${NC}"

# Step 2: Git Pull
echo ""
echo -e "${YELLOW}🔄 [Step 1/3] 최신 코드 동기화 중...${NC}"
if git pull origin main 2>&1; then
    echo -e "${GREEN}✅ git pull 완료${NC}"
else
    echo -e "${RED}⚠️  git pull 실패. 로컬 상태로 계속 진행합니다.${NC}"
fi

# Step 3: HANDOFF 최신 블록 추출
echo ""
echo -e "${YELLOW}📋 [Step 2/3] 최신 HANDOFF 읽는 중...${NC}"
HANDOFF_FILE="$PROJECT_ROOT/docs/HANDOFF_FINAL.md"

if [ -f "$HANDOFF_FILE" ]; then
    echo ""
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}  📌 최신 세션 요약 (HANDOFF_FINAL.md 끝 블록)${NC}"
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    # 마지막 세션 블록 추출 (마지막 [세션 업데이트] 블록부터)
    tail -n 200 "$HANDOFF_FILE" | grep -A 1000 "\[세션 업데이트\]" | tail -n +1
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${RED}❌ HANDOFF_FINAL.md 없음: $HANDOFF_FILE${NC}"
fi

# Step 4: 환경 상태 점검
echo ""
echo -e "${YELLOW}🔍 [Step 3/3] 환경 상태 점검...${NC}"
echo ""

# .env 확인
if [ -f "$PROJECT_ROOT/.env" ]; then
    GEMINI_SET=$(grep -q "GEMINI_API_KEY=" "$PROJECT_ROOT/.env" && echo "✅" || echo "❌")
    DART_SET=$(grep -q "OPENDART_API_KEY=" "$PROJECT_ROOT/.env" && echo "✅" || echo "❌")
    ECOS_SET=$(grep -q "ECOS_API_KEY=" "$PROJECT_ROOT/.env" && echo "✅" || echo "❌")
    echo -e "  API 키 상태:"
    echo -e "    GEMINI_API_KEY   : $GEMINI_SET"
    echo -e "    OPENDART_API_KEY : $DART_SET"
    echo -e "    ECOS_API_KEY     : $ECOS_SET"
else
    echo -e "  ${RED}⚠️  .env 파일 없음 — API 키 설정 필요${NC}"
fi

# 오늘 날짜 데이터 확인
TODAY=$(date +%Y%m%d)
DATA_DIR="$PROJECT_ROOT/data/raw/$TODAY"
SIGNAL_FILE="$PROJECT_ROOT/data/signals/$TODAY/today_signal.json"

echo ""
echo -e "  오늘($TODAY) 데이터 상태:"
if [ -d "$DATA_DIR" ]; then
    FILE_COUNT=$(ls "$DATA_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
    echo -e "    수집 데이터 : ✅ ${FILE_COUNT}개 파일 존재"
else
    echo -e "    수집 데이터 : ❌ 없음 (수집 필요)"
fi

if [ -f "$SIGNAL_FILE" ]; then
    TOPIC=$(python3 -c "import json; d=json.load(open('$SIGNAL_FILE')); print(d.get('topic','N/A')[:50])" 2>/dev/null || echo "읽기 실패")
    echo -e "    오늘 신호   : ✅ $TOPIC..."
else
    echo -e "    오늘 신호   : ❌ 없음 (파이프라인 실행 필요)"
fi

# 대시보드 서버 상태 확인
if lsof -i :8888 > /dev/null 2>&1; then
    echo -e "    대시보드    : ✅ http://localhost:8888 실행 중"
else
    echo -e "    대시보드    : ⚠️  미실행 (python3 hoin_dashboard/server.py 로 시작)"
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   ✅ 준비 완료 — 안티에게 작업 지시하세요!      ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}💡 파이프라인 실행 순서:${NC}"
echo "   PYTHONPATH=. python3 src/agents/collector.py"
echo "   PYTHONPATH=. python3 src/agents/detector.py"
echo "   PYTHONPATH=. python3 src/agents/writer.py"
echo "   python3 hoin_dashboard/server.py"
echo ""
