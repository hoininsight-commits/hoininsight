"""
Evolution Proposal Integrator
Integrates approved proposals into master documentation files.

Updates:
1. DATA_COLLECTION_MASTER.md - Add new data collection definitions
2. ANOMALY_DETECTION_LOGIC.md - Add new logic patterns
3. BASELINE_SIGNALS.md - Add new baseline signals
4. Deep Logic Analysis reports - Include proposal status

This ensures documentation stays in sync with implemented features.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class ProposalIntegrator:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.proposals_dir = base_dir / "data" / "evolution" / "proposals"
        self.docs_dir = base_dir / "docs"
        
        # Master documentation files
        self.data_master = self.docs_dir / "DATA_COLLECTION_MASTER.md"
        self.logic_master = self.docs_dir / "ANOMALY_DETECTION_LOGIC.md"
        self.baseline_master = self.docs_dir / "BASELINE_SIGNALS.md"
        
    def scan_approved_proposals(self) -> Tuple[List[Dict], List[Dict]]:
        """Scan for approved proposals that need integration"""
        data_proposals = []
        logic_proposals = []
        
        if not self.proposals_dir.exists():
            return data_proposals, logic_proposals
        
        for proposal_file in self.proposals_dir.glob("EVO-*.json"):
            try:
                proposal = json.loads(proposal_file.read_text(encoding='utf-8'))
                
                # Only process approved proposals
                if proposal.get('status') == 'APPROVED':
                    if proposal.get('category') == 'DATA_ADD':
                        data_proposals.append(proposal)
                    elif proposal.get('category') == 'LOGIC_UPDATE':
                        logic_proposals.append(proposal)
            except Exception as e:
                print(f"[Integrator] Error reading {proposal_file}: {e}")
        
        return data_proposals, logic_proposals
    
    def update_data_collection_master(self, proposals: List[Dict]) -> bool:
        """Update DATA_COLLECTION_MASTER.md with new data definitions"""
        if not proposals:
            return True
        
        try:
            # Read current content
            current_content = self.data_master.read_text(encoding='utf-8')
            
            # Prepare new entries
            new_entries = []
            for p in proposals:
                condition = p.get('content', {}).get('condition', '')
                meaning = p.get('content', {}).get('meaning', '')
                source = p.get('evidence', {}).get('source', '')
                collector = p.get('collector_script', 'TBD')
                
                # Extract data name from condition
                data_name = self._extract_data_name(condition)
                
                entry = f"""
## 🆕 {data_name} (Evolution Proposal: {p['id']})

| 카테고리 | 수집 데이터 | 수집처 | 방식 | 무료 여부 | 상태 | WHY | 최적 데이터 수집 시간단위 | 파생 여부 |
|---|---|---|---|---|---|---|---|---|
| 시장구조 | {data_name} | KRX/DART | API/CSV | Free | CANDIDATE | {meaning} | 1일 | 수집데이터 |

**출처:** {source}  
**수집 모듈:** `{collector}`  
**승인일:** {datetime.utcnow().strftime('%Y-%m-%d')}
"""
                new_entries.append(entry)
            
            # Append to file
            updated_content = current_content + "\n\n---\n\n# 🆕 Evolution Proposals (Auto-Added)\n\n" + "\n".join(new_entries)
            
            # Backup original
            backup_path = self.data_master.with_suffix('.md.backup')
            backup_path.write_text(current_content, encoding='utf-8')
            
            # Write updated content
            self.data_master.write_text(updated_content, encoding='utf-8')
            
            print(f"[Integrator] Updated DATA_COLLECTION_MASTER with {len(proposals)} proposals")
            return True
            
        except Exception as e:
            print(f"[Integrator] Error updating DATA_COLLECTION_MASTER: {e}")
            return False
    
    def update_anomaly_detection_logic(self, proposals: List[Dict]) -> bool:
        """Update ANOMALY_DETECTION_LOGIC.md with new logic patterns"""
        if not proposals:
            return True
        
        try:
            current_content = self.logic_master.read_text(encoding='utf-8')
            
            new_entries = []
            for p in proposals:
                condition = p.get('content', {}).get('condition', '')
                meaning = p.get('content', {}).get('meaning', '')
                source = p.get('evidence', {}).get('source', '')
                
                entry = f"""
