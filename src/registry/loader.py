from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List
import yaml
import importlib

@dataclass
class DatasetConfig:
    dataset_id: str
    enabled: bool
    soft_fail: bool
    entity: str
    unit: str
    source: str
    metric_name: str
    schema_version: str
    collector: str
    normalizer: str
    anomaly: str
    topic: str
    report_key: str
    curated_path: str

def load_datasets(path: Path) -> List[DatasetConfig]:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    out: List[DatasetConfig] = []
    for ds in cfg.get("datasets", []):
        out.append(
            DatasetConfig(
                dataset_id=ds["dataset_id"],
                enabled=bool(ds.get("enabled", True)),
                soft_fail=bool(ds.get("soft_fail", False)),
                entity=ds["entity"],
                unit=ds["unit"],
                source=ds["source"],
                metric_name=ds["metric_name"],
                schema_version=ds["schema_version"],
                collector=ds["collector"],
                normalizer=ds["normalizer"],
                anomaly=ds["anomaly"],
                topic=ds["topic"],
                report_key=ds["report_key"],
                curated_path=ds["curated_path"],
            )
        )
    return out

def get_callables(func_path: str):
    mod_name, func_name = func_path.split(":")
    mod = importlib.import_module(mod_name)
    return getattr(mod, func_name)
