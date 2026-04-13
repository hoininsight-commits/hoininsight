# src/agents/learner.py
# AGENT-02 LEARNER
# 역할: 경사 유튜브 새 영상 감지 + 자막 추출 + 파일 저장
# 분석/학습은 하지 않는다 — 선장이 직접 판단

import json
from datetime import datetime
from pathlib import Path


class LearnerAgent:

    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
        self.scripts_dir = Path("data/learning/scripts")
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = Path("data/learning/collected_index.json")
        self._init_index()

    def _init_index(self):
        """수집 이력 파일 초기화"""
        if not self.index_path.exists():
            self.index_path.write_text(json.dumps({
                "total_collected": 0,
                "videos": []
            }, ensure_ascii=False, indent=2))

    def _load_index(self) -> dict:
        return json.loads(self.index_path.read_text())

    def _save_index(self, index: dict):
        self.index_path.write_text(
            json.dumps(index, ensure_ascii=False, indent=2)
        )

    def _already_collected(self, video_id: str) -> bool:
        index = self._load_index()
        return video_id in [v["video_id"] for v in index["videos"]]

    def fetch_video_list(self, max_videos: int = 10) -> list:
        """채널 최신 영상 목록 가져오기"""
        print(f"  채널 영상 목록 조회 중 (최근 {max_videos}개)...")

        channel_url = "https://www.youtube.com/@경제사냥꾼/videos"

        try:
            import yt_dlp

            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'playlist_items': f'1-{max_videos}',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                videos = info.get('entries', [])

            result = [{
                "video_id": v.get("id"),
                "title": v.get("title", "제목없음"),
                "url": f"https://www.youtube.com/watch?v={v.get('id')}",
                "duration": v.get("duration"),
                "view_count": v.get("view_count"),
            } for v in videos]

            print(f"  영상 목록 조회 완료: {len(result)}개")
            return result

        except ImportError:
            print("  yt-dlp 미설치 — pip install yt-dlp")
            return []
        except Exception as e:
            print(f"  영상 목록 조회 실패: {e}")
            return []

    def extract_transcript(self, video_id: str, title: str) -> str:
        """유튜브 자막 추출"""
        try:
            try:
                # 현재 라이브러리 버전에 맞는 인스턴스 생성 후 list 호출 방식 사용
                api = YouTubeTranscriptApi()
                transcript_list = api.list(video_id)
                
                try:
                    transcript = transcript_list.find_manually_created_transcript(['ko'])
                except:
                    try:
                        transcript = transcript_list.find_generated_transcript(['ko'])
                    except:
                        transcript = transcript_list.find_transcript(['en', 'en-US'])
                
                data = transcript.fetch()
                return ' '.join([t.text for t in data])
            except Exception as e:
                print(f"  자막 추출 API 오류: {title[:30]} — {e}")
                return ""

        except ImportError:
            print("  youtube-transcript-api 미설치")
            return ""
        except Exception as e:
            print(f"  자막 없음: {title[:30]} — {e}")
            return ""

    def save_script(self, video_id: str, title: str, transcript: str) -> Path:
        """자막 파일 저장"""
        filename = f"{self.today}_{video_id}.txt"
        script_path = self.scripts_dir / filename

        content = f"""제목: {title}
영상ID: {video_id}
URL: https://www.youtube.com/watch?v={video_id}
수집일: {self.today}
수집시각: {datetime.now().strftime('%H:%M:%S')}

---

{transcript}
"""
        script_path.write_text(content, encoding='utf-8')
        return script_path

    def update_index(self, video: dict, script_path: Path):
        """수집 이력 업데이트"""
        index = self._load_index()
        index["videos"].append({
            "video_id": video["video_id"],
            "title": video["title"],
            "url": video["url"],
            "collected_date": self.today,
            "script_file": str(script_path),
            "analyzed": False
        })
        index["total_collected"] = len(index["videos"])
        self._save_index(index)

    def run(self, max_videos: int = 10):
        print(f"\n🎓 AGENT-02 LEARNER 시작 [{self.today}]")
        print(f"  역할: 경사 유튜브 자막 수집 (분석 없음)")

        videos = self.fetch_video_list(max_videos)

        if not videos:
            print("  영상 목록 조회 실패")
            print("✅ AGENT-02 완료 (수집 없음)\n")
            return {"new_collected": 0, "skipped": 0}

        new_count = 0
        skip_count = 0

        for video in videos:
            video_id = video["video_id"]
            title = video["title"]

            if self._already_collected(video_id):
                print(f"  스킵 (기수집): {title[:40]}")
                skip_count += 1
                continue

            transcript = self.extract_transcript(video_id, title)

            if not transcript:
                skip_count += 1
                continue

            script_path = self.save_script(video_id, title, transcript)
            self.update_index(video, script_path)
            print(f"  저장 완료: {title[:40]}")
            new_count += 1

        index = self._load_index()
        print(f"\n  신규 수집: {new_count}개")
        print(f"  스킵: {skip_count}개")
        print(f"  누적 수집: {index['total_collected']}개")
        print("✅ AGENT-02 완료\n")

        return {
            "new_collected": new_count,
            "skipped": skip_count,
            "total": index["total_collected"]
        }


if __name__ == "__main__":
    agent = LearnerAgent()
    agent.run()
