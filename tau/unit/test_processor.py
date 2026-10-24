"""Тесты IProcessor, IWorkflow, PipelineWorkflow (через BetaResolver)."""

from typing import Any

import pytest

from nu.psi.contracts.beta import BetaResolver, IProcessor, IWorkflow


class AddOne(IProcessor):
    async def process(self, data: Any) -> Any:
        return data + 1


class MultiplyByTwo(IProcessor):
    async def process(self, data: Any) -> Any:
        return data * 2


class FailProcessor(IProcessor):
    async def process(self, data: Any) -> Any:
        raise RuntimeError("boom")


def test_resolver_creates_workflow() -> None:
    workflow = BetaResolver().make_workflow()
    assert isinstance(workflow, IWorkflow)


async def test_pipeline_sequential_execution() -> None:
    workflow: IWorkflow = BetaResolver().make_workflow(initial_data=5)
    await workflow.run([AddOne(), MultiplyByTwo()])
    # (5 + 1) * 2 = 12
    assert workflow.get_result() == 12


async def test_pipeline_empty_stages() -> None:
    workflow: IWorkflow = BetaResolver().make_workflow(initial_data=42)
    await workflow.run([])
    assert workflow.get_result() == 42


async def test_pipeline_fail_fast() -> None:
    workflow: IWorkflow = BetaResolver().make_workflow(initial_data=1)
    with pytest.raises(RuntimeError, match="boom"):
        await workflow.run([AddOne(), FailProcessor(), MultiplyByTwo()])
    assert workflow.get_result() == 1


def test_pipeline_initial_data() -> None:
    workflow: IWorkflow = BetaResolver().make_workflow(initial_data=100)
    assert workflow.get_result() == 100
