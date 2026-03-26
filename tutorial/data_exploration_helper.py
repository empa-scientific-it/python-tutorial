import numpy as np
import pandas as pd

from tutorial.my_bubbly import bubbleplot


def get_happiness_data():
    # Load the dataset
    happiness_df = pd.read_csv(
        "data/data_exploration/World-happiness-report-updated_2024.csv",
        encoding="latin1",
        usecols=[
            "Freedom to make life choices",
            "Life Ladder",
            "Country name",
            "year",
            "Log GDP per capita",
        ],
    )

    return happiness_df


def get_clean_dataset(happiness_df: pd.DataFrame) -> pd.DataFrame:
    # Define the range of possible years
    min_year = happiness_df["year"].min()
    max_year = happiness_df["year"].max()
    possible_years = np.arange(min_year, max_year + 1)

    # Create entries for each country for every year
    all_years_countries = pd.DataFrame(
        [
            (country, year)
            for country in happiness_df["Country name"].unique()
            for year in possible_years
        ],
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
    # Apply forward fill for any remaining NaNs (shouldn't be any after the previous step, but for robustness)
    complete_happiness_df = complete_happiness_df.sort_values(
        by=["Country name", "year"]
    ).ffill()

    return complete_happiness_df


def get_clean_dataset_with_region(happiness_df: pd.DataFrame) -> pd.DataFrame:
    # Define the range of possible years
    complete_happiness_df = get_clean_dataset(happiness_df)

    # Load the region mapping
    region_df = pd.read_csv(
        "data/data_exploration/country_region_mapping.csv",
        encoding="latin1",
        usecols=["Country name", "Regional indicator"],
    ).drop_duplicates()

    # Merge region information into the main dataframe
    merged_happiness_df = pd.merge(
        complete_happiness_df, region_df, on="Country name", how="left"
    )

    # Fill any missing 'Regional indicator' values
    merged_happiness_df["Regional indicator"] = merged_happiness_df[
        "Regional indicator"
    ].fillna("Unknown")

    return merged_happiness_df


def full_clean_dataset():
    happiness_df = get_happiness_data()

    complete_happiness_df = get_clean_dataset_with_region(happiness_df)

    log_gdp_df = complete_happiness_df[["Country name", "year", "Log GDP per capita"]]
    # get global min without 1
    log_gdp_df_without_1 = log_gdp_df[log_gdp_df["Log GDP per capita"] != 1]
    global_min_log_gdp_per_country = log_gdp_df_without_1["Log GDP per capita"].min()
    # replace 1 with global min
    log_gdp_df.loc[log_gdp_df["Log GDP per capita"] == 1, "Log GDP per capita"] = (
        global_min_log_gdp_per_country
    )
    # get global max
    global_max_log_gdp_per_country = log_gdp_df["Log GDP per capita"].max()

    resized_log_gdp_df = log_gdp_df.copy()
    # Scale exponentially between 1 and 500
    resized_log_gdp_df["Resized Log GDP per capita"] = (
        np.exp(log_gdp_df["Log GDP per capita"])
        * 500
        / (
            np.exp(global_max_log_gdp_per_country)
            - np.exp(global_min_log_gdp_per_country)
        )
    )

    # append to final_happiness_df
    final_happiness_df = pd.merge(
        complete_happiness_df,
        resized_log_gdp_df[["Country name", "year", "Resized Log GDP per capita"]],
        on=["Country name", "year"],
        how="left",
    )

    return final_happiness_df


def load_bubbleplot_full_happiness_figure():
    final_happiness_df = full_clean_dataset()

    # Load the dataset
    figure = bubbleplot(
        dataset=final_happiness_df,
        x_column="Freedom to make life choices",
        y_column="Life Ladder",
        bubble_column="Country name",
        time_column="year",
        size_column="Resized Log GDP per capita",
        color_column="Regional indicator",
        x_title="Freedom to make life choices",
        y_title="Happiness Score",
        title="happyness Indicators",
        x_logscale=False,
        scale_bubble=0.2,
        height=650,
    )
    return figure


def load_full_happiness_figure():
    final_happiness_df = full_clean_dataset()
    dataset = final_happiness_df

    x_column = "Freedom to make life choices"
    y_column = "Life Ladder"
    description_column = "Country name"
    bubble_size_column = "Resized Log GDP per capita"
    category_column = "Regional indicator"
    years = dataset["year"].unique()
    years.sort()

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

    def frame_by_year_with_size_and_category(
        dataset,
        year,
        x_column,
        y_column,
        description_column,
        category_column,
        bubble_size_column,
    ):
        """Make a frame for a given year with bubble size"""

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

    figure = set_layout(
        x_title=x_column,
        y_title=y_column,
        title="Happiness Indicators",
        x_logscale=False,
        y_logscale=False,
        show_slider=True,
        slider_scale=dataset["year"].unique(),
        show_button=True,
        show_legend=True,
    )

    figure["data"] = [
        trace_by_category(
            dataset,
            2005,
            x_column,
            y_column,
            description_column,
            category_column,
            category,
            bubble_size_column,
        )
        for category in dataset[category_column].unique()
    ]

    figure["layout"]["xaxis"]["range"] = [0, 1.2]
    figure["layout"]["yaxis"]["range"] = [0, 9]
    figure["layout"]["showlegend"] = True

    # Add time frames
    figure["frames"] = [
        frame_by_year_with_size_and_category(
            dataset,
            year,
            x_column,
            y_column,
            description_column,
            category_column,
            bubble_size_column,
        )
        for year in years
    ]
    return figure


def slider_step(year):
    """Creates a slider step."""

    slider_step = {
        "args": [
            [year],
            {
                "frame": {"duration": 300, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 300},
            },
        ],
        "label": str(year),
        "method": "animate",
    }
    return slider_step


def create_slider(years):
    """Creates a slider."""

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Year:",
            "visible": True,
            "xanchor": "right",
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [],
    }
    sliders_dict["steps"] = [slider_step(year) for year in years]

    return sliders_dict


