# Step 79 완료 보고서: ECONOMIC_HUNTER_TITLE_THUMBNAIL_INTENSITY_LAYER

## 1. Step 79 목적 요약 (Implementation Summary)

**EconomicHunterTitleThumbnailIntensityLayer**는 영상의 본문(Video Intensity)과 호흡(Video Rhythm)에 맞추어, 시청자의 시선을 끄는 제목(Title)과 썸네일(Thumbnail)의 '공격 강도'를 자동 결정하는 레이어입니다. 이 단계는 단순히 작명을 하는 것이 아니라, 시스템이 정한 강도에 따라 제목의 길이, 사용 단어, 구조적 제약을 강제하여 알고리즘 최적화와 브랜드 일관성을 동시에 확보합니다.

### 주요 역할:
- **공격 강도 동기화**: Video Intensity 레벨과 제목/썸네일 강도를 1:1로 동기화하여 메시지의 일관성 유지.
- **제작 가이드라인 강제**: 레벨별 제목 글자 수, 긴급 키워드 포함 여부, 썸네일 단어 수 등의 규칙을 Narrator에 전달.
- **파이프라인 최종화**: 모든 제작 의사 결정(Lock -> Intensity -> Rhythm -> Title Intensity)을 마친 후 Narrator가 최종 스크립트를 생성하도록 함.

## 2. Intensity 매핑 표 (Mapping Table)

| Video Intensity | Title & Thumbnail Intensity | 핵심 규칙 (Rules) |
| :--- | :--- | :--- |
| **FLASH** | **TITLE_INTENSITY_FLASH** | 12자 내외, 긴급 키워드(지금, 오늘 등) 필수, 단어 3~5개 썸네일 |
| **STRIKE** | **TITLE_INTENSITY_STRIKE** | 15~18자, 원인-결과 구조, 단어 4~6개 구조적 키워드 썸네일 |
| **DEEP_HUNT** | **TITLE_INTENSITY_DEEP** | 18~25자, 질문/설명형, 단어 5~7개 개념 키워드 썸네일 |

## 3. Reject 발생 사례 (Rejection Case)

- **사례**: 상위 레이어(Step 77)로부터 유효하지 않은 `video_intensity_level`이 전달되거나, 매핑 테이블에 없는 값이 입수된 경우.
- **처리**: "Title Intensity determination failed" 사유와 함께 토픽을 Reject 처리하며, 제목 강도가 확정되지 않은 토픽은 영상 제작 프로세스를 즉시 중단합니다.

## 4. 실제 생성 예시 (Example: FLASH)

- **분석 결과**: `Video Intensity: FLASH` $\rightarrow$ `Title Intensity: FLASH`
- **적용 규칙**: 12자 내외 + 긴급 키워드
- **생성된 제목 예시**: "**지금 연준 긴급 금리 동결, 시장 터졌다!**"
- **썸네일 문구 예시**: "연준 금리 동결 / 지금 당장 / 시장 충격"

## 5. 파이프라인 통합 검증 결과 (Pipeline Integration)

`engine.py`에서 다음의 최종 파이프라인 순서가 정상 작동함을 확인했습니다:
1. Step 74: Pre-Structural Signal
2. Step 72: WHY_NOW Trigger
3. Step 75: WHY_NOW Escalation
4. Step 76: Economic Hunter Topic Lock
5. Step 77: Video Intensity
6. Step 78: Video Rhythm
7. **Step 79: Title & Thumbnail Intensity (본 단계)**
8. EconomicHunterNarrator (모든 Intensity/Rhythm 데이터 바인딩 생성)

---
**보고서 종료**
