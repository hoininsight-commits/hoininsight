# [{{layer_id}}] 원격 검증 보고서 (Remote Verification Report)

## 1. 작업명 / 목적
- **작업명**: {{task_name}}
- **목적**: {{task_purpose}}

## 2. 변경 사항
### 추가된 파일
{{added_files}}

### 변경된 파일
{{modified_files}}

## 3. 산출물 (Outputs)
{{outputs}}

## 4. 검증 방법 (원격 클린클론 절차)
1. 새로운 디렉토리 생성 및 이동
2. `git clone origin/main`
3. 파이프라인 및 검증 스크립트 실행
   - `{{test_command}}`

## 5. 검증 결과
- **상태**: ✅ PASS

## 6. 커밋 해시
- `{{commit_hash}}`

## 7. 운영자 관점 "무엇이 좋아졌나"
- {{impact_1}}
- {{impact_2}}
- {{impact_3}}
