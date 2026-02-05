document.addEventListener('DOMContentLoaded', async () => {
    const DATA_PATH = '../data/decision/'; // Assuming UI is in /ui/ and data in /data/decision/
    const MOCK_FALLBACK = true;

    async function loadJson(file, isCritical = false) {
        try {
            const path = file === 'build_meta.json' ? '../data/' : DATA_PATH;
            const res = await fetch(path + file);
            if (!res.ok) throw new Error(`Status ${res.status}`);
            const data = await res.json();

            // Adapter: Auto-convert list to dict if needed
            if (Array.isArray(data)) {
                const dict = {};
                data.forEach(item => {
                    const id = item.interpretation_id || item.topic_id || item.id;
                    if (id) dict[id] = item;
                });
                return dict;
            }
            return data;
        } catch (e) {
            console.warn(`[DATA] Failed to load ${file}: ${e.message}`);
            if (isCritical) {
                showDiagnostic(file, e.message);
            }
            return {}; // Return empty dict instead of null to prevent "cannot read property of null"
        }
    }

    function showDiagnostic(file, error) {
        let diag = document.getElementById('diag-banner');
        if (!diag) {
            diag = document.createElement('div');
            diag.id = 'diag-banner';
            diag.className = 'diag-banner';
            document.getElementById('app').prepend(diag);
        }
        const msg = document.createElement('div');
        msg.innerHTML = `⚠️ <b>데이터 로드 실패:</b> ${file} (${error})<br>
                        &nbsp;&nbsp;👉 해결: GitHub Actions → <code>full_pipeline</code> 실행 및 <code>docs/data/decision</code> 배포 확인.`;
        diag.appendChild(msg);
    }

    // 0. Load Build Meta
    const buildMeta = await loadJson('build_meta.json');
    if (buildMeta) {
        const info = document.createElement('div');
        info.style.fontSize = '0.75rem';
        info.style.color = 'var(--text-secondary)';
        info.style.marginBottom = '10px';
        info.innerText = `Build: ${buildMeta.date_kst || buildMeta.timestamp} | Commit: ${buildMeta.commit.substring(0, 7)}`;
        document.getElementById('app').prepend(info);
    }

    // 1. Load All Data
    const [unitsDict, briefingDict, heroSummary, hookData, topRisks, calendar180, decision, skeleton, mentionables, evidence, packs] = await Promise.all([
        loadJson('interpretation_units.json', true),
        loadJson('natural_language_briefing.json'),
        loadJson('../ui/hero_summary.json'),
        loadJson('../ui/narrative_entry_hook.json'),
        loadJson('../ui/upcoming_risk_topN.json'), // IS-102
        loadJson('../ui/schedule_risk_calendar_180d.json'), // IS-102
        loadJson('speakability_decision.json'),
        loadJson('narrative_skeleton.json'),
        loadJson('mentionables.json'),
        loadJson('evidence_citations.json'),
        loadJson('content_pack.json')
    ]);

    const unitKeys = Object.keys(unitsDict);
    if (unitKeys.length === 0) {
        document.getElementById('issue-hook').innerText = "오늘은 확정된 구조적 판단이 없습니다.";
        return;
    }

    // Pick Top-1 Unit
    const unitId = unitKeys[0];
    const topUnit = unitsDict[unitId];
    const briefing = briefingDict ? briefingDict[unitId] : null;

    // 1.5 Render [BLOCK -1] Entry Hook (IS-101-2)
    if (hookData && hookData.entry_sentence) {
        const hookContainer = document.createElement('div');
        hookContainer.id = 'narrative-hook';
        hookContainer.style.background = 'linear-gradient(90deg, #FFD700 0%, #FFA500 100%)';
        hookContainer.style.color = '#000';
        hookContainer.style.padding = '15px 25px';
        hookContainer.style.fontWeight = '900';
        hookContainer.style.fontSize = '1.2rem';
        hookContainer.style.textAlign = 'center';
        hookContainer.style.borderRadius = '8px';
        hookContainer.style.marginBottom = '25px';
        hookContainer.style.boxShadow = '0 4px 15px rgba(255, 215, 0, 0.3)';
        hookData.confidence_level === 'HIGH' ? hookContainer.style.border = '2px solid #fff' : null;

        hookContainer.innerText = `📢 ${hookData.entry_sentence}`;
        document.getElementById('app').prepend(hookContainer);
    }

    // 2. Render Header & Global Status
    document.getElementById('current-date').innerText = topUnit.as_of_date || new Date().toISOString().split('T')[0];
    const globalStatus = document.getElementById('global-status-badge');
    const flag = heroSummary?.status || decision[unitId]?.speakability_flag || 'HOLD';

    globalStatus.innerText = flag === 'READY' ? '🟢 READY' : (flag === 'HYPOTHESIS' ? '🟡 HYPOTHESIS' : '🔴 HOLD');
    globalStatus.className = `badge ${flag.toLowerCase()}`;

    // 3. Render [BLOCK 0] Hero Sentence
    // Diagnostic log for IS-100 [FIX]
    console.log('[IS-100] Data Diagnostics:', {
        heroSummary: {
            hasData: !!heroSummary,
            headline: heroSummary?.headline,
            oneLiner: heroSummary?.one_liner
        },
        briefing: {
            hasData: !!briefing,
            sentence: briefing?.hero?.sentence
        },
        topUnit: {
            hasData: !!topUnit,
            id: topUnit?.interpretation_id,
            theme: topUnit?.theme
        }
    });

    let heroTitle = "";
    let heroOneLiner = "";

    if (heroSummary && heroSummary.headline && heroSummary.one_liner) {
        heroTitle = heroSummary.headline;
        heroOneLiner = heroSummary.one_liner;
    } else if (briefing && briefing.hero && briefing.hero.sentence) {
        heroTitle = briefing.hero.sentence;
        heroOneLiner = briefing.hero.metric || "구조적 변화 신호 포착";
    } else {
        // Ultimate fallback: generate from topUnit (Decision logic)
        const sector = topUnit.target_sector || "알 수 없는 섹터";
        const theme = topUnit.theme || "구조적 변화";
        heroTitle = `${sector} ${theme} 분석`;
        heroOneLiner = "단순 뉴스가 아니라 구조 변화입니다.";
    }

    // Ensure no 'undefined' reaches the innerHTML
    heroTitle = heroTitle || "인사이트 데시보드";
    heroOneLiner = heroOneLiner || "데이터 수집 및 분석 중입니다.";

    document.getElementById('issue-hook').innerHTML = `
        <div style="font-size: 1.8rem; font-weight: 800; color: #fff; margin-bottom: 10px;">${heroTitle}</div>
        <div style="font-size: 1.1rem; border-left: 3px solid var(--accent-blue); padding-left: 15px; margin: 15px 0;">${heroOneLiner}</div>
    `;

    // 4. Render [BLOCK 1] Speakability
    if (briefing) {
        document.getElementById('speakability-badge').innerText = flag;
        document.getElementById('speakability-badge').className = `badge ${flag.toLowerCase()}`;

        const bDec = briefing.decision;
        document.getElementById('operator-guide').innerHTML = `
            <div style="font-weight: 800; margin-bottom: 12px; font-size: 1.1rem;">${bDec.title}</div>
            <div style="font-size: 0.95rem; line-height: 1.6;">
                ${bDec.points.map(p => `<div>${p}</div>`).join('')}
            </div>
        `;
    }

    // 5. Render [BLOCK 2] Why Now (Logic Chain)
    if (briefing) {
        const bWhy = briefing.why_now;
        document.getElementById('logic-steps').innerHTML = `
            <div style="margin-top: 10px;">
                ${bWhy.items.map((item, idx) => `
                    <div style="margin-bottom: 12px; display: flex; align-items: flex-start;">
                        <span style="font-weight: 800; color: var(--accent-blue); margin-right: 10px;">${idx + 1}️⃣</span>
                        <span style="font-size: 0.95rem;">${item}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // 6. Render [BLOCK 3] Perspectives (Mentionables)
    if (briefing) {
        const bPersp = briefing.perspectives;
        document.getElementById('mention-cards').innerHTML = `
            <div class="card-large" style="width: 100%; box-sizing: border-box; background: var(--card-bg);">
                <div style="font-weight: 800; margin-bottom: 15px; color: var(--status-ready);">${bPersp.title}</div>
                ${bPersp.items.map(item => `
                    <div style="margin-bottom: 10px; font-size: 0.95rem; display: flex; align-items: center;">
                        <span style="color: var(--accent-blue); margin-right: 8px;">•</span>
                        <span>${item}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // 7. Render [BLOCK 4] Trust (Evidence List)
    if (heroSummary && heroSummary.numbers_with_evidence) {
        document.getElementById('evidence-list').innerHTML = `
            <div class="card" style="width: 100%; box-sizing: border-box; border-left: 4px solid var(--status-ready);">
                <div style="font-weight: 800; margin-bottom: 15px;">📊 핵심 수치 및 근거</div>
                ${heroSummary.numbers_with_evidence.map(item => `
                    <div style="margin-bottom: 8px; font-size: 0.95rem;">
                        ${item}
                    </div>
                `).join('')}
                <div style="margin-top: 15px; font-size: 0.85rem; color: var(--text-secondary); font-style: italic;">
                    🚨 리스크: ${heroSummary.risk_note}
                </div>
            </div>
        `;
    } else if (briefing) {
        const bTrust = briefing.trust;
        document.getElementById('evidence-list').innerHTML = `
            <div class="card" style="width: 100%; box-sizing: border-box; border-left: 4px solid var(--status-ready);">
                <div style="font-weight: 800; margin-bottom: 15px;">${bTrust.title}</div>
                ${bTrust.items.map(item => `
                    <div style="margin-bottom: 8px; font-size: 0.9rem;">
                        ${item}
                    </div>
                `).join('')}
            </div>
        `;
    }

    // 8. Render [BLOCK 5] Checklist
    if (briefing) {
        const bCheck = briefing.checklist;
        document.getElementById('checklist-items').innerHTML = bCheck.items.map(item => `
            <li style="margin-bottom: 10px; display: flex; align-items: center;">
                <span style="margin-right: 10px;">☑</span>
                <span>${item}</span>
            </li>
        `).join('');
    }

    // 8. Render [IS-102] Upcoming Risks & Calendar
    if (topRisks && topRisks.items) {
        const riskSection = document.createElement('section');
        riskSection.className = 'section';
        riskSection.innerHTML = `
            <h2 class="section-title">📅 다가오는 90일 주요 리스크 (Top 7)</h2>
            <div class="card-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px;">
                ${topRisks.items.map(r => `
                    <div class="card" style="border-top: 3px solid #FF4500;">
                        <div style="font-weight: 800; color: #FF4500;">${r.date} | Rank ${r.rank}</div>
                        <div style="font-size: 1.1rem; font-weight: 800; margin: 8px 0;">${r.title}</div>
                        <div style="font-size: 0.9rem; color: var(--text-secondary);">${r.one_liner}</div>
                    </div>
                `).join('')}
            </div>
            
            <div style="margin-top: 20px;">
                <button id="toggle-calendar" class="badge" style="cursor: pointer; padding: 10px 20px; font-size: 0.9rem; width: 100%; text-align: center;">
                    🗓️ 180일 전체 캘린더 보기/접기
                </button>
                <div id="calendar-full" style="display: none; margin-top: 15px; max-height: 400px; overflow-y: auto; background: var(--card-bg); padding: 20px; border-radius: 8px;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                        <thead style="border-bottom: 2px solid var(--border);">
                            <tr>
                                <th style="padding: 10px; text-align: left;">날짜</th>
                                <th style="padding: 10px; text-align: left;">지역</th>
                                <th style="padding: 10px; text-align: left;">일정</th>
                                <th style="padding: 10px; text-align: left;">영향</th>
                                <th style="padding: 10px; text-align: right;">점수</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${calendar180.items.map(i => `
                                <tr style="border-bottom: 1px solid var(--border);">
                                    <td style="padding: 10px;">${i.date}</td>
                                    <td style="padding: 10px;"><span class="tag-badge">${i.region}</span></td>
                                    <td style="padding: 10px; font-weight: 600;">${i.title}</td>
                                    <td style="padding: 10px; font-size: 0.8rem;">${i.risk_mechanism}</td>
                                    <td style="padding: 10px; text-align: right; color: var(--accent-blue);">${i.final_score}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        document.getElementById('operator-view').insertBefore(riskSection, document.getElementById('evidence'));

        document.getElementById('toggle-calendar').addEventListener('click', () => {
            const cal = document.getElementById('calendar-full');
            cal.style.display = cal.style.display === 'none' ? 'block' : 'none';
        });
    }

    // 9. Content Packs (Existing logic but simplified)
    const unitPacks = packs ? (packs[unitId] || packs[topUnit.topic_id]) : null;
    if (unitPacks) {
        const pList = unitPacks.packs || [unitPacks];
        document.getElementById('pack-container').innerHTML = pList.map(p => `
            <div class="pack-card">
                <div>
                    <span class="tag-badge">${p.format}</span>
                    <span style="font-weight: bold;">${p.title}</span>
                </div>
            </div>
        `).join('');
    }
});
