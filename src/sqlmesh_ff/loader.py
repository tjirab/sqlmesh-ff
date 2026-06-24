"""SQLMesh loader that merges sqlmesh-ff package rules with project linter rules."""

from __future__ import annotations

import os
import typing as t
from pathlib import Path

from sqlglot.helper import subclasses
from sqlmesh.core import constants as c
from sqlmesh.core.linter.definition import RuleSet
from sqlmesh.core.linter.rule import Rule
from sqlmesh.core.loader import SqlMeshLoader
from sqlmesh.utils import UniqueKeyDict
from sqlmesh.utils.metaprogramming import import_python_file

from sqlmesh_ff.config import load_fitness_config
from sqlmesh_ff.context import set_ff_config
from sqlmesh_ff.rules import ALL_RULES


class FitnessLoader(SqlMeshLoader):
    """Load package fitness rules plus optional project-local linter rules."""

    def __init__(self, context, path: Path, **loader_kwargs: t.Any) -> None:
        super().__init__(context, path)
        config_path = loader_kwargs.get("fitness_functions_config", "fitness_functions.yaml")
        overrides = {
            key: value
            for key, value in loader_kwargs.items()
            if key != "fitness_functions_config"
        }
        ff_config = load_fitness_config(
            self.config_path,
            config_path=config_path,
            overrides=overrides or None,
        )
        set_ff_config(ff_config)
        self._ff_config = ff_config

    def _load_linting_rules(self) -> RuleSet:
        user_rules: UniqueKeyDict[str, type[Rule]] = UniqueKeyDict("rules")

        for rule_cls in ALL_RULES:
            user_rules[rule_cls.name] = rule_cls

        for path in self._glob_paths(
            self.config_path / c.LINTER,
            ignore_patterns=self.config.ignore_patterns,
            extension=".py",
        ):
            if os.path.getsize(path):
                self._track_file(path)
                module = import_python_file(path, self.config_path)
                _rule_exclude: t.Set[t.Type[Rule]] = {Rule}  # type: ignore[type-abstract]
                module_rules = subclasses(module.__name__, Rule, exclude=_rule_exclude)
                for user_rule in module_rules:
                    user_rules[user_rule.name] = user_rule

        return RuleSet(user_rules.values())
