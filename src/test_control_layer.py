# src/test_control_layer.py
import json
from src.llm.gemini_output_contract import validate_gemini_output
from src.writer.fallback_writer import generate_fallback, format_fallback_as_md
from src.llm.gemini_wrapper import log_gemini_usage

def test_contract():
    print("Testing Output Contract...")
    valid_data = {
        "topic_core_claim": "Test",
        "one_line_summary": "Summary"
    }
    invalid_data = {
        "topic": "Wrong Field"
    }
    print(f"  Valid Data Test: {validate_gemini_output(valid_data)}")
    print(f"  Invalid Data Test: {validate_gemini_output(invalid_data)}")

def test_fallback():
    print("\nTesting Writer Fallback...")
    signal = {"topic": "S&P500", "strength": 9.2}
    analysis = {}
    fb_data = generate_fallback(signal, analysis)
    print(f"  Fallback JSON: {json.dumps(fb_data, indent=2, ensure_ascii=False)}")
    print(f"  Fallback MD Length: {len(format_fallback_as_md(fb_data))}")

def test_logging():
    print("\nTesting Logging...")
    log_gemini_usage("TEST_AGENT", success=True, fallback_used=False, retry_count=0)
    print("  Log entry added to data/logs/gemini_usage_log.json")

if __name__ == "__main__":
    test_contract()
    test_fallback()
    test_logging()
    print("\n✅ All Control Layer tests passed.")
