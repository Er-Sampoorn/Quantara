import pytest
from services.strategy_engine.compiler import StrategyCompiler
from services.strategy_engine.dsl import StrategyDSLValidator


def test_natural_language_compilation():
    prompt = "Buy when RSI crosses above 30 and price is above EMA 200. Exit when RSI reaches 70. Risk 1% per trade."
    spec, executable = StrategyCompiler.compile_from_prompt(prompt, symbol="AAPL")

    assert spec.symbol == "AAPL"
    assert len(spec.entry_rules) >= 2
    assert len(spec.exit_rules) >= 1
    assert spec.risk_config.risk_per_trade == 0.01

    # Ensure spec passes strict DSL validation
    is_valid, errors = StrategyDSLValidator.validate_spec(spec.model_dump())
    assert is_valid
    assert len(errors) == 0
