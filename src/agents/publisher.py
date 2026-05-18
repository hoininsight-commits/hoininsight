# src/agents/publisher.py
# AGENT-06 PUBLISHER
# 역할: 이력 저장 + 대시보드 업데이트 + 선장 브리핑

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from src.utils.telegram_notifier import TelegramNotifier
from src.utils.target_date import get_target_ymd, get_current_round, get_standard_path_prefix


class PublisherAgent:

    def __init__(self):
        # [v24.2] 3단계 지능형 환경 인지: 서버 / 집 / 회사 자동 판별
        import socket
        hostname = socket.gethostname()
        self.is_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
        
        if self.is_github_actions:
            self.env_type = "SERVER"
            self.base_dir = Path(os.environ.get("GITHUB_WORKSPACE", "."))
            print("  🌐 [ENV] GitHub Actions 서버 환경 감지")
        elif "TaeHunui-MacBookPro" in hostname:
            self.env_type = "HOME"
            self.base_dir = Path(__file__).resolve().parent.parent.parent
            print(f"  🏠 [ENV] 집 맥북 환경 감지 - 경로: {self.base_dir}")
        else:
            self.env_type = "OFFICE"
            self.base_dir = Path(__file__).resolve().parent.parent.parent
            print(f"  🏢 [ENV] 회사/기타 환경 감지 - 경로: {self.base_dir}")

        self.today = get_target_ymd().replace("-", "")
        self.path_prefix = get_standard_path_prefix()
        self.round = os.environ.get("HOIN_TARGET_ROUND", str(get_current_round()))
        
        self.content_log_path = self.base_dir / "data/history/content_log.json"
        self.signal_log_path = self.base_dir / "data/history/signal_log.json"
        self.dashboard_dir = self.base_dir / "dashboard"
        self.dashboard_dir.mkdir(exist_ok=True)
        self.notifier = TelegramNotifier()

    def load_today_data(self) -> dict:
        """[v24.5] 통합 경로 로직: 가장 최근의 Topic_N 폴더를 찾아 그 안의 파일들을 세트로 로드"""
        data = {"date": f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:]}"}
        
        def safe_load_json(path: Path):
            try:
                return json.loads(path.read_text(encoding='utf-8'))
            except:
                return None

        # 1. 대상 폴더 찾기 (가장 최근에 수정된 Topic_N)
        daily_base = self.base_dir / "data" / "scripts" / self.path_prefix
        target_dir = None
        
        if daily_base.exists():
            topic_dirs = sorted(list(daily_base.glob("Topic_*")), key=lambda x: x.stat().st_mtime, reverse=True)
            if topic_dirs:
                target_dir = topic_dirs[0]
                print(f"  📂 [Publisher] Latest Topic Directory Detected: {target_dir.name}")
        
        # 2. 파일 로드 헬퍼 (타겟 폴더 우선, 없으면 표준 경로Fallback)
        def get_file_content(filename: str, use_json=True):
            # A. 타겟 폴더 내부 확인 (최우선)
            if target_dir:
                p = target_dir / filename
                if p.exists():
                    try:
                        return json.loads(p.read_text(encoding="utf-8")) if use_json else p.read_text(encoding="utf-8")
                    except: pass
            
            # B. 표준 경로 확인
            category_raw = filename.split("_")[1].split(".")[0] if "_" in filename else filename.split(".")[0]
            category = category_raw if category_raw.endswith("s") else category_raw + "s"
            std_p = self.base_dir / "data" / category / self.path_prefix / filename
            if std_p.exists():
                try:
                    return json.loads(std_p.read_text(encoding="utf-8")) if use_json else std_p.read_text(encoding="utf-8")
                except: pass
            
            # C. rglob Fallback
            for d in sorted(self.base_dir.rglob(filename), key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    return json.loads(d.read_text(encoding="utf-8")) if use_json else d.read_text(encoding="utf-8")
                except: continue
            
            return None

        # 3. 데이터 세트 조립
        script_content = get_file_content("today_script_long.md", use_json=False)
        signal_data = get_file_content("signal.json") or get_file_content("today_signal.json")
        analysis_data = get_file_content("analysis.json") or get_file_content("today_analysis.json")
        stocks_data = get_file_content("today_stocks.json")
        
        # 로우 데이터 수집 결과 (collection_status)
        data["collection_status"] = get_file_content("collection_status.json") or {}

        if not script_content or not signal_data:
            print(f"  ⚠️ [Publisher] Failed to load consistent data set (Script: {'OK' if script_content else 'NO'}, Signal: {'OK' if signal_data else 'NO'})")
            return {}

        # Arbiter 통합 구조 대응 (MAIN 키 처리)
        main_signal = signal_data.get("MAIN", signal_data)
        
        data.update({
            "script": script_content,
            "script_long_path": str(target_dir / "today_script_long.md") if target_dir else "",
            "signal": {
                "topic": main_signal.get("topic", main_signal.get("event", "N/A")),
                "event": main_signal.get("event", main_signal.get("topic", "N/A")),
                "strength": main_signal.get("final_score", main_signal.get("strength", main_signal.get("confidence", 0))) * 100,
                "content_type": "롱폼" if main_signal.get("tier") == "MAIN/TIER_1" or main_signal.get("content_type") == "NORMAL" else "쇼츠",
                "filters_hit": [main_signal.get("structure_axis", "S")],
                "why_now": main_signal.get("why_now", main_signal.get("selection_reason", "")),
                "arbiter_rationale": main_signal.get("arbiter_rationale", "N/A"),
                "hunter_insight": main_signal.get("hunter_insight", "N/A"),
                "why_hypothesis": main_signal.get("why_hypothesis", ""),
                "hypothesis_confidence": main_signal.get("hypothesis_confidence", "MEDIUM"),
                "stocks_analysis": main_signal.get("stocks_analysis", {}),
                "stocks": main_signal.get("stocks", [])
            },
            "analysis": analysis_data or {},
            "stocks": stocks_data or {},
            "path": str(target_dir.relative_to(self.base_dir)).replace("\\", "/") if target_dir else f"data/scripts/{self.path_prefix}"
        })
        
        print(f"  ✅ [PUBLISHER] Consistent data set loaded from {data['path']}")
        return data


    def update_content_log(self, data: dict) -> dict:
        """content_log.json에 오늘 콘텐츠 추가"""
        signal = data.get("signal", {})
        if not signal:
            print("  신호 없음 — 이력 업데이트 건너뜀")
            return {}

        stocks = data.get("stocks") or {}
        stock_names = [
            s["name"] for s in stocks.get("stocks", [])[:3]
        ]

        # [v24.2] 주제별 경로 반영 (데이터 로딩 시 확정된 path 우선 사용)
        rel_path = data.get("path")
        if not rel_path:
            topic_path = signal.get("paths", {}).get("topic_dir", "")
            if topic_path:
                rel_path = topic_path.split("HoinInsight/")[-1] if "HoinInsight/" in topic_path else topic_path
            else:
                rel_path = f"data/scripts/{self.path_prefix}"

        # [v24.2] 실제 파일에서 진짜 제목 추출 (Gemini가 수정한 화려한 제목 반영)
        actual_title = signal.get("topic", "")
        script_path = self.base_dir / rel_path / "today_script_long.md" if rel_path else None
        if script_path and script_path.exists():
            try:
                content = script_path.read_text(encoding="utf-8")
                # 첫 번째 줄에서 # [ECONOMIC HUNTER] 제거하고 제목만 추출
                first_line = content.split('\n')[0]
                actual_title = first_line.replace("# [ECONOMIC HUNTER]", "").replace("#", "").strip()
                if not actual_title: actual_title = signal.get("topic", "")
                print(f"  ✅ [PUBLISHER] 실제 파일 제목 추출 성공: {actual_title}")
            except: pass

        # 새 콘텐츠 항목
        new_content = {
            "id": f"{self.today}_{datetime.now().strftime('%H%M%S')}",
            "date": f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:]}",
            "type": signal.get("content_type", "롱폼"),
            "title": actual_title,
            "thumbnail_text": "",
            "custom_img": signal.get("custom_img", "cover.png"),
            "path": rel_path,
            "duration_min": 15 if signal.get("content_type") == "롱폼" else 2,
            "signal_strength": signal.get("strength", 0),
            "filters_used": signal.get("filters_hit", []),
            "stocks": stock_names,
            "status": "승인대기",
            "publish_status": "SUCCESS"
        }

        # 기존 이력 로드
        log = {"contents": []}
        if self.content_log_path.exists():
            try:
                log = json.loads(self.content_log_path.read_text())
            except Exception:
                pass

        # [v24.0] 중복 체크 강화: 날짜와 제목이 같으면 동일 리포트로 간주
        is_duplicate = False
        for i, c in enumerate(log["contents"]):
            if c.get("date") == new_content["date"] and c.get("title") == new_content["title"]:
                # 이미 존재하면 업데이트 (ID 유지 혹은 교체 가능하나 여기서는 덮어쓰기)
                log["contents"][i] = new_content
                is_duplicate = True
                break
        
        if not is_duplicate:
            log["contents"].append(new_content)

        self.content_log_path.write_text(
            json.dumps(log, ensure_ascii=False, indent=2)
        )
        print(f"  content_log.json 업데이트 (누적: {len(log['contents'])}개)")
        return new_content

    def update_signal_log(self, data: dict):
        """signal_log.json 업데이트 (탈락 후보 포함)"""
        candidates = data.get("candidates", {})
        signal = data.get("signal", {})

        log = {"signals": []}
        if self.signal_log_path.exists():
            try:
                log = json.loads(self.signal_log_path.read_text())
            except Exception:
                pass

        # 오늘 날짜 이미 있으면 스킵
        today_str = f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:]}"
        existing_dates = [s.get("date") for s in log["signals"]]
        if today_str in existing_dates:
            print("  signal_log.json 이미 오늘 날짜 존재 — 스킵")
            return

        log["signals"].append({
            "date": today_str,
            "topic": signal.get("topic", "없음"),
            "strength": signal.get("strength", 0),
            "selected": True if signal else False,
            "content_type": signal.get("content_type", ""),
            "total_candidates": candidates.get("total_candidates", 0),
        })

        self.signal_log_path.write_text(
            json.dumps(log, ensure_ascii=False, indent=2)
        )
        print(f"  signal_log.json 업데이트 (누적: {len(log['signals'])}개)")

    def generate_dashboard_data(self, data: dict, content: dict, pipeline_results: dict = None):
        """대시보드용 JSON 생성 (UI Contract v2.1 규격 통일)"""
        signal = data.get("signal") or {}
        analysis = data.get("analysis") or {}
        candidates = data.get("candidates", {}).get("candidates", [])
        
        # 1. Content Pack 구성 (Tier별 분류)
        # pipeline_results가 있으면 그곳의 content_pack을 우선 사용
        content_pack = {
            "TIER_1": [], "TIER_2": [], "TIER_3": []
        }
        
        if pipeline_results and "content_pack" in pipeline_results:
            content_pack = pipeline_results["content_pack"]
        else:
            # 백업: 모든 후보 데이터(candidates.json)를 기반으로 Content Pack 복구
            all_candidates = data.get("candidates", {}).get("candidates", [])
            if all_candidates:
                # [DEPRECATED] from src.content.content_tier import map_action_to_tier
                
                # 메인 신호 토픽 확인 (v2.0 대응: event와 topic 모두 체크)
                selected_title = ""
                selected_id = ""
                if signal:
                    selected_title = signal.get("event", signal.get("topic", ""))
                    selected_id = signal.get("candidate_id", "")
                else:
                    print("  ⚠️ [PUBLISHER] No MAIN signal found. Dashboard will show empty state.")
                
                for i, cand in enumerate(all_candidates):
                    cand_title = cand.get("event", cand.get("topic", ""))
                    cand_id = cand.get("candidate_id", "")
                    
                    # [FIX] ID가 있으면 ID로 매칭, 없으면 제목으로 매칭
                    if selected_id and cand_id:
                        is_winner = cand_id == selected_id
                        if is_winner:
                            print(f"  [DEBUG] Winner Found by ID: {cand_id}")
                    else:
                        is_winner = cand_title == selected_title and selected_title != ""
                        if is_winner:
                            print(f"  [DEBUG] Winner Found by Title: {cand_title}")
                    
                    if i < 3: # 첫 3개만 로깅
                        print(f"  [DEBUG] Processing cand {i}: title='{cand_title}', id='{cand_id}', selected_id='{selected_id}', winner={is_winner}")
                    
                    # 스크립트 본문 로드 (메인 토픽일 경우에만 전문 로드)
                    script_body = f"[{cand.get('anomaly_type', '탐지')}] {cand.get('why_anomalous')}"
                    
                    if is_winner:
                        script_path = data.get("script_long_path")
                        if script_path and Path(script_path).exists():
                            script_body = Path(script_path).read_text(encoding="utf-8")
                    
                    # 계층 할당: 오직 승자만 TIER_1, 나머지는 TIER_3(인사이트)
                    tier = "TIER_1" if is_winner else "TIER_3"
                    action = "USE" if is_winner else "DROP"
                    
                    # [V2.0 MAPPING]
                    cand_topic = cand.get("event", cand.get("topic", ""))
                    cand_why_now = cand.get("evaluation", {}).get("why_now_summary", cand.get("why_now", ""))
                    if not cand_why_now:
                        cand_why_now = cand.get("selection_reason", "")

                    processed = {
                        "topic": cand_topic,
                        "core_claim": cand_topic,
                        "why_now": cand_why_now,
                        "structural_truth": cand.get("selection_reason", ""),
                        "level2_chain": cand.get("key_indicators", []),
                        "quality_score": int(cand.get("final_score", 0) * 10) if cand.get("final_score") else int(cand.get("strength", 0) * 10),
                        "reality_score": 1 if cand.get("final_score", 0) >= 0.9 or cand.get("strength", 0) >= 9.5 else 0,
                        "score_trust": "HIGH_TRUST" if is_winner else "MEDIUM_TRUST",
                        "final_action": action,
                        "content_tier": tier,
                        "script": script_body,
                        # Why Hypothesis Layer (v2.0)
                        "why_hypothesis": cand.get("why_hypothesis", ""),
                        "mechanism": cand.get("mechanism", ""),
                        "confidence": cand.get("hypothesis_confidence", cand.get("confidence", "")),
                        # [v15.1] Stock Analysis Layer
                        "stocks": cand.get("stocks", signal.get("stocks", []) if is_winner else [])
                    }
                    content_pack[tier].append(processed)
            elif signal:
                # 최후의 백업: 단일 신호 표기
                # [LOCAL MAPPING] Replacement for missing src.content.content_tier
                action = signal.get("decision_meta", {}).get("action", "WATCH")
                tier_map = {"PROMOTE": "TIER_1", "WATCH": "TIER_2", "DROP": "TIER_3"}
                tier = tier_map.get(action, "TIER_3")
                # ... (기존 단일 처리 로직 유지 또는 통합)

        # 2. 메인 컨텐츠 추출 (TIER_1 우선)
        all_contents = []
        for t in ["TIER_1", "TIER_2", "TIER_3"]:
            all_contents.extend(content_pack.get(t, []))
            
        main_content = {}
        if all_contents:
            main_content = all_contents[0]

        # 3. 시장 지표 (Market Snapshot)
        market = data.get("market", {})
        market_data_outer = market.get("data", {})
        
        # [FIX] 중첩 구조 대응 (data -> data)
        if isinstance(market_data_outer, dict) and "data" in market_data_outer:
            market_data = market_data_outer.get("data", {})
        else:
            market_data = market_data_outer
            
        market_stats = market_data.get("multi_period_stats", {}) if isinstance(market_data, dict) else {}
        
        rates_val = market_data.get("us10y", "N/A")
        spx_val = market_data.get("sp500", "N/A")
        btc_val = market_data.get("btc_price") or market_data.get("bitcoin") or "N/A"
        
        spx_chg = market_data.get("sp500_1d_change", 0)
        trend = "BULLISH" if spx_chg > 0 else "BEARISH" if spx_chg < 0 else "NEUTRAL"

        # 4. 과거 이력 (History Layer)
        history = []
        try:
            index_path = self.base_dir / "docs/topics/index.json"
            if index_path.exists():
                history = json.loads(index_path.read_text())[:5]
        except: pass

        # 5. 최종 데이터 계약 (UI/docs 전용)
        ui_contract = {
            "top_decision": {
                "topic": main_content.get("topic", main_content.get("event", "N/A")),
                "final_action": main_content.get("final_action", "N/A"),
                "content_tier": main_content.get("content_tier", "TIER_3"),
                "summary": main_content.get("core_claim", "데이터 분석 중"),
                "why_now": main_content.get("why_now", "분석 중"),
                "why_hypothesis": main_content.get("why_hypothesis", ""),
                "mechanism": main_content.get("mechanism", ""),
                "confidence": main_content.get("confidence", main_content.get("hypothesis_confidence", ""))
            },
            "market_axis": main_content.get("market_axis", {}),
            "content_pack": content_pack,
            "reason_layer": {
                "quality_score": main_content.get("quality_score", 0),
                "reality_score": main_content.get("reality_score", 0),
                "score_trust": main_content.get("score_trust", "COLD")
            },
            "market_snapshot": {
                "rates": f"{rates_val}%" if rates_val != "N/A" else "N/A",
                "spx": f"{spx_val}",
                "btc": f"{btc_val}",
                "trend_short": trend,
                "trend_mid": "UP"
            },
            "risk_layer": {
                "kill_switch": analysis.get("risk_kill_switch", "조건 미정"),
                "opposite_scenario": analysis.get("opposite_scenario", "시나리오 미정")
            },
            "history_layer": history,
            "last_updated": datetime.now().isoformat()
        }

        # 6. 저장 및 동기화 (v22.0: dashboard/로 단일화)
        output_path = self.dashboard_dir / "today_data.json"
        output_path.write_text(json.dumps(ui_contract, ensure_ascii=False, indent=2), encoding="utf-8")
        
        print(f"  대시보드 데이터 업데이트 완료: {output_path}")


    def update_topics_archive(self, today_data: dict):
        """
        signal_log.json 전체 기반으로 topics/index.json 재구성
        매일 실행 시 전체 아카이브 최신 상태 유지
        """
        signal = today_data.get('signal', {})
        date = today_data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # v22.0: docs/에서 dashboard/로 이동
        items_dir = self.dashboard_dir / 'topics' / 'items'
        items_dir.mkdir(parents=True, exist_ok=True)

        # 신호 기록 업데이트
        if not signal:
            print("  ⏩ [ARCHIVE] No signal to archive today.")
            return

        new_entry = {
            'date': self.today,
            'topic': signal.get('topic', ''),
            'strength': signal.get('strength', 0),
            'anomaly_type': signal.get('anomaly_type', ''),
            'filters_hit': signal.get('filters_hit', ['S']),
            'why_now': signal.get('why_now', ''),
            'path': f'topics/items/{self.today}__top1.json',
            'isToday': False
        }
        item_path = items_dir / f'{self.today}__top1.json'
        with open(item_path, 'w', encoding='utf-8') as f:
            json.dump(new_entry, f, ensure_ascii=False, indent=2)

        # 2. signal_log.json에서 과거 토픽 전체 읽기
        signal_log_path = self.base_dir / 'data' / 'history' / 'signal_log.json'
        archive_list = []

        if signal_log_path.exists():
            with open(signal_log_path, 'r', encoding='utf-8') as f:
                try:
                    log_data = json.load(f)
                    entries = log_data if isinstance(log_data, list) else log_data.get('signals', log_data.get('entries', []))
                    
                    for entry in entries:
                        entry_date = entry.get('date', entry.get('날짜', ''))
                        if len(entry_date) == 8 and "-" not in entry_date:
                            entry_date = f"{entry_date[:4]}-{entry_date[4:6]}-{entry_date[6:]}"
                            
                        entry_topic = entry.get('topic', entry.get('title', entry.get('토픽', '')))
                        entry_strength = entry.get('strength', entry.get('강도', 0))
                        entry_type = entry.get('anomaly_type', entry.get('content_type', entry.get('type', '')))
                        entry_filters = entry.get('filters_hit', ['S'])

                        if entry_date and entry_topic and entry_topic != "없음":
                            archive_list.append({
                                'date': entry_date,
                                'rank': 1,
                                'topic': entry_topic,
                                'strength': entry_strength,
                                'anomaly_type': entry_type,
                                'filters_hit': entry_filters,
                                'path': f'topics/items/{entry_date}__top1.json',
                                'isToday': False
                            })
                except Exception as e:
                    print(f'  signal_log 파싱 오류: {e}')

        # 3. 오늘 항목 포함 (중복 제거 후 맨 앞 추가)
        archive_list = [x for x in archive_list if x.get('date') != date]
        archive_list.append(new_entry)
        
        # 날짜 최신순 정렬 및 최대 60개 유지
        archive_list = sorted(archive_list, key=lambda x: x.get('date', ''), reverse=True)[:60]

        # 4. index.json 저장 (v22.0: dashboard/topics/index.json)
        index_path = self.dashboard_dir / 'topics' / 'index.json'
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(archive_list, f, ensure_ascii=False, indent=2)

        print(f'  topics 아카이브 갱신 완료: {date} (총 {len(archive_list)}개)')

    def generate_brief(self, data: dict) -> str:
        """선장 확인용 브리핑 텍스트 생성 (v12.0 Intelligence Upgrade)"""
        signal = data.get("signal")
        if signal is None:
            signal = {}
        stocks = data.get("stocks")
        if stocks is None:
            stocks = {}
        analysis = data.get("analysis")
        if analysis is None:
            analysis = {}

        stock_list = "\n".join([
            f"  - {s['name']} ({s['sector']}): {s['impact']} — {s['reason']}"
            for s in stocks.get("stocks", [])[:3]
        ])

        # Analyst의 레벨2 체인 우선 순위 적용
        analysis_chain = analysis.get("level2_chain", [])
        signal_chain = signal.get("level2_chain", [])
        final_chain = analysis_chain if analysis_chain else signal_chain

        chain_str = "\n".join([
            f"  {i+1}. {step}"
            for i, step in enumerate(final_chain)
        ])

        collection_status = data.get("collection_status", {})
        failed_agents = collection_status.get("failed_agents", [])
        
        warning_block = ""
        if failed_agents:
            warning_block = f"\n⚠️ [수집 경고]\n{', '.join(failed_agents)}: API 실패 → 해당 지표 분석 제외됨\n"

        # [v14.0] 상세 사유 레이어 구성 (Arbiter & Hunter Insight)
        rationale = signal.get("arbiter_rationale") or signal.get("why_now") or "N/A"
        insight = signal.get("hunter_insight") or "N/A"
        hypothesis = signal.get("why_hypothesis") or "N/A"
        mechanism = signal.get("mechanism") or "N/A"
        confidence = signal.get("hypothesis_confidence") or "MEDIUM"

        # 종목 리스트 구성 (Agent-04 결과 우선)
        stocks_analysis = signal.get("stocks_analysis", {})
        stock_list = ""
        if stocks_analysis and "sectors" in stocks_analysis:
            stock_list = f"  🧱 병목: {stocks_analysis.get('bottleneck', 'N/A')}\n"
            for sector in stocks_analysis.get("sectors", []):
                stock_list += f"  🔹 {sector['name']}\n"
                for s in sector.get("stocks", []):
                    stock_list += f"    - {s['name']}: {s.get('linkage', 'N/A')}\n"
        else:
            display_stocks = signal.get("stocks", [])
            if not display_stocks:
                display_stocks = stocks.get("stocks", [])
            stock_list = "\n".join([
                f"  - {s['name']}: {s.get('reason', s.get('linkage', 'N/A'))}"
                for s in display_stocks[:5]
            ])



        # [v17.2] 세션 비용 로드
        session_path = self.base_dir / "data/monitoring/session_cost.json"
        session_cost_str = "N/A"
        if session_path.exists():
            try:
                s_data = json.loads(session_path.read_text())
                session_cost_str = f"${s_data.get('session_cost', 0.0):.4f}"
            except: pass

        # [v18.3] 초간결 헤더 + 스크립트 전문 체제
        script_body = ""
        script_path = data.get("script_long_path")
        if script_path and Path(script_path).exists():
            script_body = Path(script_path).read_text(encoding="utf-8")
            # [v18.4] 브랜드 명칭 제거 (사용자 요청)
            script_body = script_body.replace("경제사냥꾼", "").replace("[ECONOMIC HUNTER]", "").strip()
        else:
            script_body = "  [알림] 상세 스크립트가 아직 생성되지 않았거나 경로를 찾을 수 없습니다."

        brief = f"""========================================
🏹 HOIN Insight 일일 사냥 보고서 (v18.5)
날짜: {data.get('date', 'N/A')}
소요 비용: {session_cost_str} (USD)
========================================
[1. 오늘의 메인 사냥 토픽] ({data.get('date', 'N/A')})
🎯 주제: {signal.get('event', 'N/A')}
🔥 강도: {signal.get('strength', 'N/A')} / 100
🧠 확신도: {confidence}

{script_body}

=======================
"""
        brief_path = self.dashboard_dir / "today_brief.txt"
        brief_path.write_text(brief, encoding="utf-8")
        print(f"  선장 브리핑 생성 완료 (헤더 + 본문 통합): {brief_path}")
        return brief
        brief_path = self.dashboard_dir / "today_brief.txt"
        brief_path.write_text(brief, encoding="utf-8")
        print(f"  선장 브리핑 생성: {brief_path}")
        return brief

    def run(self, pipeline_results: dict = None):
        print(f"\n📢 AGENT-06 PUBLISHER 시작 [{self.today}]")

        data = self.load_today_data()

        if not data or not data.get("signal"):
            print("  데이터 또는 활성 신호 없음 — 종료")
            return {}

        # [DUPLICATE CHECK] 이미 동일한 토픽으로 오늘 발송했는지 확인
        topic = data["signal"].get("topic", "")
        if self.content_log_path.exists():
            try:
                log = json.loads(self.content_log_path.read_text())
                for entry in log.get("contents", []):
                    if entry.get("date") == f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:]}" and \
                       entry.get("title") == topic and \
                       entry.get("publish_status") == "SUCCESS":
                        print(f"  🚫 [DUPLICATE] 이미 동일한 제목으로 발송된 토픽입니다: {topic}")
                        return {"status": "SKIPPED", "reason": "Already published"}
            except: pass

        # 파이프라인 실시간 결과 반영 (디스크 로딩 보완)
        if pipeline_results:
            if "analyst" in pipeline_results:
                ar = pipeline_results["analyst"]
                if ar.get("analysis"):
                    data["analysis"] = ar["analysis"]
                if ar.get("stocks"):
                    data["stocks"] = ar["stocks"]
                if ar.get("failed"):
                    data["analyst_failed"] = True
                    if "signal" in data:
                        # 신호 객체에도 체인 업데이트 (실패 시 빈 배열 유지)
                        data["signal"]["level2_chain"] = []
                elif ar.get("analysis"):
                    if "signal" in data:
                        data["signal"]["level2_chain"] = ar["analysis"].get("level2_chain", [])

        # 이력 업데이트
        content = self.update_content_log(data)
        self.update_signal_log(data)

        # 대시보드 데이터 생성
        self.generate_dashboard_data(data, content, pipeline_results)
        self.update_topics_archive(data)

        # 선장 브리핑 생성
        brief = self.generate_brief(data)

        # 브리핑 출력
        print(brief)

        # [v24.0] 서버/로컬 환경에 따른 대시보드 URL 지능형 선택
        base_url = os.environ.get("DASHBOARD_URL", "http://localhost:8000").rstrip("/")
        
        # GitHub Pages 등 서브경로 대응을 위해 path 파라미터 전달
        topic_path = content.get('path', '')
        insta_link = f"{base_url}/dashboard/insta_viewer.html?path={topic_path}"
        
        brief_with_link = brief + f"\n\n📸 [카드뉴스 바로보기]\n{insta_link}"
        
        # [지시서 #082] 텔레그램 전송 결과 확인
        success = self.notifier.send_message_in_chunks(brief_with_link)
        if not success:
            print("  ⚠️ [PUBLISHER] 텔레그램 전송 실패 (Warning only)")
        else:
            print("  ✅ [PUBLISHER] 텔레그램 전송 완료 (카드뉴스 링크 포함)")
            # [v24.0] 이미 695번 라인에서 로그가 기록되었으므로, 성공 로그는 중복 없이 상태만 업데이트
            data["signal"]["status"] = "SUCCESS"
            self.update_content_log(data)

        print("✅ AGENT-06 완료\n")
        return {"content": content, "brief": brief}


if __name__ == "__main__":
    agent = PublisherAgent()
    agent.run()
