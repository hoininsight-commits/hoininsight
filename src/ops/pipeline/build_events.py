from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Adjust paths
import sys
sys.path.append(os.getcwd())

from src.events.gate_event_schema import GateEvent, EventSource, EffectiveWindow, EventEvidence

import urllib.request
import re

class URLExtractor:
    @staticmethod
    def fetch_content(url: str) -> str:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"  [!] Failed to fetch {url}: {e}")
            return ""

    @staticmethod
    def extract_metrics(content: str) -> List[EventEvidence]:
        evidence = []
        # Remove HTML tags for cleaner text processing
        clean_text = re.sub(r'<[^>]+>', ' ', content)
        clean_text = ' '.join(clean_text.split())

        # 1) Percentages with context
        matches = re.finditer(r'([-+]?\d*\.\d+|\d+)%', clean_text)
        for m in matches:
            start, end = m.span()
            context = clean_text[max(0, start-40):min(len(clean_text), end+40)].strip()
            evidence.append(EventEvidence(
                label="Extracted (%)",
                value=float(m.group(1)),
                unit="%",
                context=f"...{context}..."
            ))
            if len(evidence) >= 2: break
        
        # 2) USD values with context
        matches = re.finditer(r'\$([-+]?\d*[\.,]\d+|\d+)', clean_text)
        for m in matches:
            val_str = m.group(1).replace(',', '')
            try:
                val = float(val_str)
                start, end = m.span()
                context = clean_text[max(0, start-40):min(len(clean_text), end+40)].strip()
                evidence.append(EventEvidence(
                    label="Extracted ($)",
                    value=val,
                    unit="USD",
                    context=f"...{context}..."
                ))
            except ValueError:
                continue
        # 3) Duration/Milestone (S4)
        matches = re.finditer(r'(\d+)\s*(months?|years?|days?)', clean_text, re.IGNORECASE)
        for m in matches:
            start, end = m.span()
            context = clean_text[max(0, start-40):min(len(clean_text), end+40)].strip()
            evidence.append(EventEvidence(
                label="Duration",
                value=int(m.group(1)),
                unit=m.group(2).lower(),
                context=f"...{context}..."
            ))
            if len(evidence) >= 4: break

        # 4) Capital/Payment terms (S5)
        keywords = ["cash", "stock", "shares", "buyback", "dilution"]
        for kw in keywords:
            if kw in clean_text.lower():
                matches = re.finditer(re.escape(kw), clean_text, re.IGNORECASE)
                for m in matches:
                    start, end = m.span()
                    context = clean_text[max(0, start-40):min(len(clean_text), end+40)].strip()
                    evidence.append(EventEvidence(
                        label="Capital Detail",
                        value=kw.capitalize(),
                        unit="term",
                        context=f"...{context}..."
                    ))
                    break # Just one per keyword
            if len(evidence) >= 5: break

        if not evidence:
            evidence.append(EventEvidence(label="Relevance Score", value=0.7, unit="score"))
        return evidence[:5]

ENABLED_SOURCES = {"S1", "S2", "S3", "S4", "S5"}

from src.events.source_trust import score_event

