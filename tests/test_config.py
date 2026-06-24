"""Tests for fitness_functions.yaml loading and merging."""

from pathlib import Path

from sqlmesh_ff.config import load_fitness_config


def test_load_defaults_without_file(tmp_path: Path) -> None:
    config = load_fitness_config(tmp_path, config_path="missing.yaml")
    assert config.checks.layer_integrity.enabled is True
    assert config.rules.sql_complexity.thresholds["cte_count"] == [8, 12]


def test_load_yaml_and_merge_overrides(tmp_path: Path) -> None:
    yaml_path = tmp_path / "fitness_functions.yaml"
    yaml_path.write_text(
        """
checks:
  dependency_graph:
    fan_out_warn: 20
rules:
  column_names:
    replacements:
      bad: good
""",
        encoding="utf-8",
    )
    config = load_fitness_config(
        tmp_path,
        overrides={"checks": {"dependency_graph": {"fan_out_fail": 30}}},
    )
    assert config.checks.dependency_graph.fan_out_warn == 20
    assert config.checks.dependency_graph.fan_out_fail == 30
    assert config.rules.column_names.replacements == {"bad": "good"}
