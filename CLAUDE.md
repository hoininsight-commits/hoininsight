# HOIN Insight — Claude Code 기본 지침
# v1.0 | 2026-04-20

## 프로젝트 개요
매일 06:00 KST 자동 실행되는 경제사냥꾼 스타일
유튜브 스크립트 생성 AI 파이프라인

## 로컬 경로
- 집: ~/dev/HoinInsight
- 회사: ~/Antigravity/hoininsight

## GitHub
- Repo: hoininsight-commits/hoininsight
- Dashboard: hoininsight-commits.github.io/hoininsight/

## 핵심 문서 위치
- 현재 상태: docs/HANDOFF.md
- 경제사냥꾼 DNA: docs/dna/ECONOMIC_HUNTER.md
- 파이프라인 규칙: docs/dna/PIPELINE_RULES.md
- 에이전트 설계: docs/agents/

## 절대 규칙
- git push로 파이프라인 검증 금지
  (push 시 publish만 단독 실행됨)
- 파이프라인 실행: Actions UI → workflow_dispatch만
- API 키 값 출력 금지
- 파일 삭제는 목록 확인 후 별도 승인
- 로컬 테스트만으로 PASS 금지

## 작업 시작 전 반드시 확인
1. docs/HANDOFF.md 읽기 (현재 상태 파악)
2. 관련 에이전트 MD 읽기 (수정 작업 시)
3. 스크립트 관련 작업 시 docs/dna/ECONOMIC_HUNTER.md 읽기
