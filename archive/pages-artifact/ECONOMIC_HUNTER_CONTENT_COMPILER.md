# ECONOMIC_HUNTER_CONTENT_COMPILER (IS-9)

## 1. 목적 (Purpose)
IssueSignal의 추론 결과를 "Economic Hunter" 스타일의 완성도 높은 콘텐츠로 변환한다. 이 과정에서 **영상을 참조하지 않으며**, 순수하게 데이터와 로직(IssueSignal Trigger + HoinEngine Evidence)만을 사용하여 콘텐츠를 구성한다.

## 2. 콘텐츠 구조 (Fixed Narrative Structure)
모든 출력물은 다음 7단계 구조를 반드시 준수해야 한다.

1.  **Headline**: 질문형 또는 충격 요법 스타일의 헤드라인.
2.  **Surface-level Interpretation**: 시장이 표면적으로 이해하고 있는 일반적인 관점 기술.
3.  **Incompleteness**: 왜 그 해석이 불완전하거나 틀렸는지 지적.
4.  **True WHY-NOW**: 데이터 기반의 '진짜' 지금 움직여야 하는 이유(Trigger) 공개.
5.  **Forced Capital Flow**: 자본이 어디서 어디로 이동하도록 '강제'되고 있는지 설명.
6.  **Bottleneck → Tickers**: 병목 현상의 해치와 이를 소유한 1~3개의 핵심 Ticker 카드 제시.
7.  **Kill-switch**: 분석이 유효하지 않게 되는 조건(Invalidation Condition) 명시.

## 3. 출력 형식 (Output Formats)
- **Long-form script**: 깊이 있는 분석이 포함된 긴 대본.
- **Shorts script**: 약 30초 내외의 압축된 쇼츠용 스크립트.
- **Locked Ticker Card**: Ticker 정보가 고정된 카드 포맷.

## 4. 구현 원칙 (Implementation Rules)
- **Rule-based Generation**: 템플릿과 필드 맵핑을 통한 규칙 기반 생성을 우선한다.
- **LLM Dependency**: LLM은 문장의 자연스러운 연결과 표현 다듬기에만 최소한으로 사용한다.
- **Content Pack 확장**: 기존 `CONTENT_PACK_SCHEMA`를 확장하여 이 구조를 수용한다.
