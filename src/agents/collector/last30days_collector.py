# src/agents/collectors/last30days_collector.py

import json
import subprocess
import sys
import os
from pathlib import Path

class Last30DaysCollector:
    """
    [TASK #104] last30days library wrapper for HOIN Insight.
    Enables deep research across X, Reddit, YouTube, HN, and Polymarket.
    """

    def __init__(self):
        # 프로젝트 루트 기준 상대 경로
        self.script_path = Path("skills/last30days-skill/skills/last30days/scripts/last30days.py").resolve()
        
    def collect(self, topic: str, depth: str = "quick", subreddits: str = None, x_handle: str = None) -> dict:
        """
        주제에 대해 last30days를 실행하고 결과를 JSON으로 반환합니다.
        """
        print(f"  🌊 last30days Deep Research 시작: {topic} (depth: {depth})")
        try:
            # sys.executable을 사용하여 현재 파이썬 환경 유지
            cmd = [
                sys.executable, 
                str(self.script_path), 
                topic, 
                "--emit", "json", 
                "--depth", depth, 
                "--skip-llm",
                "--quiet"
            ]
            
            if subreddits:
                cmd.extend(["--subreddits", subreddits])
            if x_handle:
                cmd.extend(["--x-handle", x_handle])
            
            # PYTHONPATH를 skills/last30days-skill/scripts 로 설정하여 내부 lib 임포트 지원
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.script_path.parent) + os.pathsep + env.get("PYTHONPATH", "")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
            
            if not result.stdout.strip():
                print(f"  ⚠️ last30days 결과 없음 ({topic})")
                return {}
                
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️ last30days 실행 실패 ({topic}): {e}")
            if e.stderr:
                print(f"    Error detail: {e.stderr.splitlines()[-1] if e.stderr.splitlines() else 'unknown'}")
            return {}
        except Exception as e:
            print(f"  ⚠️ last30days 시스템 오류 ({topic}): {e}")
            return {}

    def transform_to_social_format(self, reports: list) -> dict:
        """
        last30days Report 형식들을 기존 social.json 형식으로 변환합니다.
        """
        combined = {
            "reddit": [],
            "x": [],
            "youtube": [],
            "hacker_news": [],
            "polymarket": [],
            "github": []
        }
        
        for report in reports:
            items = report.get("items_by_source", {})
            
            # Reddit mapping
            for item in items.get("reddit", []):
                combined["reddit"].append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "score": item.get("engagement", {}).get("score", 0),
                    "comments": item.get("engagement", {}).get("num_comments", 0),
                    "author": item.get("author"),
                    "snippet": item.get("snippet")
                })
            
            # X mapping
            for item in items.get("x", []):
                combined["x"].append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "engagement": item.get("engagement", {}),
                    "author": item.get("author"),
                    "snippet": item.get("snippet")
                })
                
            # YouTube mapping
            for item in items.get("youtube", []):
                combined["youtube"].append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "views": item.get("engagement", {}).get("views", 0),
                    "channel": item.get("author"),
                    "snippet": item.get("snippet"),
                    "has_transcript": bool(item.get("metadata", {}).get("transcript_snippet"))
                })

            # HN mapping
            for item in items.get("hackernews", []):
                combined["hacker_news"].append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "points": item.get("engagement", {}).get("points", 0),
                    "comments": item.get("engagement", {}).get("num_comments", 0),
                    "author": item.get("author")
                })

            # Polymarket mapping
            for item in items.get("polymarket", []):
                combined["polymarket"].append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "outcomes": item.get("metadata", {}).get("outcome_prices", []),
                    "volume24h": item.get("engagement", {}).get("volume24hr", 0)
                })
                
            # GitHub mapping
            for item in items.get("github", []):
                combined["github"].append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "stars": item.get("engagement", {}).get("stars", 0),
                    "author": item.get("author"),
                    "snippet": item.get("snippet")
                })

        # 중복 제거 (URL 기준)
        for key in combined:
            seen_urls = set()
            unique_items = []
            for item in combined[key]:
                url = item.get("url")
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_items.append(item)
            combined[key] = unique_items
            
        return combined

if __name__ == "__main__":
    collector = Last30DaysCollector()
    res = collector.collect("Nvidia AI", depth="quick")
    print(json.dumps(res, indent=2, ensure_ascii=False))
