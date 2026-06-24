"""Metadata fitness rules — owner, description, grain."""

from __future__ import annotations

import typing as t

from sqlmesh.core.linter.rule import Rule, RuleViolation
from sqlmesh.core.model import Model

from sqlmesh_ff.context import get_ff_config


class NoMissingOwner(Rule):
    """Model owner should always be specified."""

    def check_model(self, model: Model) -> t.Optional[RuleViolation]:
        if not get_ff_config().rules.metadata.owner:
            return None
        return (
            self.violation() if not model.owner and not model.kind.is_symbolic else None
        )


class NoMissingDescription(Rule):
    """Model description should always be specified."""

    def check_model(self, model: Model) -> t.Optional[RuleViolation]:
        if not get_ff_config().rules.metadata.description:
            return None
        return (
            self.violation()
            if not model.description and not model.kind.is_symbolic
            else None
        )


class NoMissingGrain(Rule):
    """Model grains should always be specified."""

    def check_model(self, model: Model) -> t.Optional[RuleViolation]:
        if not get_ff_config().rules.metadata.grain:
            return None
        return (
            self.violation()
            if not model.grains and not model.kind.is_symbolic
            else None
        )
