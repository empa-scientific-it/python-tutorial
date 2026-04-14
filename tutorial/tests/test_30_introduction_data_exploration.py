import numpy as np
import pandas as pd
import pytest

from tutorial.data_exploration_helper import (
    full_clean_dataset,
    get_clean_dataset,
    get_happiness_data,
    load_full_happiness_figure,
)

input_args = [1]


def reference_read_in_dataframe(path_to_happiness: str) -> pd.DataFrame:
    """Read in the data from the csv file"""
    # Read in the data
    happiness_df = pd.read_csv(path_to_happiness, encoding="latin1")

    return happiness_df


@pytest.mark.parametrize("input_arg", input_args)
def test_read_in_dataframe(input_arg, function_to_test):
    """The test case(s)"""
    # Get the path to the data
    path_to_happiness = "data/data_exploration/World-happiness-report-updated_2024.csv"

    # Read in the data
    happiness_df = reference_read_in_dataframe(path_to_happiness)

    result = function_to_test(path_to_happiness)
    assert isinstance(result, pd.DataFrame), (
        "Your function should return a pd.DataFrame, but it returned None. Did you forget the return statement?"
    )
    # Check if the two DataFrames are equal
    assert happiness_df.equals(result)


def reference_explore_dataset(happiness_df: pd.DataFrame) -> dict:
    n_rows, n_columns = happiness_df.shape
    n_countries = happiness_df["Country name"].nunique()
    n_duplicates = int(happiness_df.duplicated().sum())
    column_with_most_nans = happiness_df.isna().sum().idxmax()
    happiest_2023 = (
        happiness_df[happiness_df["year"] == 2023]
        .nlargest(1, "Life Ladder")["Country name"]
        .iloc[0]
    )
    return {
        "n_rows": n_rows,
        "n_columns": n_columns,
        "n_countries": n_countries,
        "n_duplicates": n_duplicates,
        "column_with_most_nans": column_with_most_nans,
        "happiest_country_2023": happiest_2023,
    }


@pytest.mark.parametrize("input_arg", input_args)
def test_explore_dataset(input_arg, function_to_test):
    happiness_df = reference_read_in_dataframe(
        "data/data_exploration/World-happiness-report-updated_2024.csv"
    )
    ref = reference_explore_dataset(happiness_df)
    sol = function_to_test(happiness_df)
    assert isinstance(sol, dict), (
        "Your function should return a dict, but it returned None. Did you forget the return statement?"
    )
    for key in ref:
        assert key in sol, f"Missing key '{key}' in the returned dictionary"
        assert sol[key] == ref[key], (
            f"Value for '{key}' is {sol[key]}, expected {ref[key]}"
        )


def reference_clean_dataset(happiness_df: pd.DataFrame) -> pd.DataFrame:
    # Define the range of possible years
    min_year = happiness_df["year"].min()
    max_year = happiness_df["year"].max()
    possible_years = np.arange(min_year, max_year + 1)
    possible_countries = happiness_df["Country name"].unique()

    # Create entries for each country for every year
    all_years_countries = pd.DataFrame(
        [(country, year) for country in possible_countries for year in possible_years],
        columns=["Country name", "year"],
    )
    # Extend the happiness_df to include all years for each country

    complete_happiness_df = all_years_countries.merge(
        happiness_df, on=["Country name", "year"], how="left"
    )

    # Set initial values to 1:
    year_2005 = complete_happiness_df["year"] == 2005
    complete_happiness_df.loc[year_2005] = complete_happiness_df.loc[year_2005].fillna(
        1
    )
    # Apply forward fill for any remaining NaNs (make sure sorting is in the right order)
    complete_happiness_df = complete_happiness_df.sort_values(
        by=["Country name", "year"]
    ).ffill()

    return complete_happiness_df


@pytest.mark.parametrize("input_arg", input_args)
def test_clean_dataset(input_arg, function_to_test):
    # raise TypeError("get_happiness_data() should return a DataFrame")
    hapiness_df = get_happiness_data()

    clean_ref = reference_clean_dataset(hapiness_df)
    clean_sol = function_to_test(hapiness_df)
    assert isinstance(clean_sol, pd.DataFrame), (
        "Your function should return a pd.DataFrame, but it returned None. Did you forget the return statement?"
    )
    assert "Country name" in clean_sol.columns and "year" in clean_sol.columns, (
        "The output should contain 'Country name' and 'year' columns"
    )
    clean_ref_sorted = clean_ref.sort_values(by=["Country name", "year"]).reset_index(
        drop=True
    )
    clean_sol_sorted = clean_sol.sort_values(by=["Country name", "year"]).reset_index(
        drop=True
    )

    # Check if the two DataFrames are equal, ignoring the index
    assert clean_ref_sorted.equals(clean_sol_sorted)

    import matplotlib.pyplot as plt

    # Plot the histogram of the years
    plt.figure(figsize=(10, 6))  # Adjust figure size for better readability
    plt.hist(
        clean_ref["year"], bins=2023 - 2005 + 1, edgecolor="grey"
    )  # Adjust bins as needed
    plt.title("Histogram of Years")
    plt.xlabel("Year")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()


