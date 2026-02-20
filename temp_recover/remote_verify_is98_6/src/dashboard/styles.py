
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
    body { font-family: 'Pretendard', 'Inter', system-ui, sans-serif; background: #f4f7fa; color: #1e293b; margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
    
    .top-bar { 
        background: #0f172a; 
        color: white; 
        padding: 0 40px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        height: 64px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        z-index: 100;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .top-bar h1 { margin: 0; font-size: 20px; font-weight: 800; display: flex; align-items: center; gap: 12px; }
    .top-bar .engine-badge { background: #3b82f6; color: white; padding: 4px 10px; border-radius: 6px; font-size: 11px; letter-spacing: 0.05em; }
    
    .app-container { display: flex; flex: 1; height: calc(100vh - 64px); overflow: hidden; }
    
    .nav-panel { 
        width: 280px;
        background: #0f172a; 
        color: #94a3b8; 
        display: flex; 
        flex-direction: column; 
        padding: 20px 0;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    .nav-label {
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        color: #475569;
        margin: 25px 30px 12px 30px;
        letter-spacing: 0.08em;
    }

    .nav-item { 
        padding: 14px 30px; 
        font-size: 14px; 
        font-weight: 600; 
        cursor: pointer; 
        text-decoration: none; 
        display: flex; 
        align-items: center; 
        gap: 12px; 
        color: #94a3b8;
        border-left: 4px solid transparent;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); 
    }
    .nav-item:hover { 
        background: rgba(255,255,255,0.03); 
        color: #f1f5f9; 
    }
    .nav-item.active { 
        background: rgba(59, 130, 246, 0.1); 
        color: #3b82f6; 
        border-left-color: #3b82f6;
    }
    
    .main-panel { 
        flex: 1; 
        padding: 40px; 
        overflow-y: auto; 
        background: #f8fafc; 
        scroll-behavior: smooth; 
        position: relative;
    }
    .content-max-width { 
        max-width: 1000px; 
        margin: 0 auto; 
        display: flex; 
        flex-direction: column; 
        gap: 40px; 
        padding-bottom: 120px; 
    }
    
    .data-intake-panel {
        width: 360px;
        background: white;
        border-left: 1px solid #e2e8f0;
        padding: 30px;
        overflow-y: auto;
    }

    /* Modal */
    .modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(4px); display: none; align-items: center; justify-content: center; z-index: 1000; }
    .modal.active { display: flex; }
    .modal-content { background: white; width: 90%; max-width: 800px; max-height: 90vh; border-radius: 20px; overflow-y: auto; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); }
    
    .tab-content { display: none; width: 100%; }
    .tab-content.active { display: block !important; }
    .hidden { display: none !important; }
    """
