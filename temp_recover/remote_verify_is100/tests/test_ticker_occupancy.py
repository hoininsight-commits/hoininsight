import pytest
from pathlib import Path
from src.ops.ticker_occupancy_layer import TickerOccupancyLayer

def test_ticker_occupancy_basic():
    layer = TickerOccupancyLayer(Path("."))
    candidates = ["TSM", "ASML", "AAPL", "MSFT"]
    context = {"topic": "Foundry Bottleneck"}
    
    results = layer.select_tickers(candidates, context)
    
    # Check truncation (max 3)
    assert len(results) <= 3
    
    # Check filtering (AAPL and MSFT should be lower or filtered or last)
    tickers = [r["ticker"] for r in results]
    assert "TSM" in tickers
    assert "ASML" in tickers
    assert "MSFT" not in tickers # Should be filtered by 50% Rule (0.35)

def test_ticker_occupancy_leader_exception():
    layer = TickerOccupancyLayer(Path("."))
    candidates = ["Samsung", "GOOGL"]
    context = {"topic": "Memory Market"}
    
    results = layer.select_tickers(candidates, context)
    
    tickers = [r["ticker"] for r in results]
    assert "Samsung" in tickers # Exception rule
    assert "GOOGL" not in tickers # Filtered (0.30)

def test_ticker_occupancy_sorting():
    layer = TickerOccupancyLayer(Path("."))
    # MU (1.0 manu), ASML (0.95 manu), TSM (1.0 manu)
    # MU and TSM score 1.5, ASML scores 1.45
    candidates = ["ASML", "MU", "TSM"]
    results = layer.select_tickers(candidates, {})
    
    # TSM > MU (Alphabetical if scores tie) - Wait, results sorted reverse=True
    # Scores: MU 1.5, TSM 1.5, ASML 1.45
    # TSM vs MU: TSM (T) vs MU (M) -> TSM first in reverse alphabetical if tie?
    # Actually sort(key=lambda x: (x["priority_score"], x["ticker"]), reverse=True)
    # (1.5, "TSM") > (1.5, "MU")
    assert results[0]["ticker"] == "TSM"
    assert results[1]["ticker"] == "MU"
    assert results[2]["ticker"] == "ASML"
