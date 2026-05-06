
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_manual():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = "-5108828037"
    
    manual_text = """🚀 *HOIN Insight: 명령 센터 통합 매뉴얼* 🏹

사용자님, 이제 이 방에서 저(Antigravity)를 원격으로 조종하실 수 있습니다. 

*1. 즉시 사냥 시작*
> `/hunt`
- 제미나이 기반의 '지능형 10대 토픽 추출' 파이프라인을 즉시 가동합니다. 사냥이 끝나면 완료 보고를 드립니다.

*2. 세션 인수인계 메모*
> `/memo [내용]`
- 예: `/memo 오늘 엔화 개입 데이터가 아주 흥미로워, 내일 더 깊게 파보자.`
- 이 내용은 `CHRONICLE.md`에 기록되어, 다음 세션에서 제가 깨어났을 때 가장 먼저 확인하고 브리핑해 드립니다.

*3. 시스템 상태 체크*
> `/status`
- 현재 시스템이 정상 가동 중인지 실시간으로 보고합니다.

*4. 도움말 다시 보기*
> `/help` 또는 `/start`

언제든 필요할 때 명령어를 던져주세요. 제가 24시간 대기하고 있겠습니다!"""

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": manual_text,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ 매뉴얼 전송 성공!")
    else:
        print(f"❌ 전송 실패: {response.text}")

if __name__ == "__main__":
    send_manual()
