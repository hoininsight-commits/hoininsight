import os
import argparse
from pathlib import Path

class KoreanCompletionReportGenerator:
    """
    [IS-107-1] Korean-Only Completion Report Generator
    Generates deterministic reports using a Markdown template.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.template_path = base_dir / "docs" / "engine" / "templates" / "REMOTE_VERIFICATION_REPORT_KO_TEMPLATE.md"

    def generate(self, data: dict, output_path: Path):
        if not self.template_path.exists():
            print(f"Error: Template not found at {self.template_path}")
            return

        template_content = self.template_path.read_text(encoding='utf-8')
        
        # Simple string replacement
        report = template_content
        for key, value in data.items():
            placeholder = "{{" + key + "}}"
            if isinstance(value, list):
                formatted_value = "\n".join([f"- {item}" for item in value])
                report = report.replace(placeholder, formatted_value)
            else:
                report = report.replace(placeholder, str(value))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        print(f"Report generated: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate Korean Completion Report")
    parser.add_argument("--layer_id", required=True)
    parser.add_argument("--task_name", required=True)
    parser.add_argument("--task_purpose", required=True)
    parser.add_argument("--added_files", nargs="*", default=[])
    parser.add_argument("--modified_files", nargs="*", default=[])
    parser.add_argument("--outputs", nargs="*", default=[])
    parser.add_argument("--test_command", required=True)
    parser.add_argument("--commit_hash", required=True)
    parser.add_argument("--impact_1", required=True)
    parser.add_argument("--impact_2", required=True)
    parser.add_argument("--impact_3", required=True)
    parser.add_argument("--output_file", required=True)

    args = parser.parse_args()

    data = {
        "layer_id": args.layer_id,
        "task_name": args.task_name,
        "task_purpose": args.task_purpose,
        "added_files": args.added_files,
        "modified_files": args.modified_files,
        "outputs": args.outputs,
        "test_command": args.test_command,
        "commit_hash": args.commit_hash,
        "impact_1": args.impact_1,
        "impact_2": args.impact_2,
        "impact_3": args.impact_3
    }

    generator = KoreanCompletionReportGenerator(Path("."))
    generator.generate(data, Path(args.output_file))

if __name__ == "__main__":
    main()
