
# 🧠 Phase 35: Reverse Engineering Agent (The Brain Thief)

## 1. 개요
Phase 35는 경쟁자(경제 사냥꾼 등)의 영상에서 **"그들이 사용한 로직과 데이터"를 역추적(Reverse Engineering)**하여, Hoin Insight의 로직(Baseline Signals, Anomaly Logic)에 없는 부분을 자동으로 감지하고 추가를 제안하는 **"자가 학습 루프(Self-Learning Loop)"** 모듈이다.

## 2. 핵심 목표
1.  **Transcript Analysis**: 영상의 자막(Transcript)을 다운로드 및 분석.
2.  **Logic Extraction**: 영상에서 주장하는 핵심 근거(Key Drivers) 추출. (예: "구리 재고가 줄어서 가격이 오를 것이다")
3.  **Gap Analysis**: 추출된 근거가 현재 우리 문서(`BASELINE_SIGNALS.md`, `DATA_COLLECTION_MASTER.md`)에 존재하는지 대조.
4.  **Auto-Proposal**: 누락된 로직이나 데이터가 있다면 `proposal_queue`에 **"신규 로직 추가 제안서"** 형식으로 자동 등록.

## 3. Workflow
1.  **Trigger**: `Phase 31-A (YouTube Watcher)`가 영상을 감지하고 Status가 `APPROVED`로 변경될 때.
2.  **Transcriber**: `youtube_transcript_api`를 사용하여 자막 추출 -> `data/raw/youtube/{video_id}/transcript.txt` 저장.
3.  **Analyzer (LLM)**: Transcript를 입력받아 아래 질문 수행:
    *   "이 유튜버가 결론을 내기 위해 근거로 든 지표는 무엇인가?"
    *   "그 지표와 논리 구조(A -> B)는 무엇인가?"
4.  **Validator**: 추출된 지표가 `docs/DATA_COLLECTION_MASTER.md`에 정의되어 있는지 문자열/유사도 검색.
5.  **Output**: `Proposal Generator`를 호출하여 `.md` 파일 생성.

## 4. 파일 구조
- `src/learning/transcript_fetcher.py`: 자막 다운로드 모듈
- `src/learning/logic_extractor.py`: LLM 기반 로직 추출 및 Gap 분석기
- `data/raw/youtube/{video_id}/transcript.txt`: 자막 원본
- `data/raw/youtube/{video_id}/extracted_logic.json`: 추출된 로직 구조

## 5. 기대 효과
이 모듈이 가동되면, 당신이 영상을 보고 "아, 저 지표도 봐야겠네"라고 생각하는 과정을 **AI가 대신 수행**하고, "이 지표 추가할까요?"라고 **제안**하게 된다.
