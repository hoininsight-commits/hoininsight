document.addEventListener('DOMContentLoaded', async () => {
    const DATA_PATH = '../data/decision/'; // Assuming UI is in /ui/ and data in /data/decision/
    const MOCK_FALLBACK = true;

    async function loadJson(file) {
        try {
            const res = await fetch(DATA_PATH + file);
            if (!res.ok) throw new Error(`Not found: ${file}`);
            return await res.json();
        } catch (e) {
            console.warn(`[DATA] Failed to load ${file}, using fallback or empty.`);
            return null;
        }
    }

    // 1. Load All Data
    const [units, decision, skeleton, mentionables, evidence, packs] = await Promise.all([
        loadJson('interpretation_units.json'),
        loadJson('speakability_decision.json'),
        loadJson('narrative_skeleton.json'),
        loadJson('mentionables.json'),
        loadJson('evidence_citations.json'),
        loadJson('content_pack.json')
    ]);

    if (!units || units.length === 0) {
        document.getElementById('issue-hook').innerText = "오늘의 분석 결과가 없습니다.";
        return;
    }

    // Pick Top-1 Unit (First one in JSON)
    const topUnit = units[0];
    const unitId = topUnit.interpretation_id;
    const unitDecision = decision ? decision[unitId] : { speakability_flag: 'HOLD', speakability_reasons: ['No decision data'] };
    const unitSkeleton = skeleton ? skeleton[unitId] : null;

    // 2. Render Header & Global Status
    document.getElementById('current-date').innerText = topUnit.as_of_date || new Date().toISOString().split('T')[0];
    const globalStatus = document.getElementById('global-status-badge');
    const flag = unitDecision.speakability_flag;
    const mode = topUnit.mode || 'STRUCTURAL';

    if (mode === 'HYPOTHESIS_JUMP') {
        globalStatus.innerText = '🟡 HYPOTHESIS';
        globalStatus.className = 'badge hypothesis';
    } else {
        globalStatus.innerText = flag === 'READY' ? '🟢 READY' : '🔴 HOLD';
        globalStatus.className = `badge ${flag.toLowerCase()}`;
    }

    // 3. Render Core Issue (Skeleton-based)
    if (unitSkeleton) {
        document.getElementById('issue-hook').innerText = unitSkeleton.hook;
        document.getElementById('issue-why-now').innerText = `[왜 지금인가] ${topUnit.why_now_type || '구조적 변곡점 포착'}: ${topUnit.structural_narrative}`;
    }

    // 4. Render Speakability & Guide
    const speakBadge = document.getElementById('speakability-badge');
    speakBadge.innerText = flag;
    speakBadge.className = `badge ${flag.toLowerCase()}`;

    const guideBox = document.getElementById('operator-guide');
    let guideText = "";
    if (mode === 'HYPOTHESIS_JUMP') {
        guideText = "⚠️ 가설 모드: 확정적으로 말하지 말고 '가능성'과 '데이터 추적' 프레임으로 설명하세요.";
    } else if (flag === 'READY') {
        guideText = "✅ 바로 제작 가능: 강력한 근거가 확보되었습니다. 자신 있게 전달하세요.";
    } else {
        guideText = `⏸️ 대기(HOLD): ${unitDecision.speakability_reasons.join(', ')}`;
    }
    guideBox.innerHTML = `<p>${guideText}</p>`;

    // 5. Render Logic Chain
    const logicFlow = document.getElementById('logic-steps');
    if (mode === 'HYPOTHESIS_JUMP' && topUnit.reasoning_chain) {
        const rc = topUnit.reasoning_chain;
        const steps = [
            { label: '트리거', value: rc.trigger_event },
            { label: '메커니즘', value: rc.mechanism },
            { label: '수혜/영향', value: rc.beneficiaries.join(', ') }
        ];
        logicFlow.innerHTML = steps.map(s => `
            <div class="logic-item">
                <span class="tag-badge">${s.label}</span>
                <span>${s.value}</span>
            </div>
        `).join('');
    } else if (unitSkeleton && unitSkeleton.evidence_3) {
        logicFlow.innerHTML = unitSkeleton.evidence_3.map(ev => `
            <div class="logic-item">
                <span>${ev}</span>
            </div>
        `).join('');
    }

    // 6. Render Mentionables
    const mentionGrid = document.getElementById('mention-cards');
    if (mentionables && mentionables[unitId]) {
        const items = mentionables[unitId].mentionable_items || [];
        mentionGrid.innerHTML = items.map(m => `
            <div class="mention-card">
                <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 4px;">${m.name}</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary);">${m.reason_to_mention}</div>
            </div>
        `).join('');
    }

    // 7. Render Content Packs
    const packContainer = document.getElementById('pack-container');
    if (packs && packs.packs) {
        packContainer.innerHTML = packs.packs.map(p => `
            <div class="pack-card">
                <div>
                    <span class="tag-badge">${p.format}</span>
                    <span style="font-weight: bold;">${p.title}</span>
                </div>
                <div style="font-size: 0.85rem; color: var(--accent-blue);">내용 포함됨 &gt;</div>
            </div>
        `).join('');
    }

    // 8. Render Evidence
    const evidenceGrid = document.getElementById('evidence-list');
    if (evidence && evidence[unitId]) {
        const refs = evidence[unitId].citations || [];
        evidenceGrid.innerHTML = refs.map(r => `
            <div class="mention-card" style="font-size: 0.85rem;">
                <div style="color: var(--status-ready); font-weight: bold; margin-bottom: 4px;">${r.source_name}</div>
                <div>${r.content_snippet.substring(0, 50)}...</div>
            </div>
        `).join('');
    }

    // 9. Render Checklist
    const checklistUl = document.getElementById('checklist-items');
    if (unitSkeleton && unitSkeleton.checklist_3) {
        checklistUl.innerHTML = unitSkeleton.checklist_3.map(c => `
            <li style="margin-left: 20px; margin-bottom: 8px;">${c}</li>
        `).join('');
    }
});
