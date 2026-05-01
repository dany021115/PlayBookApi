from predictions.models import Strategy
from predictions.strategies.base import BasePickStrategy, Pick
from predictions.strategies.form_streak import FormStreakStrategy
from predictions.strategies.llm_only import LLMOnlyStrategy
from predictions.strategies.totals_consensus import TotalsConsensusStrategy
from predictions.strategies.value_bet import ValueBetStrategy

STRATEGY_REGISTRY: dict[str, type[BasePickStrategy]] = {
    Strategy.Type.VALUE_BET.value: ValueBetStrategy,
    Strategy.Type.FORM_STREAK.value: FormStreakStrategy,
    Strategy.Type.TOTALS_CONSENSUS.value: TotalsConsensusStrategy,
    Strategy.Type.LLM_ONLY.value: LLMOnlyStrategy,
}

__all__ = ["BasePickStrategy", "Pick", "STRATEGY_REGISTRY"]
