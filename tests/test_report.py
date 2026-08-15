from emergence_lab.analytics.report import NOTES_TEMPLATE, publish_report
from emergence_lab.analytics.summarize import batch_dir_for_compare_out, summarize_batch
from emergence_lab.cli import main

from test_summarize import _batch


def test_publish_copies_stats_and_creates_notes(tmp_path):
    stats = tmp_path / "results" / "demo_batch"
    summarize_batch(_batch(tmp_path), stats)
    reports = tmp_path / "reports"
    lab_log = tmp_path / "docs" / "lab_log.md"
    dest = publish_report(stats, reports_dir=reports, lab_log=lab_log, batch_id="demo_batch")
    assert dest == reports / "demo_batch"
    assert (dest / "aggregate.md").is_file()
    assert (dest / "all_metrics.csv").is_file()
    assert (dest / "by_controller.csv").is_file()
    assert (dest / "paired_deltas.csv").is_file()
    notes = (dest / "NOTES.md").read_text(encoding="utf-8")
    assert "pending interpretation" in notes
    log = lab_log.read_text(encoding="utf-8")
    assert "`demo_batch`" in log
    assert "pending" in log


def test_publish_does_not_overwrite_notes_or_duplicate_lab_log(tmp_path):
    stats = tmp_path / "results" / "demo_batch"
    summarize_batch(_batch(tmp_path), stats)
    reports = tmp_path / "reports"
    lab_log = tmp_path / "lab_log.md"
    dest = publish_report(stats, reports_dir=reports, lab_log=lab_log, batch_id="demo_batch")
    (dest / "NOTES.md").write_text("human interpretation\n", encoding="utf-8")
    first_log = lab_log.read_text(encoding="utf-8")
    publish_report(stats, reports_dir=reports, lab_log=lab_log, batch_id="demo_batch")
    assert (dest / "NOTES.md").read_text(encoding="utf-8") == "human interpretation\n"
    assert lab_log.read_text(encoding="utf-8") == first_log
    assert first_log.count("— `demo_batch`") == 1


def test_summarize_publish_flag(tmp_path):
    root = _batch(tmp_path)
    reports = tmp_path / "reports"
    lab_log = tmp_path / "lab_log.md"
    paths = summarize_batch(
        root,
        publish=True,
        reports_dir=reports,
        lab_log=lab_log,
    )
    assert paths["report"] == reports / root.name
    assert (paths["report"] / "aggregate.md").is_file()
    skipped = summarize_batch(root, publish=False, reports_dir=reports, lab_log=lab_log)
    assert "report" not in skipped


def test_cli_summarize_publish(tmp_path, capsys):
    root = _batch(tmp_path)
    reports = tmp_path / "reports"
    lab_log = tmp_path / "lab_log.md"
    main(
        [
            "summarize",
            str(root),
            "--reports-dir",
            str(reports),
            "--lab-log",
            str(lab_log),
        ]
    )
    captured = capsys.readouterr().out
    assert "Published" in captured
    assert (reports / root.name / "aggregate.md").is_file()
    assert lab_log.exists()


def test_cli_summarize_no_publish(tmp_path):
    root = _batch(tmp_path)
    reports = tmp_path / "reports"
    lab_log = tmp_path / "lab_log.md"
    main(
        [
            "summarize",
            str(root),
            "--no-publish",
            "--reports-dir",
            str(reports),
            "--lab-log",
            str(lab_log),
        ]
    )
    assert not reports.exists()
    assert not lab_log.exists()
    assert (root / "aggregate.md").is_file()


def test_notes_template_mentions_batch():
    assert "`demo`" in NOTES_TEMPLATE.format(batch_id="demo")


def test_batch_dir_for_compare_out():
    assert batch_dir_for_compare_out("/tmp/exp/seed_7").name == "exp"
    assert batch_dir_for_compare_out("/tmp/compare_seed1").name == "compare_seed1"
