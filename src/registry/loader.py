from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

@dataclass
class Dataset:
    dataset_id: str
    enabled: bool
    entity: str
    unit: str
    source: str
    collector: str
    normalizer: str
    anomaly: str
    topic: str
    report_key: str
    curated_path: str

def _load_callable(spec: str) -> Callable[..., Any]:
    mod_path, func_name = spec.split(":")
    mod = importlib.import_module(mod_path)
    return getattr(mod, func_name)

def load_datasets(registry_path: Path) -> list[Dataset]:
    cfg = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    items = cfg.get("datasets", [])
    datasets: list[Dataset] = []
    for it in items:
        ds = Dataset(
            dataset_id=it["dataset_id"],
            enabled=bool(it.get("enabled", True)),
            entity=it["entity"],
            unit=it["unit"],
            source=it["source"],
            collector=it["collector"],
            normalizer=it["normalizer"],
            anomaly=it["anomaly"],
            topic=it["topic"],
            report_key=it["report_key"],
            curated_path=it["curated_path"],
        )
        datasets.append(ds)
    return datasets

def get_callables(ds: Dataset) -> dict[str, Callable[..., Any]]:
    return {
        "collector": _load_callable(ds.collector),
        "normalizer": _load_callable(ds.normalizer),
        "anomaly": _load_callable(ds.anomaly),
        "topic": _load_callable(ds.topic),
    }
