import numpy as np
import pandas as pd


def bubbleplot(
    dataset,
    x_column,
    y_column,
    bubble_column,
    z_column=None,
    time_column=None,
    size_column=None,
    color_column=None,
    x_logscale=False,
    y_logscale=False,
    z_logscale=False,
    x_range=None,
    y_range=None,
    z_range=None,
    x_title=None,
    y_title=None,
    z_title=None,
    title=None,
    colorbar_title=None,
    scale_bubble=1,
    colorscale=None,
    marker_opacity=None,
    marker_border_width=None,
    show_slider=True,
    show_button=True,
    show_colorbar=True,
    show_legend=None,
    width=None,
    height=None,
):
    """Makes the animated and interactive bubble charts from a given dataset."""

    # Set category_column as None and update it as color_column only in case
    # color_column is not None and categorical, in which case set color_column as None
    category_column = None
    if color_column:  # Can be numerical or categorical
        if dataset[color_column].dtype.name in ["category", "object", "bool"]:
            category_column = color_column
            color_column = None

    # Set the variables for making the grid
    if time_column:
        years = dataset[time_column].unique()
    else:
        years = None
        show_slider = False
        show_button = False

    column_names = [x_column, y_column]

    if z_column:
        column_names.append(z_column)
        axes3d = True
    else:
        axes3d = False

    column_names.append(bubble_column)

    if size_column:
        column_names.append(size_column)

    if color_column:
        column_names.append(color_column)

    # Make the grid
    if category_column:
        categories = dataset[category_column].unique()
        col_name_template = "{}+{}+{}_grid"
        grid = make_grid_with_categories(
            dataset, column_names, time_column, category_column, years, categories
        )
        if show_legend is None:
            showlegend = True
        else:
            showlegend = show_legend
    else:
        col_name_template = "{}+{}_grid"
        grid = make_grid(dataset, column_names, time_column, years)
        if show_legend is None:
            showlegend = False
        else:
            showlegend = show_legend

    # Set the layout
    if show_slider:
        slider_scale = years
    else:
        slider_scale = None

    figure, sliders_dict = set_layout(
        x_title,
        y_title,
        z_title,
        title,
        x_logscale,
        y_logscale,
        z_logscale,
        axes3d,
        show_slider,
        slider_scale,
        show_button,
        showlegend,
        width,
        height,
    )

    if size_column:
        sizeref = (
            2.0 * max(dataset[size_column]) / (scale_bubble * 80**2)
        )  # Set the reference size for the bubbles
    else:
        sizeref = None

    # Add the frames
    if category_column:
        # Add the base frame
        for category in categories:
            if time_column:
                year = min(years)  # The earliest year for the base frame
                col_name_template_year = col_name_template.format(year, {}, {})
            else:
                col_name_template_year = "{}+{}_grid"
            trace = get_trace(
                grid,
                col_name_template_year,
                x_column,
                y_column,
                bubble_column,
                z_column,
                size_column,
                sizeref,
                scale_bubble,
                marker_opacity,
                marker_border_width,
                category=category,
            )
            if z_column:
                trace["type"] = "scatter3d"
            figure["data"].append(trace)

        # Add time frames
        if time_column:  # Only if time_column is not None
            for year in years:
                frame = {"data": [], "name": str(year)}
                for category in categories:
                    col_name_template_year = col_name_template.format(year, {}, {})
                    trace = get_trace(
                        grid,
                        col_name_template_year,
                        x_column,
                        y_column,
                        bubble_column,
                        z_column,
                        size_column,
                        sizeref,
                        scale_bubble,
                        marker_opacity,
                        marker_border_width,
                        category=category,
                    )
                    if z_column:
                        trace["type"] = "scatter3d"
                    frame["data"].append(trace)

                figure["frames"].append(frame)

                if show_slider:
                    add_slider_steps(sliders_dict, year)

    else:
        # Add the base frame
        if time_column:
            year = min(years)  # The earliest year for the base frame
            col_name_template_year = col_name_template.format(year, {})
        else:
            col_name_template_year = "{}_grid"
        trace = get_trace(
            grid,
            col_name_template_year,
            x_column,
            y_column,
            bubble_column,
            z_column,
            size_column,
            sizeref,
            scale_bubble,
            marker_opacity,
            marker_border_width,
            color_column,
            colorscale,
            show_colorbar,
            colorbar_title,
        )
        if z_column:
            trace["type"] = "scatter3d"
        figure["data"].append(trace)

        # Add time frames
        if time_column:  # Only if time_column is not None
            for year in years:
                col_name_template_year = col_name_template.format(year, {})
                frame = {"data": [], "name": str(year)}
                trace = get_trace(
                    grid,
                    col_name_template_year,
                    x_column,
                    y_column,
                    bubble_column,
                    z_column,
                    size_column,
                    sizeref,
                    scale_bubble,
                    marker_opacity,
                    marker_border_width,
                    color_column,
                    colorscale,
                    show_colorbar,
                    colorbar_title,
                )
                if z_column:
                    trace["type"] = "scatter3d"
                frame["data"].append(trace)
                figure["frames"].append(frame)
                if show_slider:
                    add_slider_steps(sliders_dict, year)

    # Set ranges for the axes
    if x_range is None:
        x_range = set_range(dataset[x_column], x_logscale)

    if y_range is None:
        y_range = set_range(dataset[y_column], y_logscale)

    if axes3d:
        if z_range is None:
            z_range = set_range(dataset[z_column], z_logscale)
        figure["layout"]["scene"]["xaxis"]["range"] = x_range
        figure["layout"]["scene"]["yaxis"]["range"] = y_range
        figure["layout"]["scene"]["zaxis"]["range"] = z_range
    else:
        figure["layout"]["xaxis"]["range"] = x_range
        figure["layout"]["yaxis"]["range"] = y_range

    if show_slider:
        figure["layout"]["sliders"] = [sliders_dict]

    return figure


