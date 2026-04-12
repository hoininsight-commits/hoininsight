# WORKING-CONTEXT — 운영 상태 & 상세 컨텍스트

> CLAUDE.md의 상세 보완 문서. 현재 운영 상태와 JSON 스키마 정의.

## 리팩토링 완료 (2026-04-11)
- 1차: 47개 파일 삭제 (커밋 ad71023ab) — 백업파일·에러테스트·구형보고서·remote_verify 제거
- 2차: 루트 임시 파일 7개 삭제 + artifacts(62MB)·exports·github-pages(66MB) 삭제 + data_outputs → archive/legacy_data 이동
- pytest: 251/261 통과 (에러 0)
- 남은 FAILED 10개: 로직 불일치 (AGENT-04,05 활성화 후 처리 예정)
- 삭제 금지 확인: registry/ 광범위 사용 중 (src/ 전체에서 참조)

## 현재 운영 상태 (2026-04-09 기준)

| 항목 | 상태 |
|------|------|
| Gemini API 키 | 재발급 필요 (free tier quota 0 → billing 없는 새 프로젝트) |
| AGENT-01~03 | 정상 작동 |
| AGENT-04, 05 | Gemini API 키 대기 중 |
| AGENT-06 | 정상 작동 |
| GitHub Actions | `.github/workflows/daily_hoin_engine.yml` — AGENT-04,05 주석 처리 상태 |
| GitHub Pages | `main → /docs` 서빙 — v2 대시보드 (4구역 다크테마) |

## JSON 스키마 (절대 변경 금지)

### today_signal.json
`date, topic, strength, content_type, filters_hit, level2_chain, is_republish, urgency`

### today_analysis.json
`date, topic, three_lens_analysis(money_flow/structural_change/policy_direction), level2_chain, historical_reference, risk_factors, check_points`

### today_stocks.json
`date, topic_signal, stocks(ticker/name/sector/impact/reason)`

### content_log.json
`contents[]`: `id, date, type, title, signal_strength, is_republish, status`

## 데이터 경로 구조
```
data/raw/YYYYMMDD/market.json
data/signals/YYYYMMDD/today_signal.json
data/signals/YYYYMMDD/candidates.json
data/analysis/YYYYMMDD/today_analysis.json
data/analysis/YYYYMMDD/today_stocks.json
data/scripts/YYYYMMDD/longform_script.md
data/history/signal_log.json
data/history/content_log.json
dashboard/today_data.json       ← publisher가 최종 생성
```

## docs/ 경로 (GitHub Pages)
`docs/`는 `dashboard/`와 동기화. fetch 경로:
- `dashboard/today_data.json`
- `data/history/signal_log.json`
- `data/signals/YYYYMMDD/candidates.json`

## Gemini API 전환 이력
- 기존: `google.generativeai` (deprecated)
- 현재: `from google import genai` (`google-genai>=1.0.0`)
- 클라이언트: `genai.Client(api_key=...)` → `client.models.generate_content(model=..., contents=..., config=...)`
- 파일: `src/core/gemini_client.py` (ClaudeClient → GeminiClient 위임)

## Git 충돌 대응 패턴
원격 자동화 커밋과 충돌 시:
```bash
git stash
git pull --rebase
# 충돌 시: git checkout --ours [file] && git add [file] && git rebase --continue
git push
git stash pop
```
