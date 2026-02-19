
import subprocess
import json
import os
from pathlib import Path
import re

def run_tests_and_summarize():
    print("Running pytest...")
    
    # Run pytest and capture output
    # -v: verbose
    # --tb=short: shorter traceback
    result = subprocess.run(
        ["python3", "-m", "pytest", "-v", "--tb=short"], 
        capture_output=True, 
        text=True
    )
    
    stdout = result.stdout
    stderr = result.stderr
    exit_code = result.returncode
    
    # Parse output for summary stats
    # Example line: "== 15 passed, 1 skipped in 0.5s =="
    summary_line_match = re.search(r"=+\s+(.*?)\s+=+", stdout.splitlines()[-1] if stdout else "")
    
    passed = 0
    failed = 0
    skipped = 0
    
    if summary_line_match:
        summary_text = summary_line_match.group(1)
        # Parse numbers
        p_match = re.search(r"(\d+) passed", summary_text)
        if p_match: passed = int(p_match.group(1))
        
        f_match = re.search(r"(\d+) failed", summary_text)
        if f_match: failed = int(f_match.group(1))
        
        s_match = re.search(r"(\d+) skipped", summary_text)
        if s_match: skipped = int(s_match.group(1))
    
    # Tail for debugging (max 200 lines)
    raw_output = stdout + "\n" + stderr
    raw_tail = "\n".join(raw_output.splitlines()[-200:])
    
    summary_data = {
        "total_passed": passed,
        "total_failed": failed,
        "total_skipped": skipped,
        "exit_code": exit_code,
        "raw_tail": raw_tail
    }
    
    output_dir = Path("data_outputs/ops")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON Output
    json_path = output_dir / "test_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
        
    # Markdown Output
    md_path = output_dir / "test_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Pytest Execution Summary\n\n")
        f.write(f"- **Exit Code**: {exit_code}\n")
        f.write(f"- **Passed**: {passed}\n")
        f.write(f"- **Failed**: {failed}\n")
        f.write(f"- **Skipped**: {skipped}\n\n")
        
        if failed > 0:
            f.write("## ❌ Failures Detected\n")
            f.write("Please check `raw_tail` in JSON or console output.\n")
        elif passed > 0:
            f.write("## ✅ Success\n")
            
        f.write("\n## Output Tail\n")
        f.write("```\n")
        f.write(raw_tail)
        f.write("\n```\n")
        
    print(f"Test summary generated at {json_path}")
    print(f"Passed: {passed}, Failed: {failed}")

if __name__ == "__main__":
    run_tests_and_summarize()
