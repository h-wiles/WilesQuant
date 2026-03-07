from langchain_core.tools import tool
from typing import Annotated
from wiles_agents.dataflows.interface import route_to_vendor

@tool
def get_social(
    ticker: Annotated[str, "Ticker symbol"],
    curr_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"] = 7,
) -> str:
    """
    Retrieve social media posts and public sentiment data for a given ticker symbol.
    Uses the configured social_data vendor.
    Args:
        ticker (str): Ticker symbol
        curr_date (str): Current date in yyyy-mm-dd format
        look_back_days (int): Number of days to look back (default 7)
    Returns:
        str: A formatted string containing social media posts, discussions, and sentiment data
    """
    return route_to_vendor("get_social", ticker, curr_date, look_back_days)