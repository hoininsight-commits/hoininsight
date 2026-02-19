#!/usr/bin/env python3
import os
import requests
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().strip().split('\n'):
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

message = """📋 **HOIN Insight 작업 인계 (2026-02-06)**

✅ **최근 작업 (IS-113: Operator Narrative Order Layer)**
- **구현 완료:**
  - `operator_narrative_order_builder.py`: 결정론적 1 Long + N Shorts 구조 확정.
  - `render.js` 개편: Decision Zone -> Content Package -> Support Zone 순서 렌더링.
  - **Safety:** Evidence Whitelist 및 `undefined` 가드 적용.

📊 **시스템 상태**
- **Verification:** `tests/verify_is113_operator_narrative_order.py` PASSED (Shorts Count: 1)
- **Artifacts:** `operator_narrative_order.json` 정상 생성됨.

🎯 **다음 작업 (Next Steps)**
1. **[IS-114] Integration Verification:** 전체 파이프라인 통합 테스트.
2. **Dashboard Polish:** 모바일 반응형 및 UI 디테일 조정.
3. **Deployment:** Mainnet 배포 준비.

📁 **프로젝트 위치**
`/Users/jihopa/.gemini/antigravity/scratch/HoinInsight`

📝 **이어하기 프롬프트 (복사해서 사용)**
--------------------------------------------------
Hoin Insight 프로젝트 이어하기.
현재 상태: IS-113 Operator Narrative Order Layer 구현 및 검증 완료.
마지막 작업:
1. `operator_narrative_order_builder.py`로 결정론적 콘텐츠 구조 생성.
2. `render.js` 수정으로 Decision Zone 최우선 렌더링.
3. 데이터 검증(Whitelist, Undefined Check) 통과.

다음 목표: IS-114 통합 검증 및 대시보드 UI 폴리싱.
--------------------------------------------------
"""

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
data = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": message,
    "parse_mode": "Markdown"
}

try:
    print(f"Sending message to Chat ID: {TELEGRAM_CHAT_ID}...")
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("✅ 텔레그램 메시지 전송 성공!")
    else:
        print(f"❌ 전송 실패: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ 오류 발생: {e}")
