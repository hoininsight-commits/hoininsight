# 경제사냥꾼 유튜브 에이전트 장애 진단 보고서

**작성일**: 2026-04-18  
**대상**: 경제사냥꾼 수집 에이전트 (`LearnerAgent`, `YouTubeWatcher`)  
**진단자**: 안티 (Claude Code)

---

## 1) 현재 구현 상태 요약

현재 레포지토리 내에는 유튜브 수집 기능을 수행하는 에이전트가 **두 가지 버전으로 이원화**되어 존재하고 있습니다.

- **Agent A (기존)**: `src/agents/learner.py`
  - `run_learner.py`를 통해 호출되며, GitHub Actions(`learner_pipeline.yml`)에서 사용되는 주 플랫폼입니다.
  - `yt-dlp`를 사용하여 채널 페이지를 직접 파싱하고 자막을 추출합니다.
- **Agent B (신규/실험)**: `src/ui/narratives/youtube_watcher.py`
  - RSS 피드를 통해 신규 영상을 감지하며 `transcript_ingestor.py`와 연동됩니다.
  - 현재 시스템 가드에 의해 실행이 차단되어 있습니다.

| 항목 | Agent A (Learner) | Agent B (Watcher) |
|------|-------------------|-------------------|
| **파일 경로** | `src/agents/learner.py` | `src/ui/narratives/youtube_watcher.py` |
| **감지 방식** | 채널 페이지 크롤링 (yt-dlp) | RSS Feed (Atom XML) |
| **추출 방식** | Transcript API + yt-dlp | Transcript API + yt-dlp |
| **저장 위치** | `data/learning/scripts/` | `data/narratives/raw/youtube/` |
| **현재 상태** | **실행되나 수집 실패** | **실행 자체가 차단됨** |

---

## 2) 실행 경로 분석

### Agent A (Learner) 경로
1. `src/run_learner.py` (Entry)
2. `LearnerAgent.run()`
3. `fetch_video_list()`: `@경제사냥꾼/videos` 페이지 파싱
4. `_already_collected()`: `data/learning/collected_index.json` 대조
5. `extract_transcript()`: `youtube-transcript-api` 시도 후 `yt-dlp` 우회 시도
6. `save_script()`: `data/learning/scripts/YYYYMMDD`에 저장

### Agent B (Watcher) 경로
1. `src/ui/narratives/youtube_watcher.py` (Entry)
2. `check_learning_enabled()`: **환경변수 검사 (여기서 차단)**
3. `fetch_rss_feed()`: XML RSS 수집
4. `parse_feed_entries()`: 영상 ID 추출
5. `ingest_transcript()`: `transcript_ingestor.py` 호출

---

## 3) 재현 결과

### 현상 1: Agent B (Watcher) 가드 차단
- **명령어**: `python3 -m src.ui.narratives.youtube_watcher`
- **로그**: `[GUARD] ENABLE_LEARNING is false or unset. Phase 31 execution skipped.`
- **결과**: 아무 작업 없이 종료 (Exit 0).

### 현상 2: Agent A (Learner) 수집 실패
- **명령어**: `python3 src/run_learner.py`
- **로그**: 
  - `[Engine1] API 실패 또는 차단됨: YouTube is blocking requests from your IP. (HTTP 429)`
  - `[Engine2] yt-dlp 수집 실패: ERROR: Unable to download video subtitles for 'ko': HTTP Error 429`
- **결과**: 영상 목록은 가져오나 자막 추출 단계에서 전량 실패.

---

## 4) 고장 원인 판정

### **[한 줄 요약]**
> **"YouTube의 IP 기반 봇 차단(HTTP 429)이 발생했으나, 이를 우회할 인증 쿠키(`youtube_cookies.txt`)가 부재하며, 신규 에이전트는 환경변수 가드에 막혀 잠든 상태임."**

### 세부 원인
1. **차단 (Blocking)**: YouTube가 GitHub Actions 및 클라우드 IP의 자막 요청을 봇으로 간주하여 전면 차단 중입니다.
2. **인증 부재 (Auth Missing)**: `LearnerAgent`는 `youtube_cookies.txt`를 사용하도록 구현되어 있으나, 현재 실행 환경에 실제 쿠키 파일이 없어 비로그인 상태로 요청을 보내고 있습니다.
3. **가드 설정 (Env Guard)**: `YouTubeWatcher`는 `ENABLE_LEARNING=true` 설정 없이는 작동하지 않도록 설계되어 있어 자동화 라인에서 제외된 상태입니다.
4. **경로 파편화 (Path Inconsistency)**: 두 에이전트가 서로 다른 경로에 데이터를 저장하고 있어, 한쪽에서 수집한 영상이 다른 쪽에서는 "신규"로 오판되는 구조적 비효율이 존재합니다.

---

## 5) 권고안

### 즉시 조치 (Immediate)
- **쿠키 갱신**: 유효한 YouTube 세션 쿠키를 `youtube_cookies.txt`로 생성하여 레포지토리에 적용(또는 Secret 업데이트).
- **환경변수 활성화**: GitHub Actions 환경 설정에 `ENABLE_LEARNING: true` 추가.

### 안정화 조치 (Stabilization)
- **구조 단일화**: RSS 기반 감지(Watcher)가 훨씬 안정적이므로, Watcher의 감지 로직을 LearnerAgent로 통합하거나 Watcher를 메인으로 승격.
- **경로 통일**: 모든 유튜브 수집물은 `data/raw/youtube/` 경로로 통일하여 관리.

### 구조 개선 조치 (Architectural)
- **멤버십 대응**: 멤버십 영상은 `yt-dlp`에 쿠키 전달이 필수적이므로, `transcript_ingestor.py`에도 쿠키 지원 로직 강화.
- **에러 핸들링**: 429 에러 발생 시 단순 Skip이 아니라 명시적 Alert를 발생시키도록 수정.

---

## 6) 최종 판정

**[판정] 인증/외부제약 해결 전 복구 불가**
- 자막 수집 실패의 핵심인 HTTP 429는 코드 수정이 아닌 **유효한 쿠키 주입**으로만 해결 가능합니다.
- 다만, `ENABLE_LEARNING` 가드 해제 및 저장 경로 통일 등의 **코드적 정비는 즉시 가능**합니다.
