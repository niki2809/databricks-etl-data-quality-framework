import subprocess

from framework.config import load_config, resolve


def run_dbt(*args: str) -> subprocess.CompletedProcess:
    cfg = load_config()
    cmd = [
        "dbt",
        *args,
        "--project-dir", resolve(cfg["dbt"]["project_dir"]),
        "--profiles-dir", resolve(cfg["dbt"]["profiles_dir"]),
        "--target", cfg["dbt"]["target"],
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


def run_full_pipeline() -> dict:
    return {
        "seed": run_dbt("seed", "--full-refresh"),
        "run": run_dbt("run"),
        "test": run_dbt("test"),
    }
