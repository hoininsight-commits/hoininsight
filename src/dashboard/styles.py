
class DashboardStyles:
    """Design System for HOIN Insight (Premium Dark Theme)"""
    
    PRIMARY_BG = "#0f172a"
    SECONDARY_BG = "#f8fafc"
    PANEL_BG = "#1e293b"
    ACCENT_BLUE = "#3b82f6"
    ACCENT_PURPLE = "#7c3aed"
    TEXT_PRIMARY = "#1e293b"
    TEXT_MUTED = "#64748b"
    BORDER_COLOR = "#e2e8f0"

    COMMON_CSS = """
    body { font-family: 'Pretendard', 'Inter', system-ui, sans-serif; background: #f4f7fa; color: #1e293b; margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; }
    
    .top-bar { background: white; border-bottom: 1px solid #e2e8f0; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; height: 60px; box-sizing: border-box; }
    h1 { margin: 0; font-size: 18px; font-weight: 700; color: #334155; }
    
    .status-badge { padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; background: #e2e8f0; }
    .status-SUCCESS { background: #dcfce7; color: #166534; }
    .status-PARTIAL { background: #fef9c3; color: #854d0e; }
    .status-FAIL { background: #fee2e2; color: #991b1b; }
    
    .dashboard-container { display: grid; grid-template-columns: 260px 1fr; height: calc(100vh - 60px); overflow: hidden; }
    
    .nav-panel { 
        background: #0f172a; 
        color: #94a3b8; 
        display: flex; 
        flex-direction: column; 
        gap: 5px; 
        padding-top: 20px;
        overflow-y: auto;
    }
    
    .nav-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: #475569;
        margin: 20px 0 10px 25px;
        letter-spacing: 0.05em;
    }

    .nav-item { 
        padding: 12px 25px; 
        font-size: 14px; 
        font-weight: 500; 
        cursor: pointer; 
        text-decoration: none; 
        display: flex; 
        align-items: center; 
        gap: 12px; 
        color: #94a3b8;
        border-left: 3px solid transparent;
        transition: all 0.2s; 
    }
    .nav-item:hover { 
        background: #1e293b; 
        color: #f1f5f9; 
    }
    .nav-item.active { 
        background: #1e293b; 
        color: #3b82f6; 
        border-left-color: #3b82f6;
        font-weight: 600;
    }
    
    .main-panel { padding: 40px; overflow-y: auto; background: #f8fafc; display: flex; flex-direction: column; align-items: center; gap: 20px; scroll-behavior: smooth; }
    .sections-wrapper { max-width: 900px; width: 100%; display: flex; flex-direction: column; gap: 60px; padding-bottom: 100px; }
    
    /* Topic Card Premium Styles */
    .topic-card-top1 {
        background: white; border: 1px solid #e2e8f0; border-left: 4px solid #7c3aed;
        border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 30px; position: relative;
    }
    .top1-title { font-size: 24px; font-weight: 800; color: #1e293b; line-height: 1.3; }
    
    .badge-whynow { font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 4px; }
    .badge-whynow-escalated { background: #fee2e2; color: #991b1b; }
    .badge-whynow-smartmoney { background: #dcfce7; color: #166534; }
    .badge-whynow-default { background: #f3e8ff; color: #6b21a8; }
    
    .sidebar { background: white; border-left: 1px solid #e2e8f0; padding: 30px; overflow-y: auto; }
    """