class EventBuilder:
    def __init__(self, as_of_date: str):
        self.as_of_date = as_of_date
        self.output_dir = Path("data") / "events" / as_of_date.replace("-", "/")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_from_urls(self, urls: List[str]) -> List[GateEvent]:
        events = []
        extractor = URLExtractor()
        for i, url in enumerate(urls):
            print(f"  [*] Processing: {url}")
            content = extractor.fetch_content(url)
            
            # Reordered priorities: Capital/M&A often mentions "deal", so check it first
            event_type = "other"
            if any(k in url.lower() or k in content.lower() for k in ["acquisition", "merger", "buyback", "offering", "capital"]):
                event_type = "capital" # S5
            elif any(k in url.lower() or k in content.lower() for k in ["earnings", "reporting", "quarter"]):
                event_type = "earnings" # S1
            elif any(k in url.lower() or k in content.lower() for k in ["fed", "policy", "monetary"]):
                event_type = "policy" # S2
            elif any(k in url.lower() or k in content.lower() for k in ["regulation", "sec", "compliance"]):
                event_type = "regulation" # S2
            elif any(k in url.lower() or k in content.lower() for k in ["contract", "order", "deal", "supply"]):
                event_type = "contract" # S4

            title = f"Event from {url.split('/')[2]}"
            match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if match:
                title = match.group(1).strip()

            evidence = extractor.extract_metrics(content)
            
            # STRICT: DROP if no evidence
            if not evidence or (len(evidence) == 1 and evidence[0].label == "Relevance Score" and evidence[0].value < 0.8):
                print(f"  [DROP] Event from {url} dropped due to lack of evidence.")
                continue

            event_obj = GateEvent(
                event_id=f"ev_ext_{datetime.now().strftime('%H%M%S')}_{i}",
                event_type=event_type,
                title=title[:100],
                source=EventSource(publisher=url.split('/')[2], url=url),
                effective_window=EffectiveWindow(
                    start_date=self.as_of_date,
                    end_date=(datetime.strptime(self.as_of_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
                ),
                evidence=evidence
            )
            
            # Integrate Trust Scoring (New)
            score, req_conf, tier = score_event(event_obj, self.as_of_date)
            event_obj.trust_score = score
            event_obj.requires_confirmation = req_conf
            event_obj.trust_tier = tier
            
            events.append(event_obj)
        return events

    def build_from_contracts(self) -> List[GateEvent]:
        """S4: Contract / Strategic Deal official disclosures"""
        # In a real scenario, this would poll KRX/DART/EDGAR APIs.
        # Here we simulate fetching from known official disclosure URLs if provided via CLI as a fallback,
        # or we could have a list of targets. For this demo, let's keep it linked to build_from_urls 
        # but ensure they are tagged as official if the publisher matches TIER_A.
        return []

    def build_from_capital_events(self) -> List[GateEvent]:
        """S5: M&A / Capital market events (M&A, buybacks, offerings, CB/BW)"""
        # Placeholder for automatic capital market disclosure fetching.
        # e.g., scanning DART '주요사항보고서(유상증자/자기주식)'
        return []

    def collect_standard_events(self) -> List[GateEvent]:
        """S1: Earnings/IR + Guidance numbers"""
        events = []
        url = f"https://finance.yahoo.com/calendar/earnings?day={self.as_of_date}"
        print(f"  [*] Checking standard calendar: {url}")
        
        extractor = URLExtractor()
        content = extractor.fetch_content(url)
        
        symbols = re.findall(r'/quote/([A-Z]+)', content)
        unique_symbols = list(dict.fromkeys(symbols))[:5]
        
        for i, sym in enumerate(unique_symbols):
            event_obj = GateEvent(
                event_id=f"ev_cal_{datetime.now().strftime('%Y%m%d')}_{sym}",
                event_type="earnings",
                title=f"{sym} Earnings Report Expected",
                source=EventSource(publisher="Yahoo Finance", url=url),
                effective_window=EffectiveWindow(
                    start_date=self.as_of_date,
                    end_date=self.as_of_date
                ),
                evidence=[EventEvidence(label="Symbol", value=sym, unit="ticker")]
            )
            score, req_conf, tier = score_event(event_obj, self.as_of_date)
            event_obj.trust_score = score
            event_obj.requires_confirmation = req_conf
            event_obj.trust_tier = tier
            events.append(event_obj)
        
        return events

    def save_events(self, events: List[GateEvent]):
        # STEP G: Filter S1-S5 only and ensure evidence exists
        valid_types = {"earnings", "policy", "regulation", "flow", "contract", "capital"}
        filtered = []
        for e in events:
            if e.event_type not in valid_types:
                continue
            # Double check evidence (should be handled in build_* but here as a safety)
            if not e.evidence:
                continue
            filtered.append(e)

        payload = {
            "schema_version": "gate_events_v1",
            "as_of_date": self.as_of_date,
            "events": [self._to_dict(e) for e in filtered]
        }
        
        output_file = self.output_dir / "events.json"
        output_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] Saved {len(filtered)} / {len(events)} events to {output_file}")

    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        if hasattr(obj, "__dict__"):
            return {k: self._to_dict(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, list):
            return [self._to_dict(i) for i in obj]
        return obj

def main():
    parser = argparse.ArgumentParser(description="Build events.json for Content Topic Gate")
    parser.add_argument("--as-of-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--urls", nargs="*", default=[], help="List of URLs to extract events from")
    
    args = parser.parse_args()
    
    builder = EventBuilder(args.as_of_date)
    
    all_events = []
    
    # 1) Build from provided URLs (MVP Semi-auto)
    if args.urls:
        print(f"[*] Extracting events from {len(args.urls)} URLs...")
        all_events.extend(builder.build_from_urls(args.urls))
    
    # 2) Collect from standard sources (Automatic)
    print("[*] Collecting S1: Earnings standard events...")
    all_events.extend(builder.collect_standard_events())

    print("[*] Collecting S4: Contract disclosures...")
    all_events.extend(builder.build_from_contracts())

    print("[*] Collecting S5: Capital market events...")
    all_events.extend(builder.build_from_capital_events())
    
    if not all_events:
        print("[!] No events collected.")
        return

    builder.save_events(all_events)

if __name__ == "__main__":
    main()
