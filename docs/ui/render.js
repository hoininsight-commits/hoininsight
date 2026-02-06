document.addEventListener('DOMContentLoaded', async () => {
    // [REF-001] Unified Data Paths
    const BASE_PATH = '/hoininsight/data/'; // Canonical base for GitHub Pages
    const LOCAL_DATA_PATH = '../data/';   // Fallback for local development

    // UI Helpers to prevent "undefined"
    const safeText = (v) => v === undefined || v === null ? "" : String(v);
    const safeArray = (v) => Array.isArray(v) ? v : [];
    const safeObj = (v) => (v && typeof v === 'object' && !Array.isArray(v)) ? v : {};

    // [REF-011] Deeply safe getter
    const safeGet = (obj, path, fallback = "") => {
        const value = path.split('.').reduce((acc, part) => (acc && acc[part] !== undefined) ? acc[part] : undefined, obj);
        if (value === undefined || value === null) return fallback;
        if (typeof value === 'string' && (value.toLowerCase() === 'undefined' || value.toLowerCase() === 'null')) return fallback;
        return value;
    };

    async function loadJson(file, isCritical = false) {
        // Try multiple paths: canonical first, then local fallback
        const paths = [BASE_PATH + file, LOCAL_DATA_PATH + file];

        for (const path of paths) {
            try {
                const res = await fetch(path);
                if (!res.ok) continue;
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
                console.warn(`[DATA] Fetch failed for ${path}: ${e.message}`);
            }
        }

        if (isCritical) showDiagnostic(file, "데이터를 찾을 수 없습니다.");
        return null;
    }

    function showDiagnostic(file, error) {
        let diag = document.getElementById('diag-banner');
        if (!diag) {
            diag = document.createElement('div');
            diag.id = 'diag-banner';
            diag.className = 'diag-banner';
            const app = document.getElementById('app');
            if (app) app.prepend(diag);
        }
        const msg = document.createElement('div');
        msg.innerHTML = `⚠️ <b>데이터 로드 실패:</b> ${file} (${error})<br>
                        &nbsp;&nbsp;👉 해결: GitHub Actions → <code>full_pipeline</code> 실행 및 <code>docs/data/</code> 배포 확인.`;
        if (diag) diag.appendChild(msg);
    }

    // 0. Load Manifest (REF-001 Core)
    const manifest = await loadJson('ui/manifest.json');
    console.log('[REF-001] Manifest Loaded:', manifest);

    // 1. Load All Data (Defensive)
    const [unitsDict, briefingDict, heroSummary, mainCard, hookData, topRisks, calendar180, decision, operatorNarrativeOrder, dailyPackage] = await Promise.all([
        loadJson('decision/interpretation_units.json', true),
        loadJson('decision/natural_language_briefing.json'),
        loadJson('ui/hero_summary.json'),
        loadJson('ui/operator_main_card.json'),
        loadJson('ui/narrative_entry_hook.json'),
        loadJson('ui/upcoming_risk_topN.json'),
        loadJson('ui/schedule_risk_calendar_180d.json'),
        loadJson('decision/speakability_decision.json'),
        loadJson('ui/operator_narrative_order.json'),
        loadJson('ui/daily_content_package.json')
    ]);

    // Manifest-driven fallback: if interpretation_units missing, don't return!
    const unitKeys = unitsDict ? Object.keys(unitsDict) : [];
    if (unitKeys.length === 0) {
        console.warn('[REF-001] No interpretation_units found. Rendering placeholder Decision Zone.');
        const placeholder = document.createElement('div');
        placeholder.style.padding = '20px';
        placeholder.style.background = 'rgba(255,255,255,0.05)';
        placeholder.style.borderRadius = '8px';
        placeholder.style.textAlign = 'center';
        placeholder.innerHTML = `<h2 style="color:var(--text-secondary)">⚠️ 현재 구조적 판단 데이터가 없습니다.</h2><p>엔진이 데이터를 정제 중이거나 수집된 신호가 부족합니다.</p>`;
        document.getElementById('app').prepend(placeholder);
    }

    if (!manifest) {
        const emergencyCard = document.createElement('div');
        emergencyCard.className = 'card-highlight';
        emergencyCard.style.margin = '20px';
        emergencyCard.innerHTML = `
            <h2>⚠️ 데이터 생성 실패 / 미배포 안내</h2>
            <p>현재 대시보드 메니페스트를 불러올 수 없습니다. 파이프라인이 완료되었는지 확인하십시오.</p>
            <div style="margin-top: 15px; font-size: 0.8em;">
                디버그 링크: 
                <a href="../data/ui/" style="color: #60a5fa;">[UI 데이터 보관소]</a> | 
                <a href="../data/decision/" style="color: #60a5fa;">[의사결정 보관소]</a>
            </div>
        `;
        document.getElementById('operator-view').prepend(emergencyCard);
    }

    // [IS-113] Narrative Order Mode Dispatch
    if (operatorNarrativeOrder && operatorNarrativeOrder.content_package) {
        console.log('[IS-113] Narrative Order Mode Activated');
        renderNarrativeOrderMode(operatorNarrativeOrder);
        return; // PREVENT LEGACY RENDER
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
    // Diagnostic log for IS-100 [FIX] & IS-103
    console.log('[IS-103] Main Card Data:', mainCard);

    let heroTitle = "";
    let heroOneLiner = "";
    let mainStatus = "HOLD";
    let whyNowItems = [];
    let riskNote = "";

    if (mainCard && mainCard.hero) {
        heroTitle = mainCard.hero.headline;
        heroOneLiner = mainCard.hero.one_liner;
        mainStatus = mainCard.hero.status;
        whyNowItems = mainCard.hero.why_now;
        riskNote = mainCard.hero.risk_note;
    } else if (heroSummary) {
        heroTitle = heroSummary.headline;
        heroOneLiner = heroSummary.one_liner;
        mainStatus = heroSummary.status || "HOLD";
        whyNowItems = heroSummary.why_now || [];
        riskNote = heroSummary.risk_note || "";
    } else if (briefing) {
        heroTitle = briefing.hero.sentence;
        heroOneLiner = briefing.hero.metric || "구조적 변화 신호 포착";
    } else {
        const sector = topUnit.target_sector || "알 수 없는 섹터";
        const theme = topUnit.theme || "구조적 변화";
        heroTitle = `${sector} ${theme} 분석`;
        heroOneLiner = "단순 뉴스가 아니라 구조 변화입니다.";
    }

    // Hard guard against undefined
    heroTitle = heroTitle || "인사이트 대시보드";
    heroOneLiner = heroOneLiner || "데이터 수집 및 분석 중입니다.";

    document.getElementById('issue-hook').innerHTML = `
        <div style="font-size: 1.8rem; font-weight: 800; color: #fff; margin-bottom: 10px;">${heroTitle}</div>
        <div style="font-size: 1.1rem; border-left: 3px solid var(--accent-blue); padding-left: 15px; margin: 15px 0;">${heroOneLiner}</div>
    `;

    // 3.5 Render Why-now bullets (IS-103 requirement: Line 2-3 are Why-now)
    if (whyNowItems.length > 0) {
        const whyContainer = document.getElementById('issue-why-now');
        whyContainer.innerHTML = whyNowItems.map(item => `
            <div style="margin-bottom: 5px; font-weight: 600; color: #cbd5e1;">• ${item}</div>
        `).join('');
    }

    // 4. Render [IS-103] Three-Eye Check & Numbers
    if (mainCard && mainCard.three_eye) {
        const eyeSection = document.createElement('section');
        eyeSection.className = 'section card';
        eyeSection.innerHTML = `
            <h2 class="section-title">🛡️ 3-Eye Structural Checks</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                ${mainCard.three_eye.map(e => `
                    <div style="padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid var(--border);">
                        <div style="font-weight: 800;">${e.ok ? '✅' : '⚠️'} ${e.eye}</div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px;">${e.evidence}</div>
                    </div>
                `).join('')}
            </div>
        `;
        document.getElementById('operator-view').insertBefore(eyeSection, document.getElementById('mentionables'));
    }

    if (mainCard && mainCard.numbers) {
        const numSection = document.createElement('section');
        numSection.className = 'section card-highlight';
        numSection.innerHTML = `
            <h2 class="section-title">📊 핵심 지표 및 근거 (Top 4)</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                ${mainCard.numbers.map(n => `<div style="padding: 10px; background: #fff; color: #000; border-radius: 4px; font-weight: 600;">${n}</div>`).join('')}
            </div>
            <div style="margin-top: 15px; font-size: 0.9rem; color: #FF4500; font-weight: 800;">🚨 리스크 트: ${riskNote}</div>
        `;
        // Replace old evidence section or insert before
        document.getElementById('operator-view').insertBefore(numSection, document.getElementById('evidence'));
        document.getElementById('evidence').style.display = 'none';
    }

    // 5. Render [IS-103] Mentionables by Role
    if (mainCard && mainCard.mentionables_by_role) {
        const mGrid = document.getElementById('mention-cards');
        const roles = mainCard.mentionables_by_role;
        mGrid.innerHTML = `
            <div class="card" style="border-left: 4px solid #f87171;">
                <div style="font-weight: 800; color: #ef4444;">🚫 BOTTLENECK</div>
                ${roles.BOTTLENECK.map(item => `<div style="margin-top: 8px; font-size: 0.95rem;">${item}</div>`).join('')}
            </div>
            <div class="card" style="border-left: 4px solid #60a5fa;">
                <div style="font-weight: 800; color: #3b82f6;">⛏️ PICKAXE</div>
                ${roles.PICKAXE.map(item => `<div style="margin-top: 8px; font-size: 0.95rem;">${item}</div>`).join('')}
            </div>
            <div class="card" style="border-left: 4px solid #fbbf24;">
                <div style="font-weight: 800; color: #f59e0b;">🛡️ HEDGE</div>
                ${roles.HEDGE.map(item => `<div style="margin-top: 8px; font-size: 0.95rem;">${item}</div>`).join('')}
            </div>
        `;
    }

    // [IS-104] Render Multi-Topic Content Package
    if (dailyPackage && dailyPackage.long_form) {
        const pkgSection = document.createElement('section');
        pkgSection.className = 'section card-highlight';
        pkgSection.style.background = 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)';
        pkgSection.style.border = '1px solid #334155';

        const long = dailyPackage.long_form;
        const shorts = dailyPackage.short_forms || [];

        pkgSection.innerHTML = `
            <h2 class="section-title" style="color: #60a5fa;">🎬 오늘의 메인 컨텐츠 (Long-form)</h2>
            <div style="margin-bottom: 25px;">
                <div style="font-size: 1.4rem; font-weight: 800; color: #fff;">${long.title}</div>
                <div style="margin-top: 10px; color: #94a3b8; line-height: 1.6;">${long.reason}</div>
                <div style="margin-top: 10px;"><span class="badge ${long.confidence.toLowerCase()}">${long.confidence}</span></div>
            </div>

            <h3 style="font-size: 1.1rem; color: #94a3b8; margin-bottom: 15px; border-bottom: 1px solid #334155; padding-bottom: 10px;">📱 함께 보면 좋은 숏 (Short-form)</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px;">
                ${shorts.map(s => `
                    <div style="padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid #334155;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <span style="font-size: 0.75rem; color: #60a5fa; font-weight: 800;">${s.type}</span>
                        </div>
                        <div style="font-weight: 700; margin-top: 5px; color: #e2e8f0;">${s.angle}</div>
                        <div style="margin-top: 8px; font-size: 0.9rem; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px;">"${s.hook}"</div>
                    </div>
                `).join('')}
            </div>
        `;
        document.getElementById('operator-view').prepend(pkgSection);
    }

    // [IS-105] Render Capital Perspective (Capital Eye)
    if (capitalPerspective && capitalPerspective.headline) {
        const capSection = document.createElement('section');
        capSection.className = 'section card';
        capSection.style.borderLeft = '4px solid #F5D142'; // Golden for Capital
        capSection.style.background = 'rgba(245, 209, 66, 0.02)';

        capSection.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                <h2 class="section-title" style="margin-bottom: 0; color: #F5D142;">👁️ 자본 관점 (Capital Eye)</h2>
                <span class="badge" style="background: #F5D142; color: #000;">DETERMINISTIC</span>
            </div>
            
            <div style="font-size: 1.25rem; font-weight: 800; color: #fff; margin-bottom: 10px;">${capitalPerspective.headline}</div>
            <div style="font-size: 1rem; color: #94a3b8; font-style: italic; margin-bottom: 20px; border-left: 2px solid #F5D142; padding-left: 15px;">
                "${capitalPerspective.core_statement}"
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <h3 style="font-size: 0.9rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;">🔀 자금 이동 (Capital Flow)</h3>
                    ${capitalPerspective.capital_flow.map(f => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem;">• ${f}</div>`).join('')}
                </div>
                <div>
                    <h3 style="font-size: 0.9rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;">📉 내부 자본 이전 (Internal Shift)</h3>
                    ${capitalPerspective.internal_shift.map(s => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem;">• ${s}</div>`).join('')}
                </div>
            </div>

            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid var(--border); display: flex; gap: 20px; align-items: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;"><span style="color: #F5D142; font-weight: 800;">WHY NOW:</span> ${capitalPerspective.why_now_capital.join(' | ')}</div>
            </div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #ef4444; font-weight: 600;">⚠️ ${capitalPerspective.risk_note}</div>
        `;
        // Insert after main card (hero) or top-most items
        const operatorView = document.getElementById('operator-view');
        const hooks = document.getElementById('narrative-hook');
        if (hooks && hooks.nextSibling) {
            operatorView.insertBefore(capSection, hooks.nextSibling);
        } else {
            operatorView.prepend(capSection);
        }
    }

    // [IS-109-A] Render Policy → Capital Transmission Card
    if (policyCapital && policyCapital.headline) {
        const polSection = document.createElement('section');
        polSection.className = 'section card';
        polSection.style.borderLeft = '4px solid #3B82F6'; // Policy Blue
        polSection.style.background = 'rgba(59, 130, 246, 0.03)';

        polSection.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                <h2 class="section-title" style="margin-bottom: 0; color: #60A5FA;">🏛️ 정책→자금 전환 (Policy→Capital)</h2>
                <div style="display: flex; gap: 10px;">
                    <span class="badge" style="background: #3B82F6;">${policyCapital.signal_type}</span>
                    <span class="badge" style="background: #1E40AF;">${policyCapital.time_to_money}</span>
                </div>
            </div>
            
            <div style="font-size: 1.3rem; font-weight: 800; color: #fff; margin-bottom: 10px;">${policyCapital.headline}</div>
            <div style="font-size: 1rem; color: #94a3b8; border-left: 2px solid #3B82F6; padding-left: 15px; margin-bottom: 20px;">
                ${policyCapital.one_liner}
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <h3 style="font-size: 0.9rem; color: #60a5fa; text-transform: uppercase; margin-bottom: 10px;">⚙️ 전환 메커니즘</h3>
                    ${policyCapital.mechanism.map(m => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem;">• ${m}</div>`).join('')}
                </div>
                <div>
                    <h3 style="font-size: 0.9rem; color: #60a5fa; text-transform: uppercase; margin-bottom: 10px;">📊 수치 및 근거</h3>
                    ${policyCapital.numbers_with_evidence.map(n => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem;">• ${n}</div>`).join('')}
                </div>
            </div>

            <div style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <h3 style="font-size: 0.9rem; color: #fbbf24; margin-bottom: 15px;">💰 누가 먼저 돈을 받는가?</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div>
                        <div style="font-size: 0.75rem; color: #60a5fa; font-weight: 800;">⛏️ PICKAXE</div>
                        ${(policyCapital.who_gets_paid_first.PICKAXE || []).map(w => `<div style="font-size: 0.9rem; margin-top: 5px;">${w}</div>`).join('')}
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #f87171; font-weight: 800;">🚫 BOTTLENECK</div>
                        ${(policyCapital.who_gets_paid_first.BOTTLENECK || []).map(w => `<div style="font-size: 0.9rem; margin-top: 5px;">${w}</div>`).join('')}
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #fbbf24; font-weight: 800;">🛡️ HEDGE</div>
                        ${(policyCapital.who_gets_paid_first.HEDGE || []).map(w => `<div style="font-size: 0.9rem; margin-top: 5px;">${w}</div>`).join('')}
                    </div>
                </div>
            </div>

            <div style="margin-top: 15px; font-size: 0.8rem; color: #94a3b8;">
                <span style="color: #60a5fa; font-weight: 800;">PRICE FLOOR:</span> ${policyCapital.price_floor ? '✅ CONFIRMED' : '🔎 SEARCHING'}
                <span style="margin: 0 10px;">|</span>
                <span style="color: #60a5fa; font-weight: 800;">MONEY NATURE:</span> ${policyCapital.money_nature}
            </div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #fca5a5; font-style: italic;">🚨 ${policyCapital.risk_note}</div>
        `;

        const operatorView = document.getElementById('operator-view');
        const hooks = document.getElementById('narrative-hook');
        if (hooks && hooks.nextSibling) {
            operatorView.insertBefore(polSection, hooks.nextSibling);
        } else {
            operatorView.prepend(polSection);
        }
    }

    // [IS-109-B] Render Time-to-Money Card
    if (timeToMoney && timeToMoney.classification) {
        const timeSection = document.createElement('section');
        timeSection.className = 'section card-highlight';
        timeSection.style.background = 'linear-gradient(135deg, #064e3b 0%, #022c22 100%)'; // Emerald Green
        timeSection.style.border = '1px solid #059669';
        timeSection.style.boxShadow = '0 10px 30px rgba(16, 185, 129, 0.15)';

        const colorMap = {
            "IMMEDIATE": "#10B981", // Emerald
            "NEAR": "#34D399",
            "MID": "#FBBF24",
            "LONG": "#94A3B8"
        };
        const color = colorMap[timeToMoney.classification] || "#fff";

        timeSection.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                <h2 class="section-title" style="margin-bottom: 0; color: #10B981;">📅 돈이 찍히는 시간표 (Money Timeline)</h2>
                <div style="background: ${color}; color: #000; padding: 5px 15px; border-radius: 20px; font-weight: 900; font-size: 0.85rem;">
                    ${timeToMoney.classification} (${timeToMoney.time_window})
                </div>
            </div>
            
            <div style="font-size: 1.1rem; color: #ecfdf5; font-weight: 600; margin-bottom: 20px; border-left: 3px solid #10B981; padding-left: 15px;">
                "${timeToMoney.topic}"
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
                <div>
                    <h3 style="font-size: 0.9rem; color: #34d399; text-transform: uppercase; margin-bottom: 10px;">📉 시점 결정 사유 (Reasoning)</h3>
                    ${timeToMoney.reasoning.map(r => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem; color: #ecfdf5;">• ${r}</div>`).join('')}
                </div>
                <div>
                    <h3 style="font-size: 0.9rem; color: #f87171; text-transform: uppercase; margin-bottom: 10px;">🚧 주요 지연 리스크 (Blocked by)</h3>
                    ${timeToMoney.blocked_by.map(b => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem; color: #fca5a5;">⚠️ ${b}</div>`).join('')}
                </div>
            </div>

            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(16, 185, 129, 0.2);">
                <h3 style="font-size: 0.9rem; color: #10B981; margin-bottom: 10px;">🏃 먼저 반응하는 주체 (First Reactors)</h3>
                <div style="display: flex; gap: 15px;">
                    ${timeToMoney.first_reactors.map(f => `<div style="font-size: 0.9rem; color: #ecfdf5; background: rgba(16, 185, 129, 0.1); padding: 5px 12px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);">${f}</div>`).join('')}
                </div>
            </div>
        `;

        const operatorView = document.getElementById('operator-view');
        const hooks = document.getElementById('narrative-hook');
        if (hooks && hooks.nextSibling) {
            operatorView.insertBefore(timeSection, hooks.nextSibling);
        } else {
            operatorView.prepend(timeSection);
        }
    }

    // [IS-110] Render Expectation Gap Card
    if (expectationGap && expectationGap.headline) {
        const gapSection = document.createElement('section');
        gapSection.className = 'section card-highlight';
        gapSection.style.background = 'linear-gradient(135deg, #262626 0%, #0a0a0a 100%)'; // Darker background
        gapSection.style.border = '1px solid #404040';
        gapSection.style.boxShadow = '0 10px 30px rgba(0,0,0,0.4)';

        const gapColor = expectationGap.gap_type === 'POSITIVE' ? '#22C55E' : '#EF4444'; // Green for positive, Red for negative

        gapSection.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                <h2 class="section-title" style="margin-bottom: 0; color: #A3A3A3;">📉 시장 기대 vs 현실 괴리 (Market Gap)</h2>
                <div style="background: ${gapColor}; color: #fff; padding: 4px 12px; border-radius: 4px; font-weight: 800; font-size: 0.75rem; letter-spacing: 0.05em;">
                    ${expectationGap.gap_type}
                </div>
            </div>
            
            <div style="font-size: 1.3rem; font-weight: 800; color: #fff; margin-bottom: 10px;">${expectationGap.headline || ''}</div>
            <div style="font-size: 1rem; color: #A3A3A3; border-left: 2px solid ${gapColor}; padding-left: 15px; margin-bottom: 20px;">
                ${expectationGap.one_liner || ''}
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
                <div>
                    <h3 style="font-size: 0.9rem; color: #A3A3A3; text-transform: uppercase; margin-bottom: 10px;">📈 시장 기대</h3>
                    ${(expectationGap.market_expectation || []).map(e => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem;">• ${e}</div>`).join('')}
                </div>
                <div>
                    <h3 style="font-size: 0.9rem; color: #A3A3A3; text-transform: uppercase; margin-bottom: 10px;">📊 현실 데이터</h3>
                    ${(expectationGap.real_data || []).map(d => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem;">• ${d}</div>`).join('')}
                </div>
            </div>

            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #404040;">
                <h3 style="font-size: 0.9rem; color: #A3A3A3; margin-bottom: 10px;">💡 핵심 인사이트</h3>
                <div style="font-size: 0.95rem; color: #D4D4D4;">${expectationGap.insight || ''}</div>
            </div>
            <div style="margin-top: 15px; font-size: 0.8rem; color: #EF4444; font-style: italic;">🚨 리스크: ${expectationGap.risk_note || ''}</div>
        `;

        const operatorView = document.getElementById('operator-view');
        const heroSection = document.querySelector('.section.card'); // 대략적인 Hero 섹션 추정
        if (heroSection && heroSection.nextSibling) {
            operatorView.insertBefore(gapSection, heroSection.nextSibling);
        } else {
            operatorView.prepend(gapSection);
        }
    }

    // [IS-112] Render Valuation Reset Card
    if (valuationReset && valuationReset.valuation_state) {
        const valSection = document.createElement('section');
        valSection.className = 'section card-highlight';
        valSection.style.background = 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)';
        valSection.style.border = '1px solid #334155';
        valSection.style.boxShadow = '0 10px 30px rgba(0,0,0,0.3)';

        const stateColorMap = {
            "RESET": "#10B981",       // Emerald
            "OVERPRICED": "#ef4444",  // Red
            "EARLY": "#3B82F6",       // Blue
            "UNCONFIRMED": "#9ca3af"   // Gray
        };
        const color = stateColorMap[valuationReset.valuation_state] || "#fff";

        valSection.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                <h2 class="section-title" style="margin-bottom: 0; color: #94a3b8;">⚖️ 가치 재평가 분석 (Valuation Reset)</h2>
                <div style="background: ${color}; color: #fff; padding: 4px 12px; border-radius: 4px; font-weight: 800; font-size: 0.75rem; letter-spacing: 0.05em;">
                    ${valuationReset.valuation_state}
                </div>
            </div>

            <div style="font-size: 1.4rem; font-weight: 900; color: #fff; margin-bottom: 12px; line-height: 1.3;">
                "${valuationReset.one_liner}"
            </div>
            <div style="font-size: 1.1rem; color: #cbd5e1; font-weight: 600; margin-bottom: 25px; border-left: 3px solid ${color}; padding-left: 15px;">
                ${valuationReset.operator_judgement}
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 25px;">
                <div style="background: rgba(255,255,255,0.02); padding: 18px; border-radius: 8px; border: 1px solid rgba(148, 163, 184, 0.1);">
                    <h3 style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 15px; font-weight: 800;">🧠 판단 근거 (Core Reason)</h3>
                    ${valuationReset.core_reason.map(r => `<div style="font-size: 0.95rem; color: #e2e8f0; margin-bottom: 10px; line-height: 1.5;">• ${r}</div>`).join('')}
                </div>
                <div style="background: rgba(255,255,255,0.02); padding: 18px; border-radius: 8px; border: 1px solid rgba(148, 163, 184, 0.1);">
                    <h3 style="font-size: 0.8rem; color: #f43f5e; text-transform: uppercase; margin-bottom: 15px; font-weight: 800;">📊 수치 검증 (Numeric Checks)</h3>
                    ${valuationReset.numeric_checks.map(n => {
            const highlighted = n.replace(/([-+]?\d*\.?\d+(?:%|배)?)/g, '<span style="color:#fff; font-weight:800; border-bottom:1px solid #f43f5e;">$1</span>');
            return `<div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 10px;">• ${highlighted}</div>`;
        }).join('')}
                </div>
            </div>

            <div style="padding: 15px; background: rgba(0,0,0,0.2); border-radius: 8px; border-top: 2px solid ${color};">
                <div style="font-size: 0.85rem; color: #ef4444; font-weight: 700;">⚠️ 리스크 리포트: ${valuationReset.risk_note}</div>
            </div>
        `;

        const operatorView = document.getElementById('operator-view');
        // IS-110 아래, IS-111 위 배치
        const gapCard = Array.from(operatorView.querySelectorAll('.section.card-highlight')).find(c => c.innerHTML.includes('시장 기대 vs 현실 괴리'));
        if (gapCard && gapCard.nextSibling) {
            operatorView.insertBefore(valSection, gapCard.nextSibling);
        } else {
            operatorView.prepend(valSection);
        }
    }

    // [IS-111] Render Sector Rotation Acceleration Card
    if (sectorRotation && sectorRotation.acceleration) {
        const rotSection = document.createElement('section');
        rotSection.className = 'section card-highlight';
        rotSection.style.background = 'linear-gradient(135deg, #111827 0%, #1f2937 100%)';
        rotSection.style.border = '1px solid #374151';
        rotSection.style.boxShadow = '0 10px 30px rgba(0,0,0,0.3)';

        const accelColorMap = {
            "ACCELERATING": "#10B981", // Emerald
            "ROTATING": "#3B82F6",     // Blue
            "NONE": "#6B7280"          // Gray
        };
        const color = accelColorMap[sectorRotation.acceleration] || "#fff";

        rotSection.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                <h2 class="section-title" style="margin-bottom: 0; color: #9ca3af;">📈 섹터 자금 이동 가속 신호 (Rotation Accel)</h2>
                <div style="background: ${color}; color: #fff; padding: 4px 12px; border-radius: 4px; font-weight: 800; font-size: 0.75rem; letter-spacing: 0.05em;">
                    ${sectorRotation.acceleration}
                </div>
            </div>

            <div style="display: flex; align-items: center; justify-content: center; gap: 30px; margin-bottom: 30px; padding: 25px; background: rgba(0,0,0,0.2); border-radius: 12px;">
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #9ca3af; margin-bottom: 5px; font-weight: 800;">FROM (이탈)</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #f87171;">${sectorRotation.from_sector || ''}</div>
                </div>
                <div style="font-size: 2rem; color: ${color}; animation: pulse 2s infinite;">➔</div>
                <div style="text-align: center;">
                    <div style="font-size: 0.75rem; color: #9ca3af; margin-bottom: 5px; font-weight: 800;">TO (유입)</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #4ade80;">${sectorRotation.to_sector || ''}</div>
                </div>
            </div>
            
            <div style="font-size: 1.25rem; font-weight: 800; color: #fff; margin-bottom: 20px; text-align: center; line-height: 1.4;">
                "${sectorRotation.operator_sentence || ''}"
            </div>

            <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; border: 1px solid rgba(156, 163, 175, 0.1); margin-bottom: 20px;">
                <h3 style="font-size: 0.8rem; color: #9ca3af; text-transform: uppercase; margin-bottom: 12px; font-weight: 800;">🏛️ 가속 판정 근거 (Evidence)</h3>
                ${(sectorRotation.evidence || []).map(e => `<div style="font-size: 0.9rem; color: #d1d5db; margin-bottom: 8px;">• ${e}</div>`).join('')}
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem;">
                <div style="color: #6b7280;">신뢰도: <span style="color: ${color}; font-weight: 800;">${sectorRotation.confidence || ''}</span></div>
                <div style="color: #f87171; font-weight: 600;">⚠️ 리스크: ${sectorRotation.risk_note || ''}</div>
            </div>

            <style>
                @keyframes pulse {
                    0% { transform: translateX(0px); opacity: 0.5; }
                    50% { transform: translateX(10px); opacity: 1; }
                    100% { transform: translateX(0px); opacity: 0.5; }
                }
            </style>
        `;

        const operatorView = document.getElementById('operator-view');
        // Market Gap 카드 바로 아래 배치 (방금 추가한 gapSection을 찾아서 그 뒤에 삽입)
        const allCards = operatorView.querySelectorAll('.section.card-highlight');
        if (allCards.length > 0) {
            const gapCard = Array.from(allCards).find(c => c.innerHTML.includes('시장 기대 vs 현실 괴리'));
            if (gapCard && gapCard.nextSibling) {
                operatorView.insertBefore(rotSection, gapCard.nextSibling);
            } else if (gapCard) {
                operatorView.appendChild(rotSection);
            } else {
                operatorView.prepend(rotSection);
            }
        } else {
            operatorView.prepend(rotSection);
        }
    }

    // [IS-106] Render Relationship Stress Card (Relationship Break)
    if (relStressCard && relStressCard.headline) {
        const relSection = document.createElement('section');
        relSection.className = 'section card-highlight';
        relSection.style.background = 'linear-gradient(135deg, #450a0a 0%, #000 100%)';
        relSection.style.border = '1px solid #991b1b';
        relSection.style.boxShadow = '0 10px 30px rgba(153, 27, 27, 0.2)';

        relSection.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                <h2 class="section-title" style="margin-bottom: 0; color: #f87171;">💔 관계 균열 및 결별 리스크</h2>
                <span class="badge ${relStressCard.status.toLowerCase()}">${relStressCard.status}</span>
            </div>
            
            <div style="font-size: 1.5rem; font-weight: 800; color: #fff; margin-bottom: 10px;">${relStressCard.headline}</div>
            <div style="font-size: 1.1rem; color: #fca5a5; font-weight: 600; margin-bottom: 20px;">"${relStressCard.hook}"</div>

            <div style="display: flex; gap: 15px; margin-bottom: 20px; align-items: center; justify-content: center; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 1.2rem; font-weight: 800;">${relStressCard.pair.a_kr}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">${relStressCard.pair.a}</div>
                </div>
                <div style="font-size: 1.5rem; color: #f87171;">↔️</div>
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 1.2rem; font-weight: 800;">${relStressCard.pair.b_kr}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">${relStressCard.pair.b}</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
                <div>
                    <h3 style="font-size: 0.9rem; color: #ef4444; text-transform: uppercase; margin-bottom: 10px;">🔴 무엇이 달라졌나</h3>
                    ${relStressCard.what_changed.map(c => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem;">• ${c}</div>`).join('')}
                </div>
                <div>
                    <h3 style="font-size: 0.9rem; color: #f87171; text-transform: uppercase; margin-bottom: 10px;">🌊 파급 효과 (Cascade)</h3>
                    ${relStressCard.cascade.map((c, i) => `<div style="padding: 8px; margin-bottom: 5px; font-size: 0.9rem; border-left: 2px solid #ef4444; padding-left: 10px;">${i + 1}. ${c}</div>`).join('')}
                </div>
            </div>

            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 10px;"><span style="color: #ef4444; font-weight: 800;">데이터 근거:</span></div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    ${relStressCard.numbers_with_evidence.map(n => `<div style="font-size: 0.85rem; color: #cbd5e1; background: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 4px;">${n}</div>`).join('')}
                </div>
            </div>
            <div style="margin-top: 15px; font-size: 0.8rem; color: #fca5a5; font-style: italic;">🚨 리스크: ${relStressCard.risk_note}</div>
        `;

        // [IS-109-A] Render Policy → Capital Transmission Card
        if (policyCapital && policyCapital.headline) {
            const polSection = document.createElement('section');
            polSection.className = 'section card';
            polSection.style.borderLeft = '4px solid #3B82F6'; // Policy Blue
            polSection.style.background = 'rgba(59, 130, 246, 0.03)';

            polSection.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                <h2 class="section-title" style="margin-bottom: 0; color: #60A5FA;">🏛️ 정책→자금 전환 (Policy→Capital)</h2>
                <div style="display: flex; gap: 10px;">
                    <span class="badge" style="background: #3B82F6;">${policyCapital.signal_type}</span>
                    <span class="badge" style="background: #1E40AF;">${policyCapital.time_to_money}</span>
                </div>
            </div>
            
            <div style="font-size: 1.3rem; font-weight: 800; color: #fff; margin-bottom: 10px;">${policyCapital.headline}</div>
            <div style="font-size: 1rem; color: #94a3b8; border-left: 2px solid #3B82F6; padding-left: 15px; margin-bottom: 20px;">
                ${policyCapital.one_liner}
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <h3 style="font-size: 0.9rem; color: #60a5fa; text-transform: uppercase; margin-bottom: 10px;">⚙️ 전환 메커니즘</h3>
                    ${policyCapital.mechanism.map(m => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem;">• ${m}</div>`).join('')}
                </div>
                <div>
                    <h3 style="font-size: 0.9rem; color: #60a5fa; text-transform: uppercase; margin-bottom: 10px;">📊 수치 및 근거</h3>
                    ${policyCapital.numbers_with_evidence.map(n => `<div style="padding: 10px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 8px; font-size: 0.95rem;">• ${n}</div>`).join('')}
                </div>
            </div>

            <div style="margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <h3 style="font-size: 0.9rem; color: #fbbf24; margin-bottom: 15px;">💰 누가 먼저 돈을 받는가?</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div>
                        <div style="font-size: 0.75rem; color: #60a5fa; font-weight: 800;">⛏️ PICKAXE</div>
                        ${(policyCapital.who_gets_paid_first.PICKAXE || []).map(w => `<div style="font-size: 0.9rem; margin-top: 5px;">${w}</div>`).join('')}
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #f87171; font-weight: 800;">🚫 BOTTLENECK</div>
                        ${(policyCapital.who_gets_paid_first.BOTTLENECK || []).map(w => `<div style="font-size: 0.9rem; margin-top: 5px;">${w}</div>`).join('')}
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #fbbf24; font-weight: 800;">🛡️ HEDGE</div>
                        ${(policyCapital.who_gets_paid_first.HEDGE || []).map(w => `<div style="font-size: 0.9rem; margin-top: 5px;">${w}</div>`).join('')}
                    </div>
                </div>
            </div>

            <div style="margin-top: 15px; font-size: 0.8rem; color: #94a3b8;">
                <span style="color: #60a5fa; font-weight: 800;">PRICE FLOOR:</span> ${policyCapital.price_floor ? '✅ CONFIRMED' : '🔎 SEARCHING'}
                <span style="margin: 0 10px;">|</span>
                <span style="color: #60a5fa; font-weight: 800;">MONEY NATURE:</span> ${policyCapital.money_nature}
            </div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #fca5a5; font-style: italic;">🚨 ${policyCapital.risk_note}</div>
        `;

            const operatorView = document.getElementById('operator-view');
            const hooks = document.getElementById('narrative-hook');
            if (hooks && hooks.nextSibling) {
                operatorView.insertBefore(polSection, hooks.nextSibling);
            } else {
                operatorView.prepend(polSection);
            }
        }

        // [IS-106] Render Relationship Stress Card (Relationship Break)

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

                    <div style="font-weight: 800; margin-bottom: 10px;">📦 ${type}</div>
                    <div style="font-size: 1.1rem; font-weight: 800;">${p.title || 'No Title'}</div>
                    <div style="margin-top: 10px; font-size: 0.9rem; color: var(--text-secondary); white-space: pre-wrap;">${p.script_draft || p.hook || 'No content'}</div>
                </div >
            `;
            }).join('');
        }

        // [IS-103] Legacy link
        const legacyLink = document.createElement('div');
        legacyLink.style.textAlign = 'center';
        legacyLink.style.marginTop = '40px';
        legacyLink.style.padding = '20px';
        legacyLink.style.borderTop = '1px solid var(--border)';
        legacyLink.innerHTML = `< a href = "../index.html" style = "color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 600;" >📍 레거시 메인(구버전) 바로가기</a > `;
        document.getElementById('app').appendChild(legacyLink);
    });