def reference_add_regional_indicator(
    cleaned_happiness_df: pd.DataFrame, region_df: pd.DataFrame
) -> pd.DataFrame:
    # Merge region information into the main dataframe
    final_happiness_df = pd.merge(
        cleaned_happiness_df, region_df, on="Country name", how="left"
    )

    # Fill any missing 'Regional indicator' values
    final_happiness_df["Regional indicator"] = final_happiness_df[
        "Regional indicator"
    ].fillna("Unknown")

    return final_happiness_df


@pytest.mark.parametrize("input_arg", input_args)
def test_add_regional_indicator(input_arg, function_to_test):
    # Load the dataset
    cleaned_happiness_df = get_clean_dataset(get_happiness_data())

    # Load the region mapping
    region_df = pd.read_csv(
        "data/data_exploration/country_region_mapping.csv",
        encoding="latin1",
        usecols=["Country name", "Regional indicator"],
    ).drop_duplicates()

    clean_ref = reference_add_regional_indicator(cleaned_happiness_df, region_df)
    clean_sol = function_to_test(cleaned_happiness_df, region_df)

    assert isinstance(clean_sol, pd.DataFrame), (
        "Your function should return a pd.DataFrame, but it returned None. Did you forget the return statement?"
    )
    # Sort both DataFrames to ensure order-independent comparison
    sort_cols = ["Country name", "year"]
    clean_ref_sorted = clean_ref.sort_values(by=sort_cols).reset_index(drop=True)
    clean_sol_sorted = clean_sol.sort_values(by=sort_cols).reset_index(drop=True)
    assert clean_ref_sorted.equals(clean_sol_sorted)


# solution_frames_with_category


def reference_frames_with_category(
    dataset: pd.DataFrame,
    year: int,
    x_column: str,
    y_column: str,
    description_column: str,
    category_column: str,
    bubble_size_column: str,
) -> dict:
    """Make a frame for a given year with bubble size"""

    def trace_by_category(
        dataset,
        year,
        x_column,
        y_column,
        description_column,
        category_column,
        category,
        bubble_size_column,
    ):
        """Make a trace for a given year with bubble size"""
        # Make a trace
        trace = {
            "x": list(
                dataset.loc[
                    (dataset["year"] == year) & (dataset[category_column] == category),
                    x_column,
                ]
            ),
            "y": list(
                dataset.loc[
                    (dataset["year"] == year) & (dataset[category_column] == category),
                    y_column,
                ]
            ),
            "mode": "markers",
            "text": list(dataset.loc[dataset["year"] == year, description_column]),
            "marker": {
                "size": list(
                    dataset.loc[
                        (dataset["year"] == year)
                        & (dataset[category_column] == category),
                        bubble_size_column,
                    ]
                ),
                "sizemode": "area",
                "sizeref": 1,
            },
            "type": "scatter",
            "name": category,
        }
        return trace

    frame = {
        "data": [
            trace_by_category(
                dataset,
                year,
                x_column,
                y_column,
                description_column,
                category_column,
                category,
                bubble_size_column,
            )
            for category in dataset[category_column].unique()
        ],
        "name": str(year),
    }
    return frame


@pytest.mark.parametrize("input_arg", input_args)
def test_frames_with_category(input_arg, function_to_test):
    # Load the dataset
    dataset = full_clean_dataset()

    year = 2005
    x_column = "Freedom to make life choices"
    y_column = "Life Ladder"
    description_column = "Country name"
    bubble_size_column = "Resized Log GDP per capita"
    category_column = "Regional indicator"

    clean_ref = reference_frames_with_category(
        dataset,
        year,
        x_column,
        y_column,
        description_column,
        category_column,
        bubble_size_column,
    )
    clean_sol = function_to_test(
        dataset,
        year,
        x_column,
        y_column,
        description_column,
        category_column,
        bubble_size_column,
    )

    assert isinstance(clean_sol, dict), (
        "Your function should return a dict, but it returned None. Did you forget the return statement?"
    )
    assert "data" in clean_sol and "name" in clean_sol, (
        "The returned dict should have 'data' and 'name' keys"
    )
    assert clean_ref["name"] == clean_sol["name"], (
        f"Frame name mismatch: expected '{clean_ref['name']}', got '{clean_sol['name']}'"
    )
    # Compare traces regardless of category order
    ref_traces = sorted(clean_ref["data"], key=lambda t: t["name"])
    sol_traces = sorted(clean_sol["data"], key=lambda t: t["name"])
    assert len(ref_traces) == len(sol_traces), (
        f"Expected {len(ref_traces)} traces, got {len(sol_traces)}"
    )
    for ref_t, sol_t in zip(ref_traces, sol_traces, strict=True):
        assert ref_t["name"] == sol_t["name"], (
            f"Trace name mismatch: expected '{ref_t['name']}', got '{sol_t['name']}'"
        )
        assert ref_t == sol_t, f"Trace data mismatch for category '{ref_t['name']}'"

    from plotly.offline import iplot

    figure = load_full_happiness_figure()
    iplot(figure)