def make_grid(dataset, column_names, time_column, years=None):
    """Makes the grid for the plot as a pandas DataFrame by-passing the use of `plotly.grid_objs`
    that is unavailable in the offline mode for `plotly`. The grids are designed using the `col_name_template`
    from the `column_names` of the `dataset`."""

    grid = pd.DataFrame()
    if time_column:
        col_name_template = "{}+{}_grid"
        if years is None:
            years = dataset[time_column].unique()

        for year in years:
            dataset_by_year = dataset[(dataset[time_column] == int(year))]
            for col_name in column_names:
                # Each column name is unique
                temp = col_name_template.format(year, col_name)
                if dataset_by_year[col_name].size != 0:
                    grid = grid.append(
                        {"value": list(dataset_by_year[col_name]), "key": temp},
                        ignore_index=True,
                    )
    else:
        # Check if this can be simplified
        for col_name in column_names:
            # Each column name is unique
            grid = grid.append(
                {"value": list(dataset[col_name]), "key": col_name + "_grid"},
                ignore_index=True,
            )

    return grid


def make_grid_with_categories(
    dataset, column_names, time_column, category_column, years=None, categories=None
):
    """Makes the grid for the plot as a pandas DataFrame by-passing the use of plotly.grid_objs
    that is unavailable in the offline mode for plotly. The grids are designed using the `col_name_template`
    from the `column_names` of the `dataset` using the `category_column` for catergories."""

    grid = pd.DataFrame()
    if categories is None:
        categories = dataset[category_column].unique()
    if time_column:
        col_name_template = "{}+{}+{}_grid"
        if years is None:
            years = dataset[time_column].unique()

        for year in years:
            for category in categories:
                dataset_by_year_and_cat = dataset[
                    (dataset[time_column] == int(year))
                    & (dataset[category_column] == category)
                ]
                for col_name in column_names:
                    # Each column name is unique
                    temp = col_name_template.format(year, col_name, category)
                    if dataset_by_year_and_cat[col_name].size != 0:
                        grid = grid.append(
                            {
                                "value": list(dataset_by_year_and_cat[col_name]),
                                "key": temp,
                            },
                            ignore_index=True,
                        )
    else:
        col_name_template = "{}+{}_grid"
        for category in categories:
            dataset_by_cat = dataset[(dataset[category_column] == category)]
            for col_name in column_names:
                # Each column name is unique
                temp = col_name_template.format(col_name, category)
                if dataset_by_cat[col_name].size != 0:
                    grid = grid.append(
                        {"value": list(dataset_by_cat[col_name]), "key": temp},
                        ignore_index=True,
                    )

    return grid


