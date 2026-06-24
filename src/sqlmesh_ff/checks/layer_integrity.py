"""Layer integrity check — unidirectional flow and mart domain isolation."""

from __future__ import annotations

from sqlmesh.core.context import Context

from sqlmesh_ff.config import FitnessFunctionsConfig
from sqlmesh_ff.report import LintFinding, normalize_model_name
from sqlmesh_ff.utils.paths import (
    get_layer_from_path,
    get_marts_domain_from_path,
    model_path_relative,
)


def _layer_index(
    layer: str | None, dependency_model_kind: str, layer_order: list[str]
) -> int | None:
    layer_index = {name: idx for idx, name in enumerate(layer_order)}
    if layer:
        return layer_index.get(layer)
    if dependency_model_kind == "EXTERNAL":
        return -1
    return None


def collect_layer_integrity_findings(
    context: Context, config: FitnessFunctionsConfig
) -> list[LintFinding]:
    findings: list[LintFinding] = []
    layer_order = config.layers.order
    marts_layer = config.rules.mart_naming.layer_name

    for _model_name, model_context in context.models.items():
        model = context.get_model(model_context.name)
        if not model or model.kind.name == "EXTERNAL":
            continue

        model_layer = get_layer_from_path(model._path, layer_order)
        model_layer_index = _layer_index(model_layer, model.kind.name, layer_order)
        model_marts_domain = (
            get_marts_domain_from_path(model._path, marts_layer)
            if model_layer == marts_layer
            else None
        )

        for dependency in model.depends_on:
            dependency_model = context.get_model(dependency)
            if not dependency_model:
                continue

            dependency_layer = get_layer_from_path(dependency_model._path, layer_order)
            dependency_layer_index = _layer_index(
                dependency_layer, dependency_model.kind.name, layer_order
            )

            if (
                model_layer_index is not None
                and dependency_layer_index is not None
                and dependency_layer_index > model_layer_index
            ):
                findings.append(
                    LintFinding(
                        check="layer_integrity",
                        severity="error",
                        model=str(model.name),
                        path=model_path_relative(model),
                        message=(
                            f"depends on {normalize_model_name(str(dependency))} "
                            "in a downstream layer"
                        ),
                    )
                )

            if model_layer == marts_layer and dependency_layer == marts_layer:
                dependency_marts_domain = get_marts_domain_from_path(
                    dependency_model._path, marts_layer
                )
                if (
                    model_marts_domain
                    and dependency_marts_domain
                    and model_marts_domain != dependency_marts_domain
                ):
                    findings.append(
                        LintFinding(
                            check="layer_integrity",
                            severity="error",
                            model=str(model.name),
                            path=model_path_relative(model),
                            message=(
                                f"{marts_layer}/{model_marts_domain} depends on "
                                f"{normalize_model_name(str(dependency))} "
                                f"({marts_layer}/{dependency_marts_domain})"
                            ),
                        )
                    )

    return findings
