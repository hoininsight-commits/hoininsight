# /fix — HOIN 자주 발생하는 문제 해결

## 1. Gemini API 오류
**429 RESOURCE_EXHAUSTED (limit: 0)**
- 원인: billing 활성화된 프로젝트의 free quota = 0
- 해결: Google AI Studio → 새 프로젝트 생성 (billing 없음) → 새 API 키 발급 → `.env` 업데이트

**403 PERMISSION_DENIED**
- 원인: 대화에 키가 노출되어 자동 차단
- 해결: Google Cloud Console → API 키 삭제 → 새 키 발급

## 2. ModuleNotFoundError: No module named 'src'
- 원인: 프로젝트 루트가 아닌 다른 디렉토리에서 실행
- 해결: `cd /Users/jihopa/.gemini/antigravity/scratch/HoinInsight` 후 실행

## 3. git push rejected
```bash
git stash
git pull --rebase
# 충돌 시:
git checkout --ours dashboard/index.html  # 우리 버전 채택
git add dashboard/index.html
git rebase --continue
git push
git stash pop
```

## 4. Gemini SDK 임포트 오류
- 구버전 `google.generativeai` → 신버전 `from google import genai`
- `src/core/gemini_client.py` 상단 확인

## 5. pytest 실패
```bash
cd /Users/jihopa/.gemini/antigravity/scratch/HoinInsight
python -m pytest tests/ -v
# 픽스처 확인: tests/fixtures/
```

## 6. 대시보드 데이터 없음
- `python -m src.agents.publisher` 실행
- 또는 수동으로 `dashboard/today_data.json` 확인
