"""Unified lint runner orchestrating SQLMesh rules and architectural checks."""

from __future__ import annotations

import logging
from pathlib import Path

from sqlmesh.core.context import Context
from sqlmesh.core.linter.definition import AnnotatedRuleViolation

from sqlmesh_ff.checks.custom_exclusions import collect_custom_exclusion_findings
from sqlmesh_ff.checks.dependency_graph import collect_dependency_graph_findings
from sqlmesh_ff.checks.layer_integrity import collect_layer_integrity_findings
from sqlmesh_ff.checks.schema_contracts import collect_schema_contract_findings
from sqlmesh_ff.config import FitnessFunctionsConfig, load_fitness_config
from sqlmesh_ff.context import set_ff_config
from sqlmesh_ff.loader import FitnessLoader
from sqlmesh_ff.report import LintFinding, format_message, normalize_model_name
from sqlmesh_ff.utils.paths import model_path_relative

logger = logging.getLogger(__name__)

CHECK_COLLECTORS = {
    "layer_integrity": lambda ctx, cfg: collect_layer_integrity_findings(ctx, cfg),
    "custom_exclusions": lambda ctx, cfg: collect_custom_exclusion_findings(ctx, cfg),
    "schema_contracts": lambda _ctx, cfg: collect_schema_contract_findings(cfg),
    "dependency_graph": lambda ctx, cfg: collect_dependency_graph_findings(ctx, cfg),
}


class _SilentLinterConsole:
    def show_linter_violations(self, *args, **kwargs) -> None:
        return None


def collect_sqlmesh_findings(context: Context) -> list[LintFinding]:
    findings: list[LintFinding] = []
    silent_console = _SilentLinterConsole()

    for model in context.models.values():
        if model.kind.is_symbolic:
            continue

        linter = context._linters.get(model.project)
        if not linter or not linter.enabled:
            continue

        _, violations = linter.lint_model(model, context, console=silent_console)
        model_label = normalize_model_name(str(model.name))
        for violation in violations:
            if not isinstance(violation, AnnotatedRuleViolation):
                continue

            message = format_message(violation.violation_msg)
            if message.startswith(f"{model_label}: "):
                message = message[len(model_label) + 2 :]

            messages = (
                [part.strip() for part in message.split(";") if part.strip()]
                if violation.rule.name == "sqlcomplexity"
                else [message]
            )

            for part in messages:
                findings.append(
                    LintFinding(
                        check=violation.rule.name,
                        severity=violation.violation_type,
                        model=str(model.name),
                        path=model_path_relative(model),
                        message=part,
                    )
                )

    return findings


def count_models_checked(context: Context) -> int:
    return sum(
        1 for model in context.models.values() if not model.kind.is_symbolic
    )


def _check_enabled(config: FitnessFunctionsConfig, check_name: str) -> bool:
    check = getattr(config.checks, check_name, None)
    return bool(getattr(check, "enabled", False))


def run_all_checks(
    project_root: Path | None = None,
    context: Context | None = None,
    config: FitnessFunctionsConfig | None = None,
    checks: list[str] | None = None,
) -> tuple[list[LintFinding], int, list[str]]:
    project_root = project_root or Path.cwd()
    if config is None:
        config = load_fitness_config(project_root)
    set_ff_config(config)

    context = context or Context(
        paths=[str(project_root)],
        loader=FitnessLoader,
    )

    if checks is None:
        selected = ["sqlmesh"] + [
            name
            for name in CHECK_COLLECTORS
            if _check_enabled(config, name)
        ]
    else:
        selected = checks

    findings: list[LintFinding] = []

    if "sqlmesh" in selected:
        findings.extend(collect_sqlmesh_findings(context))

    for check_name, collector in CHECK_COLLECTORS.items():
        if check_name not in selected:
            continue
        if checks is None and not _check_enabled(config, check_name):
            continue
        findings.extend(collector(context, config))

    return findings, count_models_checked(context), selected
