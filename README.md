# WilesQuant：Quant Trading System📈
A full-stack quantitative trading project that provides strategy research, backtesting, and visualization.
The backend focuses on strategy implementation and backtesting, while the frontend provides interactive K-line charts and trading results visualization.

## ✨ Features
### Backend (Python / FastAPI)
* Historical price data management
* Technical indicators:
  * MA / MACD / KDJ
  * Volume–price analysis

* Entry strategies:
  * MACD divergence
  * KDJ oversold entry
  * Volume–price breakout

* Risk control:
  * Stop loss (configurable)
  * Take profit (configurable)
  *  Slippage support

* Backtesting engine:
  * Initial capital simulation
  * Trade execution by signals
  * Equity curve generation
  * Performance metrics output

* REST API for frontend visualization

### Frontend (JavaScript + React（JSX）)

* Interactive candlestick (K-line) chart
* Volume histogram separated from price chart
* Crosshair + tooltip (OHLC + volume)
* Dynamic stock code loading
* Strategy result visualization (equity curve, signals)

## 🏗 Project Structure
```text
├── api
│   └── price_api.py
├── backtest
│   ├── backtest.py
│   └── get_entry_point.py
├── data
│   ├── price_data
│   │   ├── sh.600000.csv
│   │   └── sh.600004.csv
│   ├── results
│   │   ├── ma5_diverge_test.json
│   │   └── ma5_diverge.json
│   └── stock_info.csv
├── frontend
│   └── kline.html
├── jobs
│   ├── get_data_day.py
│   └── run_daily_strategy.py
├── logs
│   └── get_data.log
├── main.py
├── README.md
├── requirements.txt
├── temp.py
└── utils
    └── MyUtils.py
```

## 🚀 Getting Started
```text
cd WilesQuant
python -m uvicorn main:app --reload     # 启动后端API

cd frontend
npm run dev     # 启动前端api
```

## 📝 notion
```text
申请域名后将main.py中的allow_origins改成域名
```