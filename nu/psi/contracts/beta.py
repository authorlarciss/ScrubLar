"""Контракт beta для внешнего использования."""

from nu.beta.public import BetaResolver as BetaResolver
from nu.beta.public import IEventBus as IEventBus
from nu.beta.public import IProcessor as IProcessor
from nu.beta.public import IWorkflow as IWorkflow

__all__ = ["IProcessor", "IWorkflow", "IEventBus", "BetaResolver"]
