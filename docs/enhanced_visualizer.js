/**
 * Project HOIN - Enhanced Visualizer for Radar View
 * Provides institutional-grade visualization effects for anticipatory signals.
 */

// Override or Enhance the chart rendering for Radar Mode
const originalRenderChart = window.renderChart;

window.renderChart = function(data) {
    if (window.currentMode !== 'radar') {
        return originalRenderChart(data);
    }
    
    console.log("📡 [Visualizer] Rendering Radar View with Highlights...");
    const traces = [];
    
    Object.keys(data).forEach(themeName => {
        const theme = data[themeName];
        const points = theme.points;
        const metrics = theme.metrics;
        const isSelected = !window.highlightedTheme || themeName === window.highlightedTheme;
        
        // 1. 선점 신호 색상 및 애니메이션 설정
        const traceColor = metrics.is_anticipation ? '#3b82f6' : null;
        const opacity = isSelected ? 1.0 : 0.15;
        
        // 2. 가속도에 따른 꼬리 폭 가변 설정
        const baseWidth = isSelected ? 3 : 1;
        const accelBonus = metrics.acceleration > 0 ? Math.min(metrics.acceleration * 2, 5) : 0;
        
        traces.push({
            x: points.map(p => p.rs_ratio),
            y: points.map(p => p.rs_momentum),
            mode: 'lines+markers',
            name: themeName,
            opacity: opacity,
            line: { 
                shape: 'spline', 
                width: baseWidth + accelBonus,
                color: traceColor
            },
            marker: {
                size: points.map((p, i) => {
                    const isLast = i === points.length - 1;
                    if (isLast) {
                        return metrics.is_anticipation ? 18 : 14;
                    }
                    return 4;
                }),
                symbol: metrics.is_anticipation ? 'diamond' : 'circle',
                line: {
                    width: metrics.is_anticipation ? 2 : 0,
                    color: '#ffffff'
                },
                // Improving 하이라이트: 가시성을 높이기 위한 설정
                opacity: opacity
            },
            text: points.map(p => {
                let note = themeName;
                if (metrics.is_anticipation) note += " 🚀 [ANTICIPATION SIGNAL]";
                return `${note}<br>${p.date}<br>Ratio: ${p.rs_ratio.toFixed(2)}<br>Mom: ${p.rs_momentum.toFixed(2)}<br>Accel: ${metrics.acceleration.toFixed(2)}`;
            }),
            hoverinfo: 'text'
        });
    });

    const layout = {
        hovermode: 'closest',
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#888899', family: 'Outfit' },
        xaxis: { 
            title: 'RS-Ratio (Strength)', range: [85, 115],
            gridcolor: '#222233', zeroline: false, tickfont: { size: 10 }
        },
        yaxis: { 
            title: 'RS-Momentum (Momentum)', range: [85, 115],
            gridcolor: '#222233', zeroline: false, tickfont: { size: 10 }
        },
        // Radar 전용 십자선 가이드
        shapes: [
            { type: 'line', x0: 100, y0: 80, x1: 100, y1: 120, line: { color: 'rgba(255,255,255,0.1)', width: 1 } },
            { type: 'line', x0: 80, y0: 100, x1: 120, y1: 100, line: { color: 'rgba(255,255,255,0.1)', width: 1 } },
            // Improving 1시 방향 화살표 (선점 가이드)
            { 
                type: 'line', x0: 90, y0: 105, x1: 98, y1: 115, 
                line: { color: 'rgba(59, 130, 246, 0.2)', width: 4, dash: 'dot' } 
            }
        ],
        annotations: [
            { x: 112, y: 112, text: 'LEADING', showarrow: false, font: { size: 12, color: '#22c55e', opacity: 0.2 } },
            { x: 112, y: 88, text: 'WEAKENING', showarrow: false, font: { size: 12, color: '#eab308', opacity: 0.2 } },
            { x: 88, y: 88, text: 'LAGGING', showarrow: false, font: { size: 12, color: '#ef4444', opacity: 0.2 } },
            { x: 88, y: 112, text: 'IMPROVING', showarrow: false, font: { size: 12, color: '#3b82f6', opacity: 0.2 } }
        ],
        margin: { l: 50, r: 30, b: 50, t: 30 },
        showlegend: false
    };

    Plotly.newPlot('rrg-chart', traces, layout, {responsive: true});
};
