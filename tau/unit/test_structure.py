"""Structural tests: check module structure follows the template."""

from pathlib import Path

import pytest

import nu

_nu_file: str | None = nu.__file__
assert _nu_file is not None, "nu.__file__ is None — nu must be a regular package"
NU_ROOT = Path(_nu_file).parent

STANDARD_MODULES = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "iota",
    "sigma",
    "mu",
]

FLAT_MODULES = ["psi"]


@pytest.mark.parametrize("module", STANDARD_MODULES)
def test_standard_module_has_public(module: str) -> None:
    """Standard modules have public/__init__.py."""
    assert (NU_ROOT / module / "public" / "__init__.py").exists(), (
        f"{module}/public/__init__.py missing"
    )


@pytest.mark.parametrize("module", STANDARD_MODULES)
def test_standard_module_has_internal(module: str) -> None:
    """Standard modules have _internal/__init__.py."""
    assert (NU_ROOT / module / "_internal" / "__init__.py").exists(), (
        f"{module}/_internal/__init__.py missing"
    )


@pytest.mark.parametrize("module", STANDARD_MODULES)
def test_standard_module_has_no_contract_py(module: str) -> None:
    """contract.py was removed in phase 2.1."""
    assert not (NU_ROOT / module / "contract.py").exists(), (
        f"{module}/contract.py should be removed"
    )


@pytest.mark.parametrize("module", FLAT_MODULES)
def test_flat_module_has_no_public(module: str) -> None:
    """Flat modules (psi) have no public/."""
    assert not (NU_ROOT / module / "public").exists(), f"{module}/public/ should not exist"


@pytest.mark.parametrize("module", FLAT_MODULES)
def test_flat_module_has_no_internal(module: str) -> None:
    """Flat modules (psi) have no _internal/."""
    assert not (NU_ROOT / module / "_internal").exists(), f"{module}/_internal/ should not exist"


def test_mu_version_moved_to_public() -> None:
    """mu/version.py should not exist; __version__ lives in mu/public/."""
    assert not (NU_ROOT / "mu" / "version.py").exists(), (
        "mu/version.py should be removed (moved to mu/public/__init__.py)"
    )
    from nu.mu.public import __version__

    assert isinstance(__version__, str)
    assert __version__


@pytest.mark.parametrize("module", STANDARD_MODULES)
def test_psi_contracts_module_exists(module: str) -> None:
    """psi/contracts/<module>.py exists for each standard module."""
    assert (NU_ROOT / "psi" / "contracts" / f"{module}.py").exists(), (
        f"psi/contracts/{module}.py missing"
    )


def test_psi_contracts_has_aggregate() -> None:
    """psi/contracts/__init__.py has Contracts aggregate."""
    from nu.psi.contracts import Contracts

    assert Contracts.alpha is not None
    assert Contracts.mu is not None
    assert Contracts.beta is not None


def test_psi_has_no_contracts_py_at_root() -> None:
    """psi/contracts is a package, not a single file."""
    assert (NU_ROOT / "psi" / "contracts" / "__init__.py").exists()
    assert not (NU_ROOT / "psi" / "contracts.py").exists()
