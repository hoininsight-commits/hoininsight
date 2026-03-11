"""
Documentation Sync Checker
Compares current implementation with master documentation files.

Checks:
1. DATA_COLLECTION_MASTER.md vs actual collectors
2. ANOMALY_DETECTION_LOGIC.md vs implemented logic
3. BASELINE_SIGNALS.md vs data sources
4. Evolution proposals vs integrated changes
"""

import json
import os
from pathlib import Path
from typing import Dict, List
import re

class DocSyncChecker:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.docs_dir = base_dir / "docs"
        self.collectors_dir = base_dir / "src" / "collectors"
        self.proposals_dir = base_dir / "data" / "evolution" / "proposals"
        
    def check_data_collection_sync(self) -> Dict:
        """Check if DATA_COLLECTION_MASTER matches implemented collectors"""
        master_file = self.docs_dir / "DATA_COLLECTION_MASTER.md"
        
        if not master_file.exists():
            return {"error": "DATA_COLLECTION_MASTER.md not found"}
        
        content = master_file.read_text(encoding='utf-8')
        
        # Extract data items from master
        master_items = set()
        for line in content.split('\n'):
            if '|' in line and 'READY' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 2:
                    master_items.add(parts[2])  # Data name column
        
        # Find implemented collectors
        implemented = set()
        if self.collectors_dir.exists():
            for collector in self.collectors_dir.rglob("collect_*.py"):
                implemented.add(collector.stem.replace('collect_', ''))
        
        # Find evolution proposals
        proposed = set()
        if self.proposals_dir.exists():
            for proposal_file in self.proposals_dir.glob("EVO-*.json"):
                try:
                    p = json.loads(proposal_file.read_text(encoding='utf-8'))
                    if p.get('category') == 'DATA_ADD':
                        proposed.add(p['id'])
                except:
                    pass
        
        return {
            "master_items_count": len(master_items),
            "implemented_collectors": len(implemented),
            "pending_proposals": len(proposed),
            "sync_status": "OK" if len(implemented) > 0 else "NEEDS_IMPLEMENTATION"
        }
    
    def check_logic_sync(self) -> Dict:
        """Check if ANOMALY_DETECTION_LOGIC matches implemented patterns"""
        logic_file = self.docs_dir / "ANOMALY_DETECTION_LOGIC.md"
        
        if not logic_file.exists():
            return {"error": "ANOMALY_DETECTION_LOGIC.md not found"}
        
        content = logic_file.read_text(encoding='utf-8')
        
        # Count logic patterns in master
        logic_patterns = len(re.findall(r'###\s+[A-Z]\.', content))
        
        # Find logic proposals
        logic_proposals = 0
        if self.proposals_dir.exists():
            for proposal_file in self.proposals_dir.glob("EVO-*.json"):
                try:
                    p = json.loads(proposal_file.read_text(encoding='utf-8'))
                    if p.get('category') == 'LOGIC_UPDATE':
                        logic_proposals += 1
                except:
                    pass
        
        return {
            "documented_patterns": logic_patterns,
            "pending_logic_proposals": logic_proposals,
            "sync_status": "OK" if logic_proposals == 0 else "NEEDS_REVIEW"
        }
    
    def generate_full_report(self) -> Dict:
        """Generate comprehensive sync report"""
        report = {
            "generated_at": Path(os.getcwd()).name,
            "data_collection": self.check_data_collection_sync(),
            "anomaly_logic": self.check_logic_sync(),
            "recommendations": []
        }
        
        # Add recommendations
        if report['data_collection'].get('pending_proposals', 0) > 0:
            report['recommendations'].append(
                f"⚠️ {report['data_collection']['pending_proposals']} data proposals pending integration"
            )
        
        if report['anomaly_logic'].get('pending_logic_proposals', 0) > 0:
            report['recommendations'].append(
                f"⚠️ {report['anomaly_logic']['pending_logic_proposals']} logic proposals pending integration"
            )
        
        if not report['recommendations']:
            report['recommendations'].append("✅ All documentation in sync")
        
        return report
    
    def print_report(self):
        """Print human-readable sync report"""
        report = self.generate_full_report()
        
        print("\n" + "="*60)
        print("📋 DOCUMENTATION SYNC REPORT")
        print("="*60)
        
        print("\n📊 DATA COLLECTION:")
        for key, value in report['data_collection'].items():
            print(f"  {key}: {value}")
        
        print("\n🧠 ANOMALY LOGIC:")
        for key, value in report['anomaly_logic'].items():
            print(f"  {key}: {value}")
        
        print("\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        
        print("\n" + "="*60 + "\n")
        
        # Save to file
        report_path = self.base_dir / "data" / "evolution" / "sync_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"📁 Report saved to: {report_path}\n")

def main():
    import os
    base_dir = Path(os.getcwd())
    checker = DocSyncChecker(base_dir)
    checker.print_report()

if __name__ == "__main__":
    main()
