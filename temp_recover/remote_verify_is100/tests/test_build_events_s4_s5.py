from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock
from src.pipeline.build_events import EventBuilder, GateEvent

@pytest.fixture
def builder():
    return EventBuilder("2026-01-24")

def test_s4_contract_dropped_without_evidence(builder):
    """S4 event with no evidence (no amount, duration, or scope) should be dropped."""
    url = "https://example.com/contract-news-empty"
    # Content has 'contract' keyword but no numbers or durations
    mock_content = "<html><body><h1>Big Contract Signed</h1><p>We signed a deal.</p></body></html>"
    
    with patch("src.pipeline.build_events.URLExtractor.fetch_content", return_value=mock_content):
        events = builder.build_from_urls([url])
        assert len(events) == 0

def test_s4_contract_passed_with_evidence(builder):
    """S4 event with evidence (amount or duration) should be kept."""
    url = "https://example.com/contract-news-valid"
    # Content has 'contract' keyword and a duration '24 months'
    mock_content = "<html><body><h1>24 months contract</h1><p>Value is not mentioned.</p></body></html>"
    
    with patch("src.pipeline.build_events.URLExtractor.fetch_content", return_value=mock_content):
        events = builder.build_from_urls([url])
        assert len(events) == 1
        assert events[0].event_type == "contract"
        assert any(ev.label == "Duration" for ev in events[0].evidence)

def test_s5_capital_dropped_without_evidence(builder):
    """S5 event with no evidence (no value, payment, or dilution) should be dropped."""
    url = "https://example.com/capital-news-empty"
    # Content has 'acquisition' keyword but no specific details
    mock_content = "<html><body><h1>Acquisition announced</h1><p>Something happened.</p></body></html>"
    
    with patch("src.pipeline.build_events.URLExtractor.fetch_content", return_value=mock_content):
        events = builder.build_from_urls([url])
        assert len(events) == 0

def test_s5_capital_passed_with_evidence(builder):
    """S5 event with evidence (e.g., 'cash' or '$') should be kept."""
    url = "https://example.com/capital-news-valid"
    # Content has 'acquisition' and 'cash'
    mock_content = "<html><body><h1>Acquisition for cash</h1><p>The deal is $500M.</p></body></html>"
    
    with patch("src.pipeline.build_events.URLExtractor.fetch_content", return_value=mock_content):
        events = builder.build_from_urls([url])
        assert len(events) == 1
        assert events[0].event_type == "capital"
        assert any(ev.unit == "USD" or "Cash" in str(ev.value) for ev in events[0].evidence)
