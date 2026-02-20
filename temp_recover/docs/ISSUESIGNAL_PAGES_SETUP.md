# IssueSignal GitHub Pages Setup Guide (IS-28)

IssueSignal Operator Dashboard를 GitHub Pages를 통해 배포하기 위한 설정 안내서입니다. 이제 `/docs` 폴더 기반 배포에서 **GitHub Actions 기반 배포**로 전환하여 더 빠르고 유연한 배포 환경을 제공합니다.

## 1. GitHub 설정 변경 (필수)
배포를 시작하기 전, 저장소 설정에서 배포 소스를 변경해야 합니다.
1. GitHub 저장소의 **Settings** 탭으로 이동합니다.
2. 왼쪽 메뉴에서 **Pages**를 선택합니다.
3. **Build and deployment** > **Source** 항목에서 `Deploy from a branch`를 **`GitHub Actions`**로 변경합니다.
   - [!] 주의: 이 설정을 바꾸면 이전의 `/docs` 폴더 기반 배포가 중단되고 Actions 워크플로에 의해 사이트가 업데이트됩니다.

## 2. 배포 확인 (Expected URL)
배포가 성공적으로 완료되면 아래 주소에서 대시보드를 확인할 수 있습니다.
- **IssueSignal 대시보드**: `https://hoininsight-commits.github.io/hoininsight/issuesignal/`
- **메인 페이지 (기존)**: `https://hoininsight-commits.github.io/hoininsight/`

| 경로 | 내용 |
| :--- | :--- |
| `/issuesignal/index.html` | IssueSignal 운영 대시보드 UI |
| `/issuesignal/dashboard.json` | 대시보드 데이터 스냅샷 |
| `/index.html` | 기존 HoinInsight 통합 대시보드 |

## 3. 수동 배포 방법 (Force Deploy)
변경사항을 즉시 배포하고 싶을 때 수동으로 워크플로를 실행할 수 있습니다.
1. **Actions** 탭으로 이동합니다.
2. 왼쪽 목록에서 **`Publish IssueSignal Dashboard`** 워크플로를 선택합니다.
3. 오른쪽의 **Run workflow** 버튼을 클릭합니다.

## 4. 문제 해결 (Troubleshooting)
- **404 Not Found**: Settings > Pages에서 Source가 `GitHub Actions`로 되어 있는지 다시 확인하세요. 배포 후 반영까지 1~2분 정도 소요될 수 있습니다.
- **Workflow Failure**: `data/dashboard/issuesignal/` 폴더에 파일이 생성되었는지 확인하세요. `full_pipeline`이 먼저 성공적으로 실행되어야 합니다.
- **Permission Error**: `.github/workflows/publish_issuesignal_dashboard.yml` 파일에 `id-token: write` 권한이 포함되어 있는지 확인하세요. (IS-28에서 자동 설정됨)