def add_button(figure):
    figure["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [
                        None,
                        {
                            "frame": {"duration": 500, "redraw": False},
                            "fromcurrent": True,
                            "transition": {
                                "duration": 300,
                                "easing": "quadratic-in-out",
                            },
                        },
                    ],
                    "label": "Play",
                    "method": "animate",
                },
                {
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0},
                        },
                    ],
                    "label": "Pause",
                    "method": "animate",
                },
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top",
        }
    ]
    return figure


def set_layout(
    x_title=None,
    y_title=None,
    title=None,
    x_logscale=False,
    y_logscale=False,
    show_slider=True,
    slider_scale=None,
    show_button=True,
    show_legend=False,
    width=None,
    height=None,
):
    """Sets the layout for the figure."""

    # Define the figure object as a dictionary
    figure = {"data": [], "layout": {}, "frames": []}

    figure = set_2daxes(figure, x_title, y_title, x_logscale, y_logscale)

    figure["layout"]["title"] = title
    figure["layout"]["hovermode"] = "closest"
    figure["layout"]["showlegend"] = show_legend
    figure["layout"]["margin"] = {"b": 50, "t": 50, "pad": 5}

    if width:
        figure["layout"]["width"] = width
    if height:
        figure["layout"]["height"] = height

    # Add slider for the time scale
    if show_slider:
        sliders_dict = create_slider(slider_scale)
        figure["layout"]["sliders"] = [sliders_dict]
    else:
        sliders_dict = {}

    # Add a pause-play button
    if show_button:
        add_button(figure)

    # Return the figure object
    return figure


def set_2daxes(figure, x_title=None, y_title=None, x_logscale=False, y_logscale=False):
    """Sets 2D axes"""

    figure["layout"]["xaxis"] = {"title": x_title, "autorange": False}
    figure["layout"]["yaxis"] = {"title": y_title, "autorange": False}

    if x_logscale:
        figure["layout"]["xaxis"]["type"] = "log"
    if y_logscale:
        figure["layout"]["yaxis"]["type"] = "log"

    return figure


def get_scatter_figure(dataset, x_column, y_column, description_column):
    """Creates a scatter plot."""

    # Define figure
    figure = {"data": [], "layout": {}, "frames": []}

    # Get a random representative year
    year = 2010

    # Make the trace
    trace = {
        "x": list(dataset.loc[dataset["year"] == year, x_column]),
        "y": list(dataset.loc[dataset["year"] == year, y_column]),
        "mode": "markers",
        "text": list(dataset.loc[dataset["year"] == year, description_column]),
    }

    # Append the trace to the figure
    figure["data"] = [trace]
    return figure


def get_scatter_figure_with_years(dataset, x_column, y_column, description_column):
    """Creates a scatter plot with years."""

    x_column = "Freedom to make life choices"
    y_column = "Life Ladder"
    description_column = "Country name"
    # time_column = 'year'
    figure = get_scatter_figure(dataset, x_column, y_column, description_column)

    def frame_by_year(dataset, year, x_column, y_column, description_column):
        """Make a trace for a given year"""
        # Make a trace
        trace = {
            "x": list(dataset.loc[dataset["year"] == year, x_column]),
            "y": list(dataset.loc[dataset["year"] == year, y_column]),
            "mode": "markers",
            "text": list(dataset.loc[dataset["year"] == year, description_column]),
            "type": "scatter",
        }
        frame = {"data": [trace], "name": str(year)}
        return frame

    # Get the years
    years = dataset["year"].unique()
    years.sort()

    # Set timestep
    figure["frames"] = [
        frame_by_year(dataset, year, x_column, y_column, description_column)
        for year in years
    ]
    return figure
