from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml

from src.registry.loader import load_datasets

@dataclass
class SchemaCheckResult:
    ok: bool
    lines: list[str]

def _load_schema(base_dir: Path, schema_version: str) -> Dict:
    schema_file = base_dir / "registry" / "schemas" / f"{schema_version}.yml"
    if not schema_file.exists():
        raise FileNotFoundError(f"schema file not found: {schema_file.as_posix()}")
    return yaml.safe_load(schema_file.read_text(encoding="utf-8"))

def _missing_cols(df_cols: List[str], required: List[str]) -> List[str]:
    s = set(df_cols)
    return [c for c in required if c not in s]

def run_schema_checks(base_dir: Path) -> SchemaCheckResult:
    reg = base_dir / "registry" / "datasets.yml"
    datasets = [ds for ds in load_datasets(reg) if ds.enabled]

    ok = True
    lines: list[str] = []
    for ds in datasets:
        schema = _load_schema(base_dir, ds.schema_version)
        required = schema.get("required_columns", [])
        curated = base_dir / ds.curated_path

        if not curated.exists():
            ok = False
            lines.append(f"[MISS] curated({ds.dataset_id}): {curated.as_posix()}")
            continue

        df = pd.read_csv(curated)
        miss = _missing_cols(list(df.columns), list(required))
        if miss:
            ok = False
            lines.append(f"[FAIL] schema({ds.dataset_id}): missing={miss}")
        else:
            lines.append(f"[OK] schema({ds.dataset_id}): {ds.schema_version}")

    return SchemaCheckResult(ok=ok, lines=lines)
