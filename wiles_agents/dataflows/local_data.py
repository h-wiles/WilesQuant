from typing import Annotated
import pandas as pd


def get_local_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    # read in data
    data = pd.read_csv(f"./data/price_data/{symbol}.csv")[["date", "open", "high", "low", "close", "volume"]]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["date"] >= start_date) & (data["date"] <= end_date)
    ]

    # remove the index from the dataframe
    filtered_data = filtered_data.reset_index(drop=True)

    return filtered_data.to_csv(index=False)


