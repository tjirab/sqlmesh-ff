"""Filename must match model name."""

from __future__ import annotations

import typing as t
from pathlib import Path

from sqlmesh.core.linter.rule import Rule, RuleViolation
from sqlmesh.core.model import Model

from sqlmesh_ff.context import get_ff_config


class FilenameEqualsModelname(Rule):
    """The filename should equal the model name."""

    def check_model(self, model: Model) -> t.Optional[RuleViolation]:
        if not get_ff_config().rules.filename_equals_modelname.enabled:
            return None
        return (
            self.violation()
            if (model.name.split(".")[-1] != Path(model._path).stem)
            and not model.kind.is_symbolic
            else None
        )
