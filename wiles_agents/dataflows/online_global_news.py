import json
from .alpha_vantage_common import _make_api_request, format_datetime_for_api


def get_global_news(curr_date, look_back_days: int = 7, limit: int = 50):
    """Returns global market news & sentiment data without ticker-specific filtering.

    Covers broad market topics like financial markets, economy, and more.

    Args:
        curr_date: Current date in yyyy-mm-dd format.
        look_back_days: Number of days to look back (default 7).
        limit: Maximum number of articles (default 50).

    Returns:
        Dictionary containing global news sentiment data or JSON string.
    """
    from datetime import datetime, timedelta

    # Calculate start date
    curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    start_dt = curr_dt - timedelta(days=look_back_days)
    start_date = start_dt.strftime("%Y-%m-%d")

    params = {
        "topics": "financial_markets,economy_macro,economy_monetary",
        "time_from": format_datetime_for_api(start_date),
        "time_to": format_datetime_for_api(curr_date),
        "limit": str(limit),
    }

    news = _make_api_request("NEWS_SENTIMENT", params)
    feeds = json.loads(news)["feed"]
    result = [{k: d[k] for k in ["title", "url", "time_published", "summary"]} for d in feeds]

    return str(result)
