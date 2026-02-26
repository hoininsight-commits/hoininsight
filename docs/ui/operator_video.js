/**
 * operator_video.js
 * Renders the Video Intelligence Candidate Pool for the Operator UI.
 */

async function initVideoView() {
    const container = document.getElementById('operator-view');
    if (!container) return;

    // Set Loading State
    container.innerHTML = `
        <section class="section">
            <h2 class="section-title">🎬 영상 후보 (Video Candidates)</h2>
            <div id="video-pool-list" class="card-grid">
                <div class="card" style="text-align: center; padding: 50px;">
                    <p>영상 제작 후보군 데이터를 불러오는 중...</p>
                </div>
            </div>
        </section>
    `;

    try {
        const paths = [
            '/hoininsight/data/ops/video_candidate_pool.json',
            '../data/ops/video_candidate_pool.json'
        ];

        let data = null;
        for (const path of paths) {
            try {
                const res = await fetch(path);
                if (res.ok) {
                    data = await res.json();
                    break;
                }
            } catch (e) { }
        }

        if (!data || !data.top_candidates || data.top_candidates.length === 0) {
            renderEmptyVideoState(container);
            return;
        }

        renderVideoCandidates(container, data.top_candidates);
    } catch (err) {
        console.error('[VideoView] Error:', err);
        container.innerHTML += `<p style="color: red; padding: 20px;">데이터 로드 실패: ${err.message}</p>`;
    }
}

function renderEmptyVideoState(container) {
    const list = document.getElementById('video-pool-list');
    if (list) {
        list.innerHTML = `
            <div class="card" style="text-align: center; padding: 50px; grid-column: 1 / -1;">
                <h3 style="color: #64748b;">현재 선별된 영상 후보가 없습니다.</h3>
                <p style="font-size: 0.9rem; color: #94a3b8; margin-top: 10px;">
                    NS 점수 및 구조적 조건(Axis, Trigger)을 충족하는 토픽이 발견되면 이곳에 표시됩니다.
                </p>
            </div>
        `;
    }
}

function renderVideoCandidates(container, candidates) {
    const list = document.getElementById('video-pool-list');
    if (!list) return;

    // Sort by video_score desc (already sorted by engine, but for safety)
    candidates.sort((a, b) => (b.video_score || 0) - (a.video_score || 0));

    // Show only top 3
    const top3 = candidates.slice(0, 3);

    list.innerHTML = '';
    top3.forEach((c, idx) => {
        const card = document.createElement('div');
        card.className = 'card video-candidate-card';
        card.style.position = 'relative';
        card.style.borderLeft = idx === 0 ? '6px solid #f59e0b' : '1px solid #e2e8f0';

        const ns = c.narrative_score != null ? c.narrative_score : 'N/A';
        const vs = c.video_score != null ? c.video_score : 'N/A';
        const intensity = c.intensity != null ? `${c.intensity}%` : 'N/A';
        const conflict = c.conflict_flag ? '⚠️ CONFLICT' : '';

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <span class="badge" style="background: #fff7ed; color: #c2410c; font-weight: 800; border: 1px solid #ffedd5;">
                    RANK ${idx + 1}
                </span>
                <span style="font-size: 0.75rem; color: #ef4444; font-weight: 800;">${conflict}</span>
            </div>
            <h3 style="font-size: 1.1rem; font-weight: 800; color: #1e293b; margin-bottom: 15px; line-height: 1.4;">${c.title || 'Untitled'}</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                <div style="background: #f8fafc; padding: 10px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 0.7rem; color: #64748b; margin-bottom: 4px;">VIDEO SCORE</div>
                    <div style="font-size: 1.2rem; font-weight: 900; color: #f59e0b;">${vs}</div>
                </div>
                <div style="background: #f8fafc; padding: 10px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 0.7rem; color: #64748b; margin-bottom: 4px;">NARRATIVE (NS)</div>
                    <div style="font-size: 1.2rem; font-weight: 900; color: #3b82f6;">${ns}</div>
                </div>
            </div>

            <div style="font-size: 0.85rem; color: #475569; margin-bottom: 15px;">
                <div style="margin-bottom: 5px;"><strong>Intensity:</strong> ${intensity}</div>
                <div style="margin-bottom: 5px;"><strong>Trigger:</strong> ${c.why_now_type || 'N/A'}</div>
                <div><strong>Axes:</strong> ${(c.structural_axes || []).join(', ') || 'N/A'}</div>
            </div>

            <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                <span class="badge-mini" style="background: #f1f5f9; color: #475569; font-size: 0.7rem;">ID: ${c.dataset_id || 'unknown'}</span>
            </div>
        `;
        list.appendChild(card);
    });
}
