import pathlib

import pandas as pd
import pytest


def get_data_path(filename: str) -> pathlib.Path:
    """Return a path to a file in the data directory."""
    return pathlib.Path(__file__).parents[2] / "data" / filename


# Working with DataFrames
@pytest.fixture
def df() -> pd.DataFrame:
    return pd.read_csv(get_data_path("01/parsed.csv"))


def test_pandas_1(df: pd.DataFrame, function_to_test):
    assert function_to_test(df) == reference_pandas_1(df)


def reference_pandas_1(df: pd.DataFrame) -> float:
    return df[(df.parsed_place == "Japan") & (df.magType == "mb")].mag.quantile(0.95)


def test_pandas_2(df: pd.DataFrame, function_to_test):
    result = function_to_test(df)
    assert isinstance(result, str)
    assert "%" in result
    assert result == reference_pandas_2(df)


def reference_pandas_2(df: pd.DataFrame) -> str:
    return f"{df[df.parsed_place == 'Indonesia'].tsunami.value_counts(normalize=True).iloc[1,]:.2%}"  # type: ignore


# Data wrangling

# Data aggregation
