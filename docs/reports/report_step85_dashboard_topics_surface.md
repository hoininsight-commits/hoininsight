# report_step85_dashboard_topics_surface.md

## 1. 개요
엔진이 선정한 Top-1 Topic을 정적 JSON 파일로 내보내고(Export), 이를 GitHub Pages 대시보드에서 직접 확인할 수 있도록 UI를 연결하였습니다. 
이제 런타임 객체에 의존하지 않고 `docs/dashboard/topics/` 아래의 데이터를 소스로 하여 안정적인 화면 노출이 가능합니다.

## 2. GitHub Pages 접속 정보
- **대시보드 URL**: [https://hoininsight-commits.github.io/HoinInsight/dashboard/](https://hoininsight-commits.github.io/HoinInsight/dashboard/)
- **확인 방법**: 최상단 "🟣 오늘의 TOP-1 핵심" 카드를 확인하십시오. (Static JSON Source 적용 완료)

## 3. 생성 및 수정 파일 리스트
- `src/dashboard/topic_exporter.py` [NEW]: 엔진 결과를 정적 JSON으로 변환/저장
- `src/engine.py` [MODIFY]: 파이프라인 끝에 `TopicExporter` 실행 단계 추가
- `src/dashboard/dashboard_generator.py` [MODIFY]: 정적 JSON 소스를 읽어 Top-1 카드 렌더링하도록 수정
- `docs/dashboard/topics/index.json` [NEW]: 전체 토픽 인덱스 파일
- `docs/dashboard/topics/items/YYYY-MM-DD__top1.json` [NEW]: 개별 날짜별 상세 토픽 데이터
- `verify_step85_dashboard_topics_surface.py` [NEW]: Step 85 검증 스크립트

## 4. 실산출물 JSON 예시 (docs/dashboard/topics/items/2026-01-27__top1.json)
```json
{
  "topic_id": "STRUCT_20260127_signal_f",
  "date": "2026-01-27",
  "rank": 1,
  "title": "Global Semiconductor Alliance mandates new supply chain standard for 2026, forcing all member firms to comply with immediate effect.",
  "summary": [
    "구조적 재정의 패턴 감지: '' 키워드 또는 프레임 매칭. 시장 인식 변화 구간."
  ],
  "why_now": {
    "type": "Mechanism Activation",
    "anchor": "Detected Pattern",
    "evidence": [
      "signal_fact_signal_test"
    ]
  },
  "badges": {
    "intensity": "STRIKE",
    "rhythm": "STRUCTURE_FLOW",
    "scope": "SINGLE",
    "lock": true,
                "rejected": false
  },
  "entities": [],
  "source_refs": [
    "data/ops/structural_top1_today.json"
  ]
}
```

## 5. 검증 결과
### 로컬 검증
- `python3 verify_step85_dashboard_topics_surface.py` 실행 결과:
  - ✅ index.json 존재 및 형식 확인
  - ✅ top1.json 필수 키(date, rank, title, why_now, badges) 존재 확인
  - ✅ dashboard/index.html 내 Top-1 섹션 포함 확인
- `python3 -m src.dashboard.dashboard_generator` 실행 시 `[Step 85] Using static Top-1 from ...` 로그 확인 완료

### GitHub Actions 확인 포인트
- 파이프라인 실행 시 `topic_exporter: ok` 로그가 나오는지 확인하십시오.
- `Generate Dashboard (Update)` 단계에서 `Using static Top-1` 메시지가 출력되는지 확인하십시오.
- `gh-pages` 브랜치에 `docs/dashboard/topics/` 폴더가 포함되어 푸시되는지 확인하십시오.
