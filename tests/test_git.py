import subprocess


import pytest


from bench_runner import git


@pytest.mark.parametrize("reuse", [True, False])
def test_clone_existing_checkout(tmp_path, reuse):
    repo = tmp_path / "repo"
    subprocess.check_call(["git", "init", "--object-format=sha1", repo])
    commit = [
        "git",
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.com",
        "commit",
        "--no-gpg-sign",
        "--allow-empty",
        "-m",
        "Test commit",
    ]
    subprocess.check_call(commit, cwd=repo)
    commit_hash = git.get_log("%H", repo)
    checkout = tmp_path / "checkout"
    git.clone(checkout, str(repo), branch=commit_hash)
    subprocess.check_call(["git", "config", "core.abbrev", "7"], cwd=checkout)
    build_output = checkout / "build-output"
    build_output.touch()

    if not reuse:
        subprocess.check_call(commit, cwd=repo)
        commit_hash = git.get_log("%H", repo)

    git.clone(checkout, str(repo), branch=commit_hash)

    assert build_output.exists() == reuse
    assert git.get_log("%H", checkout) == commit_hash
