from pathlib import Path

def pass_through(base_dir: Path):
    # Derived metrics are already saved in curated format by the engine.
    # This is a no-op normalizer required by registry schema.
    pass
