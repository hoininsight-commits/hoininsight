"""
Human-in-the-Loop Notification System
Sends notifications to user when evolution proposals require approval or implementation.

Notification Channels:
1. Telegram - Immediate alerts for critical proposals
2. GitHub Issue - Detailed task tracking for implementation
3. Dashboard Badge - Visual indicator on dashboard

Workflow:
1. Evolution proposal generated (DATA_ADD or LOGIC_UPDATE)
2. Auto Collector Generator creates template (if DATA_ADD)
3. Notification sent to user via Telegram + GitHub Issue
4. User reviews proposal on dashboard
5. User approves → Notifies Antigravity to implement
6. User rejects → Logs reason and archives
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import os

class HumanLoopNotifier:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.proposals_dir = base_dir / "data" / "evolution" / "proposals"
        self.notifications_dir = base_dir / "data" / "evolution" / "notifications"
        self.notifications_dir.mkdir(parents=True, exist_ok=True)
        
    def scan_pending_proposals(self) -> List[Dict]:
        """Scan for proposals that need human approval"""
        pending = []
        
        if not self.proposals_dir.exists():
            return pending
        
        for proposal_file in self.proposals_dir.glob("EVO-*.json"):
            try:
                proposal = json.loads(proposal_file.read_text(encoding='utf-8'))
                
                # Check if proposal needs approval
                status = proposal.get('status', '')
                if status in ['PROPOSED', 'COLLECTOR_GENERATED']:
                    # Check if already notified
                    notif_file = self.notifications_dir / f"{proposal['id']}_notified.json"
                    if not notif_file.exists():
                        pending.append(proposal)
            except Exception as e:
                print(f"[HumanLoop] Error reading {proposal_file}: {e}")
        
        return pending
    
    def send_telegram_notification(self, proposals: List[Dict]) -> bool:
        """Send Telegram notification for pending proposals"""
        if not proposals:
            return True
        
        try:
            from src.utils.telegram_notifier import TelegramNotifier
            
            notifier = TelegramNotifier()
            
            # Group by category
            data_proposals = [p for p in proposals if p.get('category') == 'DATA_ADD']
            logic_proposals = [p for p in proposals if p.get('category') == 'LOGIC_UPDATE']
            
            message = "🔔 **HOIN ENGINE 진화 제안 알림**\n\n"
            message += f"승인 대기 중인 제안: {len(proposals)}건\n\n"
            
            if data_proposals:
                message += f"📊 **데이터 수집 제안** ({len(data_proposals)}건)\n"
                for p in data_proposals[:3]:  # Show first 3
                    condition = p.get('content', {}).get('condition', '')[:50]
                    collector = p.get('collector_script', 'N/A')
                    message += f"• `{p['id']}`\n"
                    message += f"  조건: {condition}...\n"
                    if collector != 'N/A':
                        message += f"  ✅ 수집 모듈: {collector}\n"
                message += "\n"
            
            if logic_proposals:
                message += f"🧠 **로직 업데이트 제안** ({len(logic_proposals)}건)\n"
                for p in logic_proposals[:3]:
                    condition = p.get('content', {}).get('condition', '')[:50]
                    message += f"• `{p['id']}`\n"
                    message += f"  조건: {condition}...\n"
                message += "\n"
            
            message += "📌 **다음 단계:**\n"
            message += "1. 대시보드에서 제안 검토\n"
            message += "2. 승인 필요 시 → Antigravity에게 구현 요청\n"
            message += "3. 거절 시 → 사유 기록\n\n"
            message += f"🔗 대시보드: https://hoininsight-commits.github.io/hoininsight/\n"
            
            notifier.send_message(message)
            print(f"[HumanLoop] Telegram notification sent for {len(proposals)} proposals")
            return True
            
        except Exception as e:
            print(f"[HumanLoop] Telegram notification failed: {e}")
            return False
    
    def create_github_issue(self, proposals: List[Dict]) -> bool:
        """Create GitHub Issue for implementation tracking"""
        if not proposals:
            return True
        
        try:
            import subprocess
            
            # Group proposals by category
            data_proposals = [p for p in proposals if p.get('category') == 'DATA_ADD']
            logic_proposals = [p for p in proposals if p.get('category') == 'LOGIC_UPDATE']
            
            title = f"[Human Approval] {len(proposals)}개 진화 제안 구현 필요"
            
            body = "## 🤖 HOIN ENGINE 진화 제안\n\n"
            body += f"**생성 시각:** {datetime.utcnow().isoformat()}\n\n"
            body += "---\n\n"
            
            if data_proposals:
                body += f"### 📊 데이터 수집 제안 ({len(data_proposals)}건)\n\n"
                for p in data_proposals:
                    body += f"#### {p['id']}\n"
                    body += f"- **조건:** {p.get('content', {}).get('condition', 'N/A')}\n"
                    body += f"- **의미:** {p.get('content', {}).get('meaning', 'N/A')}\n"
                    body += f"- **출처:** {p.get('evidence', {}).get('source', 'N/A')}\n"
                    
                    if p.get('collector_script'):
                        body += f"- **수집 모듈:** ✅ `{p['collector_script']}`\n"
                        body += f"- **구현 상태:** 템플릿 생성 완료, 실제 API 연동 필요\n"
                    else:
                        body += f"- **구현 상태:** 수집 모듈 생성 필요\n"
                    
                    body += "\n"
            
            if logic_proposals:
                body += f"### 🧠 로직 업데이트 제안 ({len(logic_proposals)}건)\n\n"
                for p in logic_proposals:
                    body += f"#### {p['id']}\n"
                    body += f"- **조건:** {p.get('content', {}).get('condition', 'N/A')}\n"
                    body += f"- **의미:** {p.get('content', {}).get('meaning', 'N/A')}\n"
                    body += f"- **출처:** {p.get('evidence', {}).get('source', 'N/A')}\n"
                    body += f"- **구현 상태:** ANOMALY_DETECTION_LOGIC 업데이트 필요\n"
                    body += "\n"
            
            body += "---\n\n"
            body += "## ✅ 승인 체크리스트\n\n"
            body += "- [ ] 대시보드에서 제안 검토 완료\n"
            body += "- [ ] 데이터 소스 확인 완료\n"
            body += "- [ ] Antigravity에게 구현 요청\n"
            body += "- [ ] 구현 완료 후 테스트\n"
            body += "- [ ] DATA_COLLECTION_MASTER 업데이트\n\n"
            body += f"🔗 [대시보드 바로가기](https://hoininsight-commits.github.io/hoininsight/)\n"
            
            # Create issue using gh CLI
            result = subprocess.run(
                ['gh', 'issue', 'create', '--title', title, '--body', body, '--label', 'evolution,human-approval'],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"[HumanLoop] GitHub Issue created: {result.stdout.strip()}")
                return True
            else:
                print(f"[HumanLoop] GitHub Issue creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[HumanLoop] GitHub Issue creation error: {e}")
            return False
    
    def mark_as_notified(self, proposals: List[Dict]):
        """Mark proposals as notified to avoid duplicate notifications"""
        for proposal in proposals:
            notif_file = self.notifications_dir / f"{proposal['id']}_notified.json"
            notif_data = {
                "proposal_id": proposal['id'],
                "notified_at": datetime.utcnow().isoformat(),
                "category": proposal.get('category'),
                "status": proposal.get('status'),
                "channels": ["telegram", "github_issue"]
            }
            notif_file.write_text(json.dumps(notif_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def run(self):
        """Main notification workflow"""
        print("[HumanLoop] Scanning for pending proposals...")
        
        pending = self.scan_pending_proposals()
        
        if not pending:
            print("[HumanLoop] No pending proposals found")
            return
        
        print(f"[HumanLoop] Found {len(pending)} pending proposals")
        
        # Send notifications
        telegram_ok = self.send_telegram_notification(pending)
        github_ok = self.create_github_issue(pending)
        
        if telegram_ok or github_ok:
            self.mark_as_notified(pending)
            print(f"[HumanLoop] Notifications sent successfully")
        else:
            print(f"[HumanLoop] All notification channels failed")

def main():
    base_dir = Path(__file__).parent.parent.parent
    notifier = HumanLoopNotifier(base_dir)
    notifier.run()

if __name__ == "__main__":
    main()
