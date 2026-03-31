"""
Auto Collector Generator
Automatically generates data collection modules based on evolution proposals.

Process:
1. Read evolution proposals (DATA_ADD category)
2. Match with DATA_SOURCE_REGISTRY
3. Generate collector script from template
4. Save to src/collectors/auto_generated/
5. Update proposal status to READY_FOR_APPROVAL
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class AutoCollectorGenerator:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.registry_path = base_dir / "docs" / "DATA_SOURCE_REGISTRY.md"
        self.proposals_dir = base_dir / "data" / "evolution" / "proposals"
        self.output_dir = base_dir / "src" / "collectors" / "auto_generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load registry (simple keyword matching for now)
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Dict]:
        """Parse DATA_SOURCE_REGISTRY.md for source mappings"""
        if not self.registry_path.exists():
            return {}
        
        content = self.registry_path.read_text(encoding='utf-8')
        
        # Simple keyword-based registry
        registry = {
            "외국인": {
                "name": "foreign_investor_flow",
                "source": "KRX 정보데이터시스템",
                "method": "CSV",
                "free": True,
                "interval": "1일",
                "category": "market_flow"
            },
            "수급": {
                "name": "investor_flow",
                "source": "KRX 정보데이터시스템",
                "method": "CSV",
                "free": True,
                "interval": "1일",
                "category": "market_flow"
            },
            "연기금": {
                "name": "pension_fund_flow",
                "source": "금융감독원 전자공시",
                "method": "DART API",
                "free": True,
                "interval": "1주",
                "category": "institutional_flow"
            },
            "밸류업": {
                "name": "value_up_participants",
                "source": "금융위원회 공시",
                "method": "공개자료",
                "free": True,
                "interval": "이벤트",
                "category": "policy"
            },
            "테슬라": {
                "name": "tesla_fsd_data",
                "source": "Tesla Investor Relations",
                "method": "웹스크래핑",
                "free": True,
                "interval": "분기",
                "category": "corporate"
            },
            "FSD": {
                "name": "tesla_fsd_miles",
                "source": "Tesla Investor Relations",
                "method": "웹스크래핑",
                "free": True,
                "interval": "분기",
                "category": "corporate"
            }
        }
        return registry
    
    def match_source(self, condition: str) -> Optional[Dict]:
        """Match proposal condition to data source"""
        condition_lower = condition.lower()
        
        for keyword, source_info in self.registry.items():
            if keyword in condition:
                return source_info
        
        return None
    
    def generate_collector_script(self, proposal: Dict, source_info: Dict) -> str:
        """Generate Python collector script from template"""
        data_name = source_info['name']
        source_name = source_info['source']
        method = source_info['method']
        category = source_info['category']
        
        script = f'''"""
Auto-generated collector for: {data_name}
Source: {source_name}
Method: {method}
Generated: {datetime.now().isoformat()}
Status: CANDIDATE
Proposal ID: {proposal['id']}
"""

from pathlib import Path
import json
from datetime import datetime

def collect():
    """
    Collect {data_name} from {source_name}
    
    TODO: Implement collection logic
    1. Fetch data from {source_name} using {method}
    2. Parse and validate data
    3. Save to data/raw/{category}/{data_name}/YYYY/MM/DD/
    
    Reference:
    - Proposal: {proposal['id']}
    - Evidence: {proposal.get('evidence', {}).get('quote', 'N/A')}
    """
    
    base_dir = Path(__file__).parent.parent.parent.parent
    output_dir = base_dir / "data" / "raw" / "{category}" / "{data_name}"
    
    # Get current date
    now = datetime.now()
    date_path = output_dir / now.strftime("%Y/%m/%d")
    date_path.mkdir(parents=True, exist_ok=True)
    
    # TODO: Implement actual collection
    print(f"[{data_name}] Collection not yet implemented")
    print(f"[{data_name}] Target source: {source_name}")
    print(f"[{data_name}] Output: {{date_path}}")
    
    # Placeholder: Save metadata
    metadata = {{
        "collected_at": now.isoformat(),
        "source": "{source_name}",
        "status": "NOT_IMPLEMENTED",
        "proposal_id": "{proposal['id']}"
    }}
    
    metadata_path = date_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    
    return metadata

if __name__ == "__main__":
    result = collect()
    print(f"Collection result: {{result}}")
'''
        return script
    
    def process_proposals(self):
        """Process all DATA_ADD proposals and generate collectors"""
        if not self.proposals_dir.exists():
            print("[AutoCollector] No proposals directory found")
            return
        
        generated_count = 0
        
        for proposal_file in self.proposals_dir.glob("EVO-*.json"):
            try:
                proposal = json.loads(proposal_file.read_text(encoding='utf-8'))
                
                # Only process DATA_ADD proposals
                if proposal.get('category') != 'DATA_ADD':
                    continue
                
                # Skip if already processed
                if proposal.get('status') == 'COLLECTOR_GENERATED':
                    continue
                
                condition = proposal.get('content', {}).get('condition', '')
                if not condition:
                    continue
                
                # Match to source
                source_info = self.match_source(condition)
                if not source_info:
                    print(f"[AutoCollector] No source match for: {condition[:50]}...")
                    continue
                
                # Generate collector script
                script_content = self.generate_collector_script(proposal, source_info)
                script_name = f"collect_{source_info['name']}.py"
                script_path = self.output_dir / script_name
                
                # Save script
                script_path.write_text(script_content, encoding='utf-8')
                print(f"[AutoCollector] Generated: {script_path}")
                
                # Update proposal status
                proposal['status'] = 'COLLECTOR_GENERATED'
                proposal['collector_script'] = str(script_path.relative_to(self.base_dir))
                proposal_file.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding='utf-8')
                
                generated_count += 1
                
            except Exception as e:
                print(f"[AutoCollector] Error processing {proposal_file.name}: {e}")
        
        print(f"[AutoCollector] Generated {generated_count} collector scripts")
        return generated_count

def main():
    base_dir = Path(__file__).parent.parent.parent
    generator = AutoCollectorGenerator(base_dir)
    generator.process_proposals()

if __name__ == "__main__":
    main()
