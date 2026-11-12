from pathlib import Path


import pytest


from bench_runner import config
from bench_runner import runners
from bench_runner.scripts import install


DATA_PATH = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "os, default_timeout", [("linux", 1440), ("darwin", None), ("windows", None)]
)
def test_benchmark_timeout_minutes(tmp_path, monkeypatch, os, default_timeout):
    cfg = config.get_config(DATA_PATH / "bench_runner.toml")
    configured = runners.Runner(
        nickname="configured",
        os=os,
        arch="x86_64",
        hostname="configured",
        timeout_minutes=210,
    )
    default = runners.Runner(
        nickname="default", os=os, arch="x86_64", hostname="default"
    )
    monkeypatch.setattr(cfg, "runners", {"configured": configured, "default": default})
    monkeypatch.setattr(config, "get_config", lambda: cfg)

    source = install.load_yaml(install.TEMPLATE_PATH / "_benchmark.src.yml")
    output = tmp_path / "_benchmark.yml"
    install.write_yaml(output, install.generate__benchmark(source), check=False)
    jobs = install.load_yaml(output)["jobs"]

    assert jobs[f"benchmark-{configured.name}"]["timeout-minutes"] == 210
    default_job = jobs[f"benchmark-{default.name}"]
    if default_timeout is None:
        assert "timeout-minutes" not in default_job
    else:
        assert default_job["timeout-minutes"] == default_timeout
