import pytest

from emergence_lab.batch import parse_controllers, parse_seed_spec, seed_is_complete
from emergence_lab.cli import main


def test_parse_seed_spec():
    assert parse_seed_spec("1-3") == [1, 2, 3]
    assert parse_seed_spec("1,5,9") == [1, 5, 9]
    assert parse_seed_spec("1-2,10,20-21") == [1, 2, 10, 20, 21]
    assert parse_seed_spec("3,1-3") == [3, 1, 2]
    with pytest.raises(ValueError):
        parse_seed_spec("")
    with pytest.raises(ValueError):
        parse_seed_spec("5-1")
    with pytest.raises(ValueError):
        parse_seed_spec("nope")


def test_parse_controllers():
    assert parse_controllers("random, random_r, reactive_r") == [
        "random",
        "random_r",
        "reactive_r",
    ]
    with pytest.raises(ValueError):
        parse_controllers(" , ")


def test_batch_runs_and_resumes(tmp_path, capsys):
    out = tmp_path / "ablation_demo"
    common = [
        "batch",
        "--experiment-id",
        "ablation_demo",
        "--seeds",
        "1-2",
        "--ticks",
        "8",
        "--controllers",
        "random,reactive",
        "--out-root",
        str(out),
        "--no-publish",
    ]
    main(common)
    first = capsys.readouterr().out
    assert "ran=2 skipped=0" in first
    assert (out / "seed_1" / "metrics.csv").is_file()
    assert (out / "seed_2" / "metrics.csv").is_file()
    assert (out / "aggregate.md").is_file()
    assert seed_is_complete(out / "seed_1")

    main(common)
    second = capsys.readouterr().out
    assert "skip seed 1" in second
    assert "skip seed 2" in second
    assert "ran=0 skipped=2" in second
