# IssueSignal Operator Dashboard Spec (IS-27)

## 1. 개요 (Overview)
IssueSignal 엔진의 실시간 상태를 시각화하는 정적 HTML 대시보드 사양이다. 복잡한 도구 없이 브라우저에서 즉시 엔진의 판단 결과와 차단 사유를 확인할 수 있도록 설계한다.

## 2. 핵심 원칙 (Core Principles)
1. **10-Second Read**: 대시보드를 열고 10초 이내에 오늘의 엔진 상황을 파악할 수 있어야 한다.
2. **Read-Only**: 대시보드는 엔진의 출력 파일을 읽기만 하며, 내부 로직에 영향을 주지 않는다.
3. **Extreme Robustness**: 특정 파일이나 데이터 필드가 누락되어도 페이지 렌더링이 중단되지 않는다. (Missing은 "-"로 표시)
4. **Static & Fast**: 의존성 없는 단일 HTML 파일로 생성되어 로컬이나 GitHub Pages에서 지연 없이 로딩된다.

## 3. 상태 컬러 코드 (Status Colors)
- **TRUST_LOCKED**: #10B981 (Emerald Green) - 즉시 발화 가능
- **TRIGGER / PRE_TRIGGER**: #3B82F6 (Blue) - 활성/관찰 상태
- **HOLD**: #F59E0B (Amber) - 보완 필요
- **REJECT / SILENT_DROP**: #EF4444 (Red) - 차단

## 4. 페이지 구성 (Page Sections)
1. **Header**: 현재 날짜, 엔진 구동 시각, 글로벌 상태(SUCCESS/FAIL).
2. **Summary Dashboard**: 상태별 카운트 (6종: TRUST_LOCKED, TRIGGER, PRE_TRIGGER, HOLD, REJECT, SILENT_DROP).
3. **Top Insights (LOCKED)**: 최상위 `TRUST_LOCKED` 카드 3개 (가장 큰 카드).
4. **Watchlist (PRE)**: 관찰 중인 `PRE_TRIGGER` 목록.
5. **Silent Queue (HOLD/REJECT)**: 발화되지 않은 이유와 최근 5건의 차단 로그.
6. **Timeline**: 최근 14일간의 발화 추이.

## 5. 데이터 입력 규약 (Data Input Contract)
- **Decision Cards**: `data/decision/*.json`
- **Ops Logs**: `data/ops/*reject*.json` 또는 `data/issuesignal/packs/*.yaml` (카운트용)
- **Memory**: `data/snapshots/memory/*.json`

## 6. 대비책 (Fallback Behavior)
- 데이터 파일 없음: "No data available today" 메시지 표시.
- 필드 누락: 해당 위치에 "`-`" 표시.
- 이미지/자산: 외부 의존성 배제, 모든 아이콘은 SVG 또는 이모지 사용.
