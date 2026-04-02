import json
import os
from datetime import datetime
from pathlib import Path


class LearnerAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.scripts_dir = Path("data/learning/scripts")
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_path = Path("data/learning/topic_patterns.json")
        self.weights_path = Path("data/learning/filter_weights.json")
        self._init_files()

    def _init_files(self):
        """초기 파일 생성 (없을 경우)"""
        if not self.patterns_path.exists():
            self.patterns_path.write_text(json.dumps({
                "total_analyzed": 0,
                "filter_frequency": {
                    "필터1_역사적임계값": 0,
                    "필터2_역설적현상": 0,
                    "필터3_미반영격차": 0,
                    "필터4_시의성": 0,
                    "필터5_연결고리": 0,
                    "필터6_권위자변화": 0,
                    "필터7_공포무관섹터": 0
                },
                "recent_topics": []
            }, ensure_ascii=False, indent=2))

        if not self.weights_path.exists():
            self.weights_path.write_text(json.dumps({
                "필터1_역사적임계값": 1.5,
                "필터2_역설적현상": 1.3,
                "필터3_미반영격차": 1.4,
                "필터4_시의성": 1.6,
                "필터5_연결고리": 1.2,
                "필터6_권위자변화": 1.1,
                "필터7_공포무관섹터": 1.0
            }, ensure_ascii=False, indent=2))

    def fetch_latest_transcripts(self):
        """경사 유튜브 채널 최신 영상 자막 수집"""
        print("🎬 경사 유튜브 채널 크롤링 중...")

        channel_url = "https://www.youtube.com/@경제사냥꾼/videos"
        transcripts = []

        try:
            import yt_dlp
            from youtube_transcript_api import YouTubeTranscriptApi

            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'playlist_items': '1-5',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                videos = info.get('entries', [])[:5]

            for video in videos:
                video_id = video.get('id')
                title = video.get('title', '제목없음')

                # 이미 수집한 영상은 스킵
                script_path = self.scripts_dir / f"{video_id}.txt"
                if script_path.exists():
                    print(f"  이미 수집됨: {title[:30]}")
                    continue

                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(
                        video_id, languages=['ko']
                    )
                    text = ' '.join([t['text'] for t in transcript_list])
                    script_path.write_text(
                        f"제목: {title}\n영상ID: {video_id}\n수집일: {self.today}\n\n{text}",
                        encoding='utf-8'
                    )
                    transcripts.append({
                        'video_id': video_id,
                        'title': title,
                        'text': text
                    })
                    print(f"  수집 완료: {title[:30]}")

                except Exception as e:
                    print(f"  자막 없음: {title[:30]} → {e}")

        except ImportError:
            print("  yt-dlp 또는 youtube-transcript-api 미설치 → pip install yt-dlp youtube-transcript-api")
        except Exception as e:
            print(f"  크롤링 실패: {e}")

        return transcripts

    def analyze_patterns(self, transcripts):
        """수집된 자막에서 토픽 선정 패턴 분석"""
        if not transcripts:
            return

        print(f"  {len(transcripts)}개 영상 패턴 분석 중...")

        patterns = json.loads(self.patterns_path.read_text())

        FILTER_KEYWORDS = {
            "필터1_역사적임계값": ["N년 만", "역대", "처음", "최초", "최고", "최저", "기록"],
            "필터2_역설적현상": ["반대 맞고", "틀린 이야기", "역설", "이상한", "근데 여기서"],
            "필터3_미반영격차": ["아직 안 오른", "저평가", "숨어", "미반영", "담아두고"],
            "필터4_시의성": ["내일부터", "오늘부터", "빨리", "지금 바로", "긴급"],
            "필터5_연결고리": ["때문에", "연결", "파급", "영향", "이어지는"],
            "필터6_권위자변화": ["버핏", "이재용", "머스크", "이재명", "회장", "CEO"],
            "필터7_공포무관섹터": ["시장 무관", "리스크 없", "독립적", "관계없이"]
        }

        for t in transcripts:
            text = t['text']
            for filter_name, keywords in FILTER_KEYWORDS.items():
                if any(kw in text for kw in keywords):
                    patterns["filter_frequency"][filter_name] += 1

            patterns["recent_topics"].append({
                "title": t['title'],
                "video_id": t['video_id'],
                "date": self.today
            })

        patterns["total_analyzed"] += len(transcripts)
        patterns["recent_topics"] = patterns["recent_topics"][-30:]

        self.patterns_path.write_text(
            json.dumps(patterns, ensure_ascii=False, indent=2)
        )
        self._update_weights(patterns)
        print("  패턴 및 가중치 업데이트 완료")

    def _update_weights(self, patterns):
        """필터 빈도 기반 가중치 재계산"""
        freq = patterns["filter_frequency"]
        total = sum(freq.values()) or 1
        weights = json.loads(self.weights_path.read_text())

        for filter_name, count in freq.items():
            base = 1.0
            bonus = (count / total) * 2.0
            weights[filter_name] = round(base + bonus, 2)

        self.weights_path.write_text(
            json.dumps(weights, ensure_ascii=False, indent=2)
        )

    def run(self):
        print(f"\n🎓 AGENT-02 LEARNER 시작 [{self.today}]")
        transcripts = self.fetch_latest_transcripts()
        if transcripts:
            self.analyze_patterns(transcripts)
        else:
            print("  새로 수집된 영상 없음 (기존 파일 유지)")
        print("✅ AGENT-02 완료\n")
        return {"new_transcripts": len(transcripts)}


if __name__ == "__main__":
    agent = LearnerAgent()
    agent.run()
