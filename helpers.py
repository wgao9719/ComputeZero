import requests

from flask import redirect, render_template, session
from functools import wraps

import plotly.graph_objects as go

def login_required(f):
    """
    Decorate routes to require login. Detects if user is logged in by checking for user_id in current session.
    If no user_id is found, user is reidrected to login page.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Redirect to login page if no session id is found
        if session.get("user_id") is None:
            return redirect("/login")
        # Else, continue to intended page
        return f(*args, **kwargs)

    return decorated_function

def create_stacked_bar_chart(bar_chart_info):
    """
    Creates a stacked bar chart comparing prices from three cloud providers. Takes in a list containing
    data about the cloud providers and different pricing costs and returns an HTML represenation of an
    interactive stacked bar chart (to be embedded into an HTML webpage).
    """
    # Read provider names and costs from bar_chart_info
    providers = bar_chart_info[0]
    compute_cost = bar_chart_info[1]
    storage_cost = bar_chart_info[2]
    data_transfer_cost = bar_chart_info[3]

    # Create chart object with three price categories
    chart = go.Figure(data=[
            #Each go.Bar adds one price category (or one stack) to the chart
            go.Bar(
                name='Compute',
                x=providers,
                y=compute_cost,
                # Add interactivity (hover text)
                hovertemplate='Compute<br>Cost: $%{y}<extra></extra>'
            ),
            go.Bar(
                name='Storage',
                x=providers,
                y=storage_cost,
                hovertemplate='Storage<br>Cost: $%{y}<extra></extra>'
            ),
            go.Bar(
                name='Data Transfer',
                x=providers,
                y=data_transfer_cost,
                hovertemplate='Data Transfer<br>Cost: $%{y}<extra></extra>'
            )])

    # Update layout to stacked bar chart and add titles for the graph and two axes
    chart.update_layout(barmode = "stack",
                      title = "Provider Price Comparison Chart",
                      xaxis_title = "Providers",
                      yaxis_title = "Prices ($)")

    #Return HTMl representation of chart
    return chart.to_html(full_html=False)
