from pathlib import Path
import socket


import pytest


from bench_runner import config
from bench_runner import runners


DATA_PATH = Path(__file__).parent / "data"


def test_get_runner_for_hostname(monkeypatch):
    monkeypatch.setattr(socket, "gethostname", lambda: "pyperf")

    runner = runners.get_runner_for_hostname(cfgpath=DATA_PATH / "bench_runner.toml")

    assert runner.os == "linux"
    assert runner.arch == "x86_64"
    assert runner.hostname == "pyperf"
    assert runner.timeout_minutes == 210


@pytest.mark.parametrize("timeout_minutes", [None, 1, 1440])
def test_runner_timeout_minutes_valid(timeout_minutes):
    runner = runners.Runner(
        nickname="x",
        os="linux",
        arch="x86_64",
        hostname="x",
        timeout_minutes=timeout_minutes,
    )
    assert runner.timeout_minutes == timeout_minutes


@pytest.mark.parametrize(
    "timeout_minutes", ["0", "-1", "true", "false", "1.5", '"210"']
)
def test_runner_timeout_minutes_invalid(tmp_path, timeout_minutes):
    cfgpath = tmp_path / "bench_runner.toml"
    contents = (DATA_PATH / "bench_runner.toml").read_text()
    cfgpath.write_text(
        contents.replace(
            "timeout_minutes = 210", f"timeout_minutes = {timeout_minutes}"
        )
    )

    with pytest.raises(ValueError, match="timeout_minutes.*must be a positive integer"):
        config.get_config(cfgpath)
