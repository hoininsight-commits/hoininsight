# src/agents/publisher.py
# AGENT-06 PUBLISHER
# 역할: 이력 저장 + 대시보드 업데이트 + 선장 브리핑

import json
import re
from datetime import datetime
from pathlib import Path
from src.utils.telegram_notifier import TelegramNotifier


class PublisherAgent:

    def __init__(self):
        # Modular CI/CD Trigger Test - FIXED
        import os
        self.base_dir = Path(os.getenv("HOIN_BASE_DIR", Path(__file__).resolve().parents[2]))
        self.today = datetime.now().strftime("%Y%m%d")
        self.content_log_path = Path("data/history/content_log.json")
        self.signal_log_path = Path("data/history/signal_log.json")
        self.dashboard_dir = Path("dashboard")
        self.dashboard_dir.mkdir(exist_ok=True)
        self.notifier = TelegramNotifier()

    def load_today_data(self) -> dict:
        """오늘 생성된 모든 데이터 로드"""
        data = {}

        def safe_load_json(path: Path):
            try:
                return json.loads(path.read_text(encoding='utf-8'))
            except:
                return None

        # 신호 (v4.0: data/topics/topic_selection.json 우선 로드)
        topic_sel_p = self.base_dir / "data/topics/topic_selection.json"
        if topic_sel_p.exists():
            res = safe_load_json(topic_sel_p)
            if res and res.get("MAIN"):
                # Detector의 MAIN 결과를 Publisher 규격으로 변환
                main = res["MAIN"]
                data["signal"] = {
                    "topic": main.get("event", main.get("topic", "")),
                    "event": main.get("event", ""),
                    "strength": main.get("final_score", 0) * 10,
                    "content_type": "롱폼" if main.get("tier") == "MAIN/TIER_1" else "쇼츠",
                    "filters_hit": [main.get("structure_axis", "S")],
                    "why_now": main.get("why_now", main.get("selection_reason", "")),
                    "why_hypothesis": main.get("why_hypothesis", ""),
                    "mechanism": main.get("mechanism", ""),
                    "hypothesis_confidence": main.get("hypothesis_confidence", ""),
                    "is_mismatch": main.get("is_mismatch", False)
                }
                print(f"  [DEBUG] Loaded Topic Selection MAIN: {data['signal']['topic']}")
        
        if "signal" not in data:
            for d in sorted(Path("data/signals").iterdir(), reverse=True):
                p = d / "today_signal.json"
                if p.exists():
                    res = safe_load_json(p)
                    if res:
                        data["signal"] = res
                        break

        # 분석
        if Path("data/analysis").exists():
            for d in sorted(Path("data/analysis").iterdir(), reverse=True):
                p = d / "today_analysis.json"
                if p.exists():
                    res = safe_load_json(p)
                    if res:
                        data["analysis"] = res
                        break

        # 종목
        if Path("data/analysis").exists():
            for d in sorted(Path("data/analysis").iterdir(), reverse=True):
                p = d / "today_stocks.json"
                if p.exists():
                    res = safe_load_json(p)
                    if res:
                        data["stocks"] = res
                        break

        # 스크립트
        if Path("data/scripts").exists():
            for d in sorted(Path("data/scripts").iterdir(), reverse=True):
                p = d / "today_script_long.md"
                if p.exists():
                    data["script_long_path"] = str(p)
                    break

            for d in sorted(Path("data/scripts").iterdir(), reverse=True):
                p = d / "today_script_short.md"
                if p.exists():
                    data["script_short_path"] = str(p)
                    break

        # 후보 목록 (v2.0: data/topics/topic_candidates.json 대응)
        topic_p = self.base_dir / "data/topics/topic_candidates.json"
        if topic_p.exists():
            res = safe_load_json(topic_p)
            print(f"  [DEBUG] Loaded topic_candidates.json: {len(res) if isinstance(res, list) else 'N/A'} items")
            if res:
                data["candidates"] = {"candidates": res} if isinstance(res, list) else res
        else:
            print(f"  [DEBUG] topic_candidates.json NOT FOUND at {topic_p}")
            # Fallback to signals dir
            for d in sorted(Path("data/signals").iterdir(), reverse=True):
                p = d / "topic_candidates.json"
                if not p.exists():
                    p = d / "candidates.json"
                if p.exists():
                    res = safe_load_json(p)
                    if res:
                        data["candidates"] = {"candidates": res} if isinstance(res, list) else res
                        break

        # market 데이터
        if Path("data/raw").exists():
            for d in sorted(Path("data/raw").iterdir(), reverse=True):
                p = d / "market.json"
                if p.exists():
                    res = safe_load_json(p)
                    if res:
                        data["market"] = res
                        break

        # macro 데이터
        if Path("data/raw").exists():
            for d in sorted(Path("data/raw").iterdir(), reverse=True):
                p = d / "macro.json"
                if p.exists():
                    res = safe_load_json(p)
                    if res:
                        data["macro"] = res
                        break

        # sentiment 데이터
        if Path("data/raw").exists():
            for d in sorted(Path("data/raw").iterdir(), reverse=True):
                p = d / "sentiment.json"
                if p.exists():
                    res = safe_load_json(p)
                    if res:
                        data["sentiment"] = res
                        break

        # putcall 데이터
        p = Path("data/outputs/putcall.json")
        if p.exists():
            res = safe_load_json(p)
            if res:
                data["putcall"] = res

        # [지시서 #055] COT 데이터 로드
        if Path("data/raw").exists():
            for d in sorted(Path("data/raw").iterdir(), reverse=True):
                p = d / "cot.json"
                if p.exists():
                    res = safe_load_json(p)
                    if res:
                        data["cot"] = res
                        break

        # collection_status 데이터
        if Path("data/raw").exists():
            for d in sorted(Path("data/raw").iterdir(), reverse=True):
                p = d / "collection_status.json"
                if p.exists():
                    res = safe_load_json(p)
                    if res:
                        data["collection_status"] = res
                        break

        return data

    def update_content_log(self, data: dict) -> dict:
        """content_log.json에 오늘 콘텐츠 추가"""
        signal = data.get("signal", {})
        if not signal:
            print("  신호 없음 — 이력 업데이트 건너뜀")
            return {}

        stocks = data.get("stocks", {})
        stock_names = [
            s["name"] for s in stocks.get("stocks", [])[:3]
        ]

        # 새 콘텐츠 항목
        new_content = {
            "id": f"{self.today}_001",
            "date": f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:]}",
            "type": signal.get("content_type", "롱폼"),
            "title": signal.get("topic", ""),
            "thumbnail_text": "",
            "duration_min": 15 if signal.get("content_type") == "롱폼" else 2,
            "signal_strength": signal.get("strength", 0),
            "filters_used": signal.get("filters_hit", []),
            "stocks": stock_names,
            "is_republish": signal.get("is_republish", False),
            "original_id": None,
            "script_path": data.get("script_long_path", ""),
            "status": "승인대기",
            "operator_approved": False,
            "approved_at": None,
            "publish_status": signal.get("status", "UNKNOWN")
        }

        # 기존 이력 로드
        log = {"contents": []}
        if self.content_log_path.exists():
            try:
                log = json.loads(self.content_log_path.read_text())
            except Exception:
                pass

        # 오늘 날짜 이미 있으면 업데이트, 없으면 추가
        existing_ids = [c["id"] for c in log["contents"]]
        if new_content["id"] not in existing_ids:
            log["contents"].append(new_content)
        else:
            log["contents"] = [
                new_content if c["id"] == new_content["id"] else c
                for c in log["contents"]
            ]

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
        signal = data.get("signal", {})
        analysis = data.get("analysis", {})
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
                selected_title = signal.get("event", signal.get("topic", ""))
                
                for i, cand in enumerate(all_candidates):
                    cand_title = cand.get("event", cand.get("topic", ""))
                    is_winner = cand_title == selected_title and selected_title != ""
                    
                    if i < 3: # 첫 3개만 로깅
                        print(f"  [DEBUG] Processing cand {i}: title='{cand_title}', winner={is_winner}")
                    
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
                        "confidence": cand.get("hypothesis_confidence", cand.get("confidence", ""))
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

        # 6. 저장 및 동기화
        output_path = self.dashboard_dir / "today_data.json"
        output_path.write_text(json.dumps(ui_contract, ensure_ascii=False, indent=2))
        
        docs_dir = self.base_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        (docs_dir / "today_data.json").write_text(json.dumps(ui_contract, ensure_ascii=False, indent=2))
        
        print(f"  대시보드 데이터 및 HTML 동기화 완료: {docs_dir}")


    def update_topics_archive(self, today_data: dict):
        """
        signal_log.json 전체 기반으로 topics/index.json 재구성
        매일 실행 시 전체 아카이브 최신 상태 유지
        """
        signal = today_data.get('signal', {})
        date = today_data.get('date', datetime.now().strftime('%Y-%m-%d'))

        items_dir = self.base_dir / 'docs' / 'topics' / 'items'
        items_dir.mkdir(parents=True, exist_ok=True)

        # 1. 오늘 상세 파일 저장
        item_today = {
            'date': date,
            'rank': 1,
            'topic': signal.get('topic', ''),
            'strength': signal.get('strength', 0),
            'anomaly_type': signal.get('anomaly_type', ''),
            'filters_hit': signal.get('filters_hit', ['S']),
            'why_now': signal.get('why_now', ''),
            'path': f'topics/items/{date}__top1.json',
            'isToday': False
        }
        item_path = items_dir / f'{date}__top1.json'
        with open(item_path, 'w', encoding='utf-8') as f:
            json.dump(item_today, f, ensure_ascii=False, indent=2)

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
        archive_list.append(item_today)
        
        # 날짜 최신순 정렬 및 최대 60개 유지
        archive_list = sorted(archive_list, key=lambda x: x.get('date', ''), reverse=True)[:60]

        # 4. index.json 저장
        index_path = self.base_dir / 'docs' / 'topics' / 'index.json'
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(archive_list, f, ensure_ascii=False, indent=2)

        print(f'  topics 아카이브 갱신 완료: {date} (총 {len(archive_list)}개)')

    def generate_brief(self, data: dict) -> str:
        """선장 확인용 브리핑 텍스트 생성 (v12.0 Intelligence Upgrade)"""
        signal = data.get("signal", {})
        stocks = data.get("stocks", {})
        analysis = data.get("analysis", {})

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

        # [v12.0] 상세 사유 레이어 구성
        rationale = signal.get("why_now", "데이터 분석 기반 자율 선정")
        hypothesis = signal.get("why_hypothesis", "N/A")
        mechanism = signal.get("mechanism", "N/A")
        confidence = signal.get("hypothesis_confidence", "MEDIUM")

        brief = f"""
========================================
🏹 HOIN Insight 일일 사냥 보고서
날짜: {self.today[:4]}-{self.today[4:6]}-{self.today[6:]}
========================================{warning_block}

[1. 오늘의 메인 사냥 토픽]
🎯 주제: {signal.get("topic", "없음")}
🔥 강도: {signal.get("strength", 0)} / 10
🧠 확신도: {confidence}

[2. 선정 사유 (Selection Rationale)]
📝 {rationale}

[3. AI 가설 및 메커니즘]
💡 가설 (Why Now): {hypothesis}
⚙️ 작동 원리 (Mechanism): {mechanism}

[4. 레벨2 인과관계]
{chain_str if chain_str else ("  분석 실패 (AGENT-04 오류)" if data.get("analyst_failed") else "  없음 (AGENT-04 미실행)")}

[5. 관련 종목 (Market Target)]
{stock_list if stock_list else ("  매핑 실패 (AGENT-04 오류)" if data.get("analyst_failed") else "  종목 데이터 없음 (AGENT-04 미실행)")}

[6. 산출물 경로]
🎬 롱폼: {data.get("script_long_path", "미생성")}
📱 쇼츠: {data.get("script_short_path", "미생성")}

========================================
선장님, 대시보드에서 최종 승인 후 발행을 진행해주세요.
========================================
"""
        brief_path = self.dashboard_dir / "today_brief.txt"
        brief_path.write_text(brief, encoding="utf-8")
        print(f"  선장 브리핑 생성 완료 (상세 사유 포함): {brief_path}")
        return brief
        brief_path = self.dashboard_dir / "today_brief.txt"
        brief_path.write_text(brief, encoding="utf-8")
        print(f"  선장 브리핑 생성: {brief_path}")
        return brief

    def run(self, pipeline_results: dict = None):
        print(f"\n📢 AGENT-06 PUBLISHER 시작 [{self.today}]")

        data = self.load_today_data()

        if not data:
            print("  데이터 없음 — 종료")
            return {}

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

        # [지시서 #054] 텔레그램 전송 (본문 포함)
        brief_with_script = brief
        script_path = data.get("script_long_path")
        if script_path and Path(script_path).exists():
            script_body = Path(script_path).read_text(encoding="utf-8")
            brief_with_script += f"\n\n[📜 롱폼 스크립트 전문]\n\n{script_body}"
        
        # [지시서 #082] 텔레그램 전송 결과 확인
        # 텔레그램은 알림 수단 — 전송 실패가 파이프라인 전체 실패로 이어지면 안 됨
        success = self.notifier.send_message_in_chunks(brief_with_script)
        if not success:
            print("  ⚠️ [PUBLISHER] 텔레그램 전송 실패 (Warning only — 파이프라인 계속)")
        else:
            print("  ✅ [PUBLISHER] 텔레그램 전송 완료")

        print("✅ AGENT-06 완료\n")
        return {"content": content, "brief": brief}


if __name__ == "__main__":
    agent = PublisherAgent()
    agent.run()
