import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from src.ui.narratives.youtube_watcher import run_watcher
from src.core.gemini_client import GeminiClient

class LearnerAgent:
    """
    [v16.0] Independent Evolution Agent - 'The Mirror of Hunter'
    사냥꾼의 실제 영상과 우리 엔진의 결과물을 비교 분석하여 스스로 엔진을 개선함.
    메인 파이프라인과 독립적으로 구동됨.
    """

    def __init__(self):
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[2]))
        self.transcript_dir = Path("youtube_data/transcripts")
        self.content_log_path = Path("data/history/content_log.json")
        self.evolution_log_path = Path("youtube_data/history/dna_evolution.json")
        self.client = GeminiClient()

    def run_evolution_loop(self, run_round: int = 1):
        """1. 신규 영상 수집 및 대본 확보"""
        print(f"\n🎓 [LEARNER] {run_round}회차: 신규 영상 수집 시작...")
        # YouTubeWatcher 실행 (신규 영상 감지 및 대본 저장)
        os.environ["ENABLE_LEARNING"] = "true"
        os.environ["SKIP_GUARD"] = "true"
        run_watcher(run_round=run_round)

        """2. 분석 단계 (DNA 추출 및 진화) - [PAUSED for Cost Optimization]"""
        print("  [LEARNER] DNA 분석 및 추출 단계가 사용자 요청으로 일시 중단되었습니다. (파일 보관만 진행)")
        # new_transcripts = self._get_recent_transcripts(days=1)
        # if not new_transcripts:
        #     return
        # for transcript_info in new_transcripts:
        #     self._process_single_learning_unit(transcript_info)

    def _get_recent_transcripts(self, days: int) -> list:
        results = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for p in self.transcript_dir.glob("**/*.txt"):
            # 파일 수정 시간이나 경로상 날짜로 필터링
            try:
                # 경로 예시: data/transcripts/youtube/2026/04/24/vid_id.txt
                parts = p.parts
                y, m, d = parts[-4], parts[-3], parts[-2]
                file_date = datetime.strptime(f"{y}{m}{d}", "%Y%m%d")
                
                if file_date >= cutoff:
                    results.append({
                        "path": p,
                        "date": f"{y}-{m}-{d}",
                        "video_id": p.stem,
                        "content": p.read_text(encoding="utf-8")
                    })
            except:
                continue
        return results

    def _process_single_learning_unit(self, hunter_data: dict):
        video_id = hunter_data["video_id"]
        
        # 이미 학습 완료했는지 확인
        if self._is_already_learned(video_id):
            print(f"  [LEARNER] Video {video_id} - 이미 학습 완료됨. 스킵.")
            return

        print(f"  🔍 [LEARNER] {hunter_data['date']} 영상 학습 시작: {video_id}")

        # 1. 우리 엔진의 당시 리포트 찾기
        hoin_report = self._find_matching_hoin_report(hunter_data["date"])
        
        if not hoin_report:
            print(f"  ⚠️ [LEARNER] {hunter_data['date']}에 대응하는 우리 리포트가 없습니다.")
            # 리포트가 없어도 사냥꾼의 단독 분석은 가능하지만, '비교 분석'이 목적이므로 일단 보류하거나 일반 학습 진행
            hoin_report = {"event": "Unknown (No Matching HOIN Report)", "script": "N/A"}

        # 2. Gap Analysis (LLM 호출)
        analysis_result = self._perform_gap_analysis(hunter_data, hoin_report)
        
        if analysis_result:
            self._save_evolution_log(video_id, analysis_result)
            print(f"  ✅ [LEARNER] {video_id} 학습 및 진화 로그 저장 완료.")

    def _find_matching_hoin_report(self, date_str: str) -> dict:
        """
        data/history/content_log.json 에서 해당 날짜와 가장 가까운 리포트 로드
        """
        if not self.content_log_path.exists():
            return None
            
        try:
            logs = json.loads(self.content_log_path.read_text(encoding="utf-8"))
            # 로그는 리스트 형태
            for entry in reversed(logs):
                if entry.get("date") == date_str.replace("-", ""):
                    return entry
        except:
            pass
        return None

    def _perform_gap_analysis(self, hunter_data: dict, hoin_report: dict) -> dict:
        """
        사냥꾼의 대본과 우리의 리포트를 비교하여 '데이터 누락', '논리적 차이', '화법의 차이' 분석
        """
        prompt = f"""
당신은 '경제사냥꾼' AI 엔진의 진화를 담당하는 **'미러 에이전트(Mirror Agent)'**입니다. 
실제 사냥꾼의 영상 대본과 우리 AI 엔진이 작성한 리포트를 비교하여, 우리가 놓치고 있는 '안목'과 '데이터'를 찾아내십시오.

[HUNTER'S ACTUAL SCRIPT - {hunter_data['date']}]
{hunter_data['content'][:5000]} ... (이하 생략)

[HOIN AI'S REPORT - {hoin_report.get('date', 'Unknown')}]
주제: {hoin_report.get('event', 'N/A')}
요약: {hoin_report.get('why_now', 'N/A')}

[ANALYSIS TASK - CRITICAL RULE: DO NOT MENTION SPECIFIC STOCK NAMES IN DNA PATCH]
1. **Data Gap**: 사냥꾼이 사용한 데이터 중 우리가 놓친 핵심 수치나 지표는 무엇인가?
2. **Logic Gap**: 같은 현상을 보고도 사냥꾼은 어떤 '역설'이나 '이면'을 보았는가? 우리 엔진의 평면적인 해석과 어떻게 다른가?
3. **Tone & Hook Gap**: 사냥꾼이 시청자를 사로잡기 위해 사용한 더 강력한 비유나 훅은 무엇인가?
4. **DNA Patch (Structural Evolution)**: 우리 엔진의 프롬프트나 지식 체계에 즉시 반영해야 할 '사고의 구조'나 '분석 방법론'은 무엇인가? 
   - **주의**: "삼성전자", "테슬라" 등 특정 종목명을 절대 명시하지 마십시오. 
   - **대안**: "시장 선도주", "대장주", "특정 섹터의 핵심 기업" 등 추상화된 용어를 사용하십시오. 종목 추천이 아닌 '사냥꾼의 안목(분석 프레임워크)' 자체를 학습하는 것이 목적입니다.

반드시 아래 JSON 형식으로 응답하라:
{{
  "data_gap": ["..."],
  "logic_gap": ["..."],
  "tone_gap": ["..."],
  "dna_patch": "...",
  "priority": (1~5)
}}
"""
        print(f"  [GEMINI] Comparing Hunter vs HOIN for {hunter_data['video_id']}...")
        # 현재 API 한도 문제로 실제 호출 시 에러가 날 수 있으나 구조는 유지
        try:
            # Tier 3 (Flash) 사용 권장
            result = self.client.call_json_controlled(prompt, agent="LEARNER_GAP_ANALYZER", tier=3)
            return result
        except Exception as e:
            print(f"  ❌ [LEARNER] LLM 분석 실패 (API 한도 초과 가능성): {e}")
            return None

    def _is_already_learned(self, video_id: str) -> bool:
        if not self.evolution_log_path.exists():
            return False
        try:
            logs = json.loads(self.evolution_log_path.read_text(encoding="utf-8"))
            return video_id in logs
        except:
            return False

    def _save_evolution_log(self, video_id: str, result: dict):
        logs = {}
        if self.evolution_log_path.exists():
            try:
                logs = json.loads(self.evolution_log_path.read_text(encoding="utf-8"))
            except:
                pass
        
        logs[video_id] = {
            "learned_at": datetime.now().isoformat(),
            "analysis": result
        }
        
        self.evolution_log_path.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    agent = LearnerAgent()
    agent.run_evolution_loop()
