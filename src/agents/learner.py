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
        self.base_scripts_dir = Path("data/learning/scripts")
        self.scripts_dir = self.base_scripts_dir / self.today
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
        """유튜브 자막 추출 (Dual-Engine: API + yt-dlp)"""
        cookies_path = Path("youtube_cookies.txt")
        cookies_arg = str(cookies_path) if cookies_path.exists() else None
        
        # [1순위] youtube-transcript-api 시도
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            api = YouTubeTranscriptApi()
            
            # 쿠키가 있다면 적용 (라이브러리 버전에 따라 다를 수 있어 예외처리)
            try:
                # 최신 버전은 인스턴스 생성 시 또는 list 호출 시 cookies 지원 여부 확인 필요
                # 여기서는 기본 시도 후 실패 시 yt-dlp로 넘김
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
                print(f"  [Engine1] API 실패 또는 차단됨: {e}")
        except ImportError:
            pass

        # [2순위] yt-dlp 시도 (API보다 차단 회피력이 강력함)
        print(f"  [Engine2] yt-dlp로 우회 수집 시도 중...")
        try:
            import yt_dlp
            import tempfile
            import os
            import re
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                ydl_opts = {
                    'skip_download': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['ko', 'en'],
                    'outtmpl': os.path.join(tmp_dir, '%(id)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                
                if cookies_arg:
                    ydl_opts['cookiefile'] = cookies_arg
                    print(f"    (쿠키 인증 사용 중: {cookies_arg})")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
                    
                    # 다운로드된 자막 파일 찾기
                    sub_files = list(Path(tmp_dir).glob(f"{video_id}.*.vtt"))
                    if not sub_files:
                        sub_files = list(Path(tmp_dir).glob(f"{video_id}.*.srt"))
                        
                    if sub_files:
                        with open(sub_files[0], 'r', encoding='utf-8') as f:
                            raw_text = f.read()
                            
                        # VTT/SRT 태그 및 타임스탬프 제거 (간이 파서)
                        clean_text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*\n', '', raw_text)
                        clean_text = re.sub(r'<[^>]*>', '', clean_text)
                        clean_text = re.sub(r'WEBVTT.*\n', '', clean_text)
                        clean_text = re.sub(r'Kind:.*\n', '', clean_text)
                        clean_text = re.sub(r'Language:.*\n', '', clean_text)
                        clean_text = re.sub(r'\n+', ' ', clean_text).strip()
                        
                        return clean_text
            
            return ""
        except Exception as e:
            print(f"  [Engine2] yt-dlp 수집 실패: {e}")
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