def set_layout(
    x_title=None,
    y_title=None,
    z_title=None,
    title=None,
    x_logscale=False,
    y_logscale=False,
    z_logscale=False,
    axes3d=False,
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

    # Start with filling the layout first
    if axes3d:
        figure = set_3daxes(
            figure, x_title, y_title, z_title, x_logscale, y_logscale, z_logscale
        )
    else:
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
        sliders_dict = add_slider(figure, slider_scale)
    else:
        sliders_dict = {}

    # Add a pause-play button
    if show_button:
        add_button(figure)

    # Return the figure object
    return figure, sliders_dict


def set_2daxes(figure, x_title=None, y_title=None, x_logscale=False, y_logscale=False):
    """Sets 2D axes"""

    figure["layout"]["xaxis"] = {"title": x_title, "autorange": False}
    figure["layout"]["yaxis"] = {"title": y_title, "autorange": False}

    if x_logscale:
        figure["layout"]["xaxis"]["type"] = "log"
    if y_logscale:
        figure["layout"]["yaxis"]["type"] = "log"

    return figure


def set_3daxes(
    figure,
    x_title=None,
    y_title=None,
    z_title=None,
    x_logscale=False,
    y_logscale=False,
    z_logscale=False,
):
    """Sets 3D axes"""

    figure["layout"]["scene"] = {}
    figure["layout"]["scene"]["xaxis"] = {"title": x_title, "autorange": False}
    figure["layout"]["scene"]["yaxis"] = {"title": y_title, "autorange": False}
    figure["layout"]["scene"]["zaxis"] = {"title": z_title, "autorange": False}

    if x_logscale:
        figure["layout"]["scene"]["xaxis"]["type"] = "log"
    if y_logscale:
        figure["layout"]["scene"]["yaxis"]["type"] = "log"
    if z_logscale:
        figure["layout"]["scene"]["zaxis"]["type"] = "log"

    return figure


def add_slider(figure, slider_scale):
    """Adds slider for animation"""

    figure["layout"]["sliders"] = {
        "args": ["slider.value", {"duration": 400, "ease": "cubic-in-out"}],
        "initialValue": min(slider_scale),
        "plotlycommand": "animate",
        "values": slider_scale,
        "visible": True,
    }

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

    return sliders_dict


def add_slider_steps(sliders_dict, year):
    """Adds the slider steps."""

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
    sliders_dict["steps"].append(slider_step)


def add_button(figure):
    """Adds the pause-play button for animation"""

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


def set_range(values, logscale=False):
    """Finds the axis range for the figure."""

    if logscale:
        rmin = min(np.log10(values)) * 0.97
        rmax = max(np.log10(values)) * 1.04
    else:
        rmin = min(values) * 0.7
        rmax = max(values) * 1.4

    return [rmin, rmax]


def get_trace(
    grid,
    col_name_template,
    x_column,
    y_column,
    bubble_column,
    z_column=None,
    size_column=None,
    sizeref=200000,
    scale_bubble=1,
    marker_opacity=None,
    marker_border_width=None,
    color_column=None,
    colorscale=None,
    show_colorbar=True,
    colorbar_title=None,
    category=None,
):
    """Makes the trace for the data as a dictionary object that can be added to the figure or time frames."""

    trace = {
        "x": grid.loc[
            grid["key"] == col_name_template.format(x_column, category), "value"
        ].values[0],
        "y": grid.loc[
            grid["key"] == col_name_template.format(y_column, category), "value"
        ].values[0],
        "text": grid.loc[
            grid["key"] == col_name_template.format(bubble_column, category), "value"
        ].values[0],
        "mode": "markers",
    }

    if z_column:
        trace["z"] = grid.loc[
            grid["key"] == col_name_template.format(z_column, category), "value"
        ].values[0]

    if size_column:
        trace["marker"] = {
            "sizemode": "area",
            "sizeref": sizeref,
            "size": grid.loc[
                grid["key"] == col_name_template.format(size_column, category), "value"
            ].values[0],
        }
    else:
        trace["marker"] = {
            "size": 10 * scale_bubble,
        }

    if marker_opacity:
        trace["marker"]["opacity"] = marker_opacity

    if marker_border_width:
        trace["marker"]["line"] = {"width": marker_border_width}

    if color_column:
        trace["marker"]["color"] = grid.loc[
            grid["key"] == col_name_template.format(color_column), "value"
        ].values[0]
        trace["marker"]["colorbar"] = {"title": colorbar_title}
        trace["marker"]["colorscale"] = colorscale

    if category:
        trace["name"] = category

    return trace