### {p['id']}: {self._extract_logic_name(condition)}

**조건:**  
{condition}

**의미:**  
{meaning}

**출처:** {source}  
**승인일:** {datetime.utcnow().strftime('%Y-%m-%d')}

---
"""
                new_entries.append(entry)
            
            updated_content = current_content + "\n\n## 🆕 Evolution Proposals (Auto-Added Logic)\n\n" + "\n".join(new_entries)
            
            backup_path = self.logic_master.with_suffix('.md.backup')
            backup_path.write_text(current_content, encoding='utf-8')
            
            self.logic_master.write_text(updated_content, encoding='utf-8')
            
            print(f"[Integrator] Updated ANOMALY_DETECTION_LOGIC with {len(proposals)} proposals")
            return True
            
        except Exception as e:
            print(f"[Integrator] Error updating ANOMALY_DETECTION_LOGIC: {e}")
            return False
    
    def mark_as_integrated(self, proposals: List[Dict]):
        """Mark proposals as integrated into master docs"""
        for proposal in proposals:
            proposal_file = self.proposals_dir / f"{proposal['id']}.json"
            if proposal_file.exists():
                proposal['status'] = 'INTEGRATED'
                proposal['integrated_at'] = datetime.utcnow().isoformat()
                proposal_file.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _extract_data_name(self, condition: str) -> str:
        """Extract data name from condition string"""
        # Simple heuristic: look for key terms
        if '외국인' in condition or '수급' in condition:
            return '외국인/기관 투자자 매매동향'
        elif '연기금' in condition:
            return '연기금 매매 동향'
        elif '밸류업' in condition:
            return '밸류업 프로그램 참여 기업'
        elif 'ETF' in condition:
            return 'ETF 거래대금 (섹터별)'
        else:
            return '신규 데이터 항목'
    
    def _extract_logic_name(self, condition: str) -> str:
        """Extract logic name from condition string"""
        if 'MSCI' in condition or '코스피' in condition:
            return 'Passive Index Arbitrage Lock-in'
        elif '정부' in condition:
            return 'Political Capital Route Fixation'
        else:
            return '신규 이상징후 로직'
    
    def generate_comparison_report(self) -> Dict:
        """Generate comparison report between proposals and master docs"""
        data_proposals, logic_proposals = self.scan_approved_proposals()
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "data_proposals": {
                "total": len(data_proposals),
                "approved_not_integrated": [p['id'] for p in data_proposals if p.get('status') == 'APPROVED'],
                "integrated": [p['id'] for p in data_proposals if p.get('status') == 'INTEGRATED']
            },
            "logic_proposals": {
                "total": len(logic_proposals),
                "approved_not_integrated": [p['id'] for p in logic_proposals if p.get('status') == 'APPROVED'],
                "integrated": [p['id'] for p in logic_proposals if p.get('status') == 'INTEGRATED']
            },
            "master_docs_status": {
                "DATA_COLLECTION_MASTER": self.data_master.exists(),
                "ANOMALY_DETECTION_LOGIC": self.logic_master.exists(),
                "BASELINE_SIGNALS": self.baseline_master.exists()
            }
        }
        
        return report
    
    def run(self):
        """Main integration workflow"""
        print("[Integrator] Scanning for approved proposals...")
        
        data_proposals, logic_proposals = self.scan_approved_proposals()
        
        if not data_proposals and not logic_proposals:
            print("[Integrator] No approved proposals to integrate")
            return
        
        print(f"[Integrator] Found {len(data_proposals)} data proposals, {len(logic_proposals)} logic proposals")
        
        # Update master documents
        if data_proposals:
            self.update_data_collection_master(data_proposals)
        
        if logic_proposals:
            self.update_anomaly_detection_logic(logic_proposals)
        
        # Mark as integrated
        self.mark_as_integrated(data_proposals + logic_proposals)
        
        # Generate comparison report
        report = self.generate_comparison_report()
        report_path = self.base_dir / "data" / "evolution" / "integration_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        
        print(f"[Integrator] Integration complete. Report saved to {report_path}")

def main():
    base_dir = Path(__file__).parent.parent.parent
    integrator = ProposalIntegrator(base_dir)
    integrator.run()

if __name__ == "__main__":
    main()
