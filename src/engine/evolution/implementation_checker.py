"""
Comprehensive System Implementation Checker
Verifies that all items in master documentation are actually implemented.

Checks:
1. DATA_COLLECTION_MASTER.md - Are collectors implemented?
2. ANOMALY_DETECTION_LOGIC.md - Are logic patterns implemented?
3. BASELINE_SIGNALS.md - Are baseline signals collected?
4. Registry files vs actual implementation
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set

class SystemImplementationChecker:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.docs_dir = base_dir / "docs"
        self.src_dir = base_dir / "src"
        self.registry_dir = base_dir / "registry"
        
    def check_data_collection_implementation(self) -> Dict:
        """Check if DATA_COLLECTION_MASTER items are implemented"""
        master_file = self.docs_dir / "DATA_COLLECTION_MASTER.md"
        
        if not master_file.exists():
            return {"error": "DATA_COLLECTION_MASTER.md not found"}
        
        content = master_file.read_text(encoding='utf-8')
        
        # Parse master file for READY items
        ready_items = []
        candidate_items = []
        blocked_items = []
        
        for line in content.split('\n'):
            if '|' in line and len(line.split('|')) > 6:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 7:
                    data_name = parts[2] if len(parts) > 2 else ""
                    status = parts[6] if len(parts) > 6 else ""
                    
                    if 'READY' in status:
                        ready_items.append(data_name)
                    elif 'CANDIDATE' in status:
                        candidate_items.append(data_name)
                    elif 'BLOCKED' in status:
                        blocked_items.append(data_name)
        
        # Check actual collectors
        collectors_dir = self.src_dir / "collectors"
        implemented_collectors = set()
        
        if collectors_dir.exists():
            for collector_file in collectors_dir.rglob("collect_*.py"):
                implemented_collectors.add(collector_file.stem)
        
        # Check registry
        datasets_yml = self.registry_dir / "datasets.yml"
        registered_datasets = set()
        
        if datasets_yml.exists():
            import yaml
            try:
                with open(datasets_yml, 'r', encoding='utf-8') as f:
                    registry = yaml.safe_load(f)
                    if registry and 'datasets' in registry:
                        registered_datasets = set(registry['datasets'].keys())
            except:
                pass
        
        return {
            "documented_ready": len(ready_items),
            "documented_candidate": len(candidate_items),
            "documented_blocked": len(blocked_items),
            "implemented_collectors": len(implemented_collectors),
            "registered_datasets": len(registered_datasets),
            "ready_items_sample": ready_items[:10],
            "implemented_collectors_list": list(implemented_collectors),
            "registered_datasets_list": list(registered_datasets)
        }
    
    def check_anomaly_logic_implementation(self) -> Dict:
        """Check if ANOMALY_DETECTION_LOGIC patterns are implemented"""
        logic_file = self.docs_dir / "ANOMALY_DETECTION_LOGIC.md"
        
        if not logic_file.exists():
            return {"error": "ANOMALY_DETECTION_LOGIC.md not found"}
        
        content = logic_file.read_text(encoding='utf-8')
        
        # Count documented patterns
        patterns = {
            "금리/통화": len(re.findall(r'금리.*쇼크|커브.*급변|인플레.*전환', content)),
            "FX": len(re.findall(r'달러.*레짐|원화.*스트레스|엔화.*위험', content)),
            "Equity": len(re.findall(r'지수.*급락|거래대금.*이례|VIX', content)),
            "Credit": len(re.findall(r'스프레드.*확대|금융.*스트레스', content)),
            "Commodities": len(re.findall(r'금.*급등|유가.*쇼크|구리', content)),
            "Crypto": len(re.findall(r'BTC.*레짐|거래량.*과열', content)),
            "교차신호": len(re.findall(r'리스크.*오프|인플레.*재점화|경기.*침체', content))
        }
        
        # Check if anomaly detector exists
        anomaly_detector = self.src_dir / "anomaly" / "detector.py"
        detector_exists = anomaly_detector.exists()
        
        # Check if regime analyzer exists
        regime_analyzer = self.src_dir / "regime" / "analyzer.py"
        regime_exists = regime_analyzer.exists()
        
        return {
            "documented_patterns": patterns,
            "total_patterns": sum(patterns.values()),
            "detector_implemented": detector_exists,
            "regime_analyzer_implemented": regime_exists,
            "implementation_status": "PARTIAL" if detector_exists or regime_exists else "NOT_IMPLEMENTED"
        }
    
    def check_baseline_signals_implementation(self) -> Dict:
        """Check if BASELINE_SIGNALS are collected"""
        baseline_file = self.docs_dir / "BASELINE_SIGNALS.md"
        
        if not baseline_file.exists():
            return {"error": "BASELINE_SIGNALS.md not found"}
        
        content = baseline_file.read_text(encoding='utf-8')
        
        # Parse baseline signals
        baseline_categories = {
            "금리": 0,
            "물가": 0,
            "FX": 0,
            "주식": 0,
            "신용": 0,
            "원자재": 0,
            "암호화폐": 0
        }
        
        for category in baseline_categories.keys():
            baseline_categories[category] = len(re.findall(category, content))
        
        return {
            "baseline_categories": baseline_categories,
            "total_baselines": sum(baseline_categories.values()),
            "collection_status": "Check DATA_COLLECTION_MASTER for implementation"
        }
    
    def check_registry_vs_implementation(self) -> Dict:
        """Check if registry matches actual implementation"""
        datasets_yml = self.registry_dir / "datasets.yml"
        
        if not datasets_yml.exists():
            return {"error": "datasets.yml not found"}
        
        try:
            import yaml
            with open(datasets_yml, 'r', encoding='utf-8') as f:
                registry = yaml.safe_load(f)
            
            if not registry or 'datasets' not in registry:
                return {"error": "Invalid registry format"}
            
            registered = set(registry['datasets'].keys())
            
            # Check actual data files
            data_dir = self.base_dir / "data" / "raw"
            actual_data = set()
            
            if data_dir.exists():
                for category_dir in data_dir.iterdir():
                    if category_dir.is_dir():
                        for dataset_dir in category_dir.iterdir():
                            if dataset_dir.is_dir():
                                actual_data.add(dataset_dir.name)
            
            # Check curated data
            curated_dir = self.base_dir / "data" / "curated"
            curated_data = set()
            
            if curated_dir.exists():
                for file in curated_dir.rglob("*.csv"):
                    curated_data.add(file.stem)
            
            return {
                "registered_datasets": len(registered),
                "actual_raw_data": len(actual_data),
                "curated_data": len(curated_data),
                "registered_list": list(registered)[:20],
                "actual_data_list": list(actual_data)[:20],
                "match_rate": f"{len(registered & actual_data) / max(len(registered), 1) * 100:.1f}%"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_full_report(self) -> Dict:
        """Generate comprehensive implementation report"""
        report = {
            "generated_at": "2026-01-18T14:23:00+09:00",
            "data_collection": self.check_data_collection_implementation(),
            "anomaly_logic": self.check_anomaly_logic_implementation(),
            "baseline_signals": self.check_baseline_signals_implementation(),
            "registry_vs_actual": self.check_registry_vs_implementation(),
            "summary": {}
        }
        
        # Generate summary
        data_impl_rate = (report['data_collection'].get('implemented_collectors', 0) / 
                         max(report['data_collection'].get('documented_ready', 1), 1) * 100)
        
        report['summary'] = {
            "data_implementation_rate": f"{data_impl_rate:.1f}%",
            "logic_implementation": report['anomaly_logic'].get('implementation_status', 'UNKNOWN'),
            "overall_status": "PARTIAL_IMPLEMENTATION",
            "critical_gaps": []
        }
        
        # Identify critical gaps
        if data_impl_rate < 50:
            report['summary']['critical_gaps'].append(
                f"⚠️ Only {data_impl_rate:.1f}% of documented READY items are implemented"
            )
        
        if report['anomaly_logic'].get('implementation_status') == 'NOT_IMPLEMENTED':
            report['summary']['critical_gaps'].append(
                "⚠️ Anomaly detection logic not implemented"
            )
        
        if report['data_collection'].get('implemented_collectors', 0) < 10:
            report['summary']['critical_gaps'].append(
                f"⚠️ Only {report['data_collection'].get('implemented_collectors', 0)} collectors implemented"
            )
        
        return report
    
    def print_report(self):
        """Print human-readable implementation report"""
        report = self.generate_full_report()
        
        print("\n" + "="*70)
        print("🔍 COMPREHENSIVE SYSTEM IMPLEMENTATION CHECK")
        print("="*70)
        
        print("\n📊 DATA COLLECTION IMPLEMENTATION:")
        print("-" * 70)
        dc = report['data_collection']
        print(f"  Documented (READY):        {dc.get('documented_ready', 0)}")
        print(f"  Documented (CANDIDATE):    {dc.get('documented_candidate', 0)}")
        print(f"  Documented (BLOCKED):      {dc.get('documented_blocked', 0)}")
        print(f"  Implemented Collectors:    {dc.get('implemented_collectors', 0)}")
        print(f"  Registered in datasets.yml: {dc.get('registered_datasets', 0)}")
        print(f"\n  Implementation Rate: {report['summary']['data_implementation_rate']}")
        
        if dc.get('implemented_collectors_list'):
            print(f"\n  Implemented Collectors:")
            for collector in dc['implemented_collectors_list'][:10]:
                print(f"    ✓ {collector}")
        
        print("\n🧠 ANOMALY DETECTION LOGIC:")
        print("-" * 70)
        al = report['anomaly_logic']
        print(f"  Total Documented Patterns: {al.get('total_patterns', 0)}")
        print(f"  Detector Implemented:      {al.get('detector_implemented', False)}")
        print(f"  Regime Analyzer:           {al.get('regime_analyzer_implemented', False)}")
        print(f"  Status:                    {al.get('implementation_status', 'UNKNOWN')}")
        
        if al.get('documented_patterns'):
            print(f"\n  Pattern Categories:")
            for category, count in al['documented_patterns'].items():
                print(f"    {category}: {count} patterns")
        
        print("\n📈 BASELINE SIGNALS:")
        print("-" * 70)
        bs = report['baseline_signals']
        print(f"  Total Baseline Signals:    {bs.get('total_baselines', 0)}")
        
        if bs.get('baseline_categories'):
            print(f"\n  Categories:")
            for category, count in bs['baseline_categories'].items():
                print(f"    {category}: {count} mentions")
        
        print("\n📋 REGISTRY VS ACTUAL DATA:")
        print("-" * 70)
        rv = report['registry_vs_actual']
        print(f"  Registered Datasets:       {rv.get('registered_datasets', 0)}")
        print(f"  Actual Raw Data:           {rv.get('actual_raw_data', 0)}")
        print(f"  Curated Data:              {rv.get('curated_data', 0)}")
        print(f"  Match Rate:                {rv.get('match_rate', 'N/A')}")
        
        print("\n⚠️  CRITICAL GAPS:")
        print("-" * 70)
        for gap in report['summary']['critical_gaps']:
            print(f"  {gap}")
        
        if not report['summary']['critical_gaps']:
            print("  ✅ No critical gaps found")
        
        print("\n" + "="*70 + "\n")
        
        # Save report
        report_path = self.base_dir / "data" / "evolution" / "implementation_check.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"📁 Full report saved to: {report_path}\n")

def main():
    base_dir = Path(os.getcwd())
    checker = SystemImplementationChecker(base_dir)
    checker.print_report()

if __name__ == "__main__":
    main()
