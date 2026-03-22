import { useState, useEffect } from "react";
import ReactECharts from "echarts-for-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LineChart, BarChart2, BrainCircuit, FileText } from "lucide-react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "github-markdown-css/github-markdown.css";


const Header = ({ code, setCode, setPage }) => {

  const [updateInfo, setUpdateInfo] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [open, setOpen] = useState(false);

  const updateData = async () => {

    if (!code) {
      alert("请输入股票代码");
      return;
    }

    setUpdating(true);

    try {

      const res = await fetch(
        `http://127.0.0.1:8000/api/get_data_day?code=${code}`
      );

      if (!res.ok) {
        throw new Error(`HTTP错误 ${res.status}`);
      }

      const json = await res.json();

      setUpdateInfo(json);
      setOpen(true);   // 打开弹窗

    } catch (err) {

      setUpdateInfo({
        message: "更新失败",
        error: err.message
      });

      setOpen(true);

    } finally {

      setUpdating(false);

    }

  };

  return (
    <div className="text-center mb-8">

      <h1 className="text-4xl font-bold mb-3">
        AI 股票分析平台 v1.0
      </h1>

      <p className="text-gray-500">
        输入股票代码，选择你想要的分析方式（开始分析前建议先更新数据）
      </p>

      <div className="flex justify-center gap-3 mt-6">

        <Input
          placeholder="例如：sh.600004"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="max-w-xs"
        />

        <Button onClick={() => setPage("menu")}>
          开始分析
        </Button>

        <Button
          variant="outline"
          onClick={updateData}
          disabled={updating}
        >
          {updating ? "更新中..." : "更新数据"}
        </Button>

      </div>

      {/* ⭐ 自定义弹窗 */}
      {open && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">

          <div className="bg-white rounded-xl shadow-xl w-96 p-6">

            <h2 className="text-xl font-bold mb-4">
              📦 数据更新结果
            </h2>

            {updateInfo && (

              <div className="space-y-2 text-sm">

                {updateInfo.code && (
                  <p>
                    <span className="text-gray-500">股票代码：</span>
                    {updateInfo.code}
                  </p>
                )}

                <p>
                  <span className="text-gray-500">更新信息：</span>
                  {updateInfo.message}
                </p>

                {updateInfo.start_date && updateInfo.end_date && (
                  <p>
                    <span className="text-gray-500">数据区间：</span>
                    {updateInfo.start_date} ~ {updateInfo.end_date}
                  </p>
                )}

                {updateInfo.error && (
                  <p className="text-red-500">
                    错误：{updateInfo.error}
                  </p>
                )}

              </div>

            )}

            <div className="flex justify-end mt-6">

              <Button onClick={() => setOpen(false)}>
                关闭
              </Button>

            </div>

          </div>

        </div>
      )}

    </div>
  );
};


export default function StockDashboard() {
  const [code, setCode] = useState("");
  const [page, setPage] = useState(null);

  // ===== 策略状态 =====

  const OptionCard = ({ title, icon: Icon, value, desc }) => (
    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }}>
      <Card
        className="cursor-pointer shadow-lg hover:shadow-2xl transition-all rounded-2xl"
        onClick={() => setPage(value)}
      >
        <CardContent className="p-6 flex flex-col items-center gap-4">
          <Icon size={40} />
          <h2 className="text-xl font-semibold">{title}</h2>
          <p className="text-sm text-gray-500 text-center">{desc}</p>
        </CardContent>
      </Card>
    </motion.div>
  );

  const BackBtn = () => (
    <Button variant="outline" className="mb-6" onClick={() => setPage("menu")}>
      返回
    </Button>
  );

  /* ===================== K线页面 ===================== */
  const KLinePage = () => {
    const [kdata, setKdata] = useState([]);

    useEffect(() => {
      const fetchData = async () => {
        try {
          const res = await fetch(
            `http://127.0.0.1:8000/api/price?code=${code}`
          );
          let data = await res.json();
          if (!Array.isArray(data)) data = [data];
          setKdata(data);
        } catch (err) {
          console.error("获取行情失败:", err);
        }
      };
      fetchData();
    }, [code]);

    function formatVol(v) {
      if (v > 1e8) return (v / 1e8).toFixed(2) + " 亿";
      if (v > 1e4) return (v / 1e4).toFixed(2) + " 万";
      return v;
    }

    const buildOption = () => {
      if (!kdata.length) return {};

      const dates = kdata.map(i => i.date);
      const kValues = kdata.map(i => [i.open, i.close, i.low, i.high]);
      const volumes = kdata.map(i => i.volume);

      return {
        animation: false,
        animationDuration: 0,
        animationDurationUpdate: 0,

        tooltip: {
          trigger: "axis",
          triggerOn: "mousemove|click",
          transitionDuration: 0,
          enterable: false,
          confine: true,
          axisPointer: {
            type: "cross",
            animation: false
          },

          formatter: function (params) {
            const k = params[0];                 // K线
            const v = k.data;
            const idx = k.dataIndex;             // ⭐ 当前索引
            const volume = formatVol(kdata[idx].volume);

            return `
              <b>${k.axisValue}</b><br/>
              开盘：${v[1].toFixed(2)}<br/>
              收盘：${v[2].toFixed(2)}<br/>
              最低：${v[3].toFixed(2)}<br/>
              最高：${v[4].toFixed(2)}<br/>
              <span style="color:#888">成交量：${volume}</span>
            `;
          }
        },

        // ⭐ 鼠标十字线
        axisPointer: {
          link: [{ xAxisIndex: "all" }],
          label: { backgroundColor: "#777" }
        },

        // ⭐ 两个图布局
        grid: [
          { left: "8%", right: "5%", height: "55%" },
          { left: "8%", right: "5%", top: "72%", height: "18%" }
        ],

        xAxis: [
          {
            type: "category",
            data: dates,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false }
          },
          {
            type: "category",
            gridIndex: 1,
            data: dates,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false }
          }
        ],

        yAxis: [
          // 主图（K线）
          {
            scale: true,
            splitArea: { show: true }
          },

          // ⭐ 成交量副图（隐藏Y轴）
          {
            gridIndex: 1,
            splitNumber: 2,
            axisLabel: { show: false },   // 隐藏数字
            axisTick: { show: false },    // 隐藏刻度
            axisLine: { show: false },    // 隐藏轴线
            splitLine: { show: false }    // 隐藏网格线
          }
        ],


        // ⭐⭐⭐ 核心：缩放 + 滑动
        dataZoom: [
          {
            type: "inside",
            xAxisIndex: [0, 1],
            start: 70,
            end: 100,
            throttle: 50   // ⭐ 拖动节流（关键）
          },
          {
            show: true,
            type: "slider",
            xAxisIndex: [0, 1],
            bottom: 10,
            start: 70,
            end: 100,
            throttle: 50
          }
        ],


        series: [
          {
            name: "K线",
            type: "candlestick",
            data: kValues,
            large: true,          // ⭐ 大数据模式
            largeThreshold: 200   // 超过200根K线自动优化
          },

          {
            name: "Volume",
            type: "bar",
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: volumes,
            large: true,
            silent: true,        // ⭐ 核心！鼠标忽略成交量
            tooltip: { show: false }  // ⭐ 不参与 tooltip
          }
        ]
      };
    };

    return (
      <div>
        <BackBtn />
        <Card className="p-8 shadow-xl rounded-2xl">
          <h2 className="text-2xl font-bold mb-4">📈 {code} K线图</h2>

          {kdata.length === 0 ? (
            <div className="h-72 flex items-center justify-center text-gray-400">
              正在加载行情数据...
            </div>
          ) : (
            <ReactECharts option={buildOption()} style={{ height: 420 }} />
          )}
        </Card>
      </div>
    );
  };

  /* ===================== 量化策略界面 ===================== */
  const StrategyPage = () => {

    const [data, setData] = useState([]);
    const [entryStrategy, setEntryStrategy] = useState("ma5_diverge");
    const [exitStrategy, setExitStrategy] = useState("fix_tp_sl");
    const [loading, setLoading] = useState(false);

    /* ================= 入场策略 ================= */
    const entryStrategies = [
      {
        value: "ma5_diverge",
        name: "MA5 乖离策略",
        desc: "价格偏离并小于5日均线5%"
      },
      {
        value: "kdj_oversold",
        name: "KDJ 超卖策略",
        desc: "J < 0 时寻找反弹机会"
      },
      {
        value: "macd_golden_cross",
        name: "MACD 金叉",
        desc: "趋势启动信号，适合波段"
      },
      {
        value: "macd_bullish_divergence",
        name: "MACD 底背离",
        desc: "价格创新低但动能减弱"
      },
      {
        value: "volume_breakout",
        name: "放量突破",
        desc: "成交量放大突破关键位"
      }
    ];

    /* ================= 出场策略 ================= */
    const exitStrategies = [
      {
        value: "fix_tp_sl",
        name: "2%止盈 + 1%止损",
        desc: "固定比例止盈止损"
      },
      {
        value: "fix_hold_days",
        name: "固定持股天数3",
        desc: "固定持股天数后出场"
      },
      {
        value: "kdj_overbuy",
        name: "kdj超买(J>80)",
        desc: "kdj超买(J>80)出场"
      }
    ];

    /* ================= 拉取回测数据 ================= */
    const fetchBacktest = async () => {
      setLoading(true);

      const res = await fetch(
        `http://127.0.0.1:8000/api/backtest?code=${code}&entry_strategy=${entryStrategy}&exit_strategy=${exitStrategy}`
      );

      const json = await res.json();
      setData(json);
      setLoading(false);
    };

    useEffect(() => {
      if (code) fetchBacktest();
    }, [entryStrategy, exitStrategy]);

    /* ================= 数据转换 ================= */

    const dates = data.map(d => d.date);
    const klineData = data.map(d => [d.open, d.close, d.low, d.high]);
    const equity = data.map(d => d.equity);

    const maxDD = equity.length ? calcMaxDrawdown(equity) : 0;
    const sharpe = equity.length ? calcSharpeRatio(equity) : 0;
    const totalReturn = equity.length ? calcTotalReturn(equity) : 0;
    const cumReturns = equity.length ? calcCumReturn(equity) : [];

    const buyPoints = data
      .map((d, i) => (d.signal === 1 ? [i, d.close] : null))
      .filter(Boolean);

    const sellPoints = data
      .map((d, i) => (d.signal === -1 ? [i, d.close] : null))
      .filter(Boolean);

    /* ================= K线图 ================= */

    const klineOption = {
      tooltip: { trigger: "axis" },
      dataZoom: [
        { type: "inside", start: 70, end: 100 },
        { show: true, type: "slider", start: 70, end: 100 }
      ],
      xAxis: { type: "category", data: dates },
      yAxis: { scale: true },
      series: [
        {
          type: "candlestick",
          data: klineData
        },
        {
          name: "Buy",
          type: "scatter",
          data: buyPoints,
          symbol: "triangle",
          symbolSize: 18,
          itemStyle: { color: "#16a34a" }
        },
        {
          name: "Sell",
          type: "scatter",
          data: sellPoints,
          symbol: "triangle",
          symbolRotate: 180,
          symbolSize: 18,
          itemStyle: { color: "#dc2626" }
        }
      ]
    };

    /* ================= 收益曲线 ================= */

    const equityOption = {
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: dates },
      yAxis: { type: "value" },
      series: [
        {
          name: "策略资金曲线",
          type: "line",
          smooth: true,
          data: equity
        }
      ]
    };

    const returnOption = {
      tooltip: {
        trigger: "axis",
        formatter: (params) => {
          const v = params[0].value;
          return `${params[0].axisValue}<br/>收益率：${v.toFixed(2)}%`;
        }
      },
      xAxis: { type: "category", data: dates },
      yAxis: {
        type: "value",
        axisLabel: {
          formatter: "{value}%"
        }
      },
      series: [
        {
          name: "累计收益率",
          type: "line",
          smooth: true,
          data: cumReturns
        }
      ]
    };

    function calcMaxDrawdown(equity) {
      let peak = equity[0];
      let maxDD = 0;

      for (let i = 0; i < equity.length; i++) {
        if (equity[i] > peak) peak = equity[i];
        const drawdown = (peak - equity[i]) / peak;
        if (drawdown > maxDD) maxDD = drawdown;
      }

      return maxDD;
    }

    function calcDailyReturns(equity) {
      let returns = [];
      for (let i = 1; i < equity.length; i++) {
        returns.push((equity[i] - equity[i-1]) / equity[i-1]);
      }
      return returns;
    }

    function calcSharpeRatio(equity) {
      const returns = calcDailyReturns(equity);
      const mean = returns.reduce((a,b)=>a+b,0) / returns.length;

      const std = Math.sqrt(
        returns.map(r => (r - mean) ** 2).reduce((a,b)=>a+b,0) / returns.length
      );

      const sharpe = (mean / std) * Math.sqrt(252);
      return sharpe;
    }

    function calcTotalReturn(equity) {
      return (equity[equity.length-1] / equity[0]) - 1;
    }

    function calcCumReturn(equity) {
      const base = equity[0];
      return equity.map(v => (v / base - 1) * 100);
    }


    /* ================= UI ================= */
    return (
      <div>
        <BackBtn />

        <Card className="p-6 mb-6 shadow-xl rounded-2xl">

          <h2 className="text-2xl font-bold mb-6">⚙️ 策略选择</h2>

          {/* ===== 入场策略 ===== */}
          <h3 className="text-xl font-semibold mb-4">📥 选择入场策略</h3>
          <div className="grid grid-cols-5 gap-4 mb-8">
            {entryStrategies.map((s) => (
              <Card
                key={s.value}
                onClick={() => setEntryStrategy(s.value)}
                className={`cursor-pointer p-4 border-2 transition-all 
                ${entryStrategy === s.value ? "border-blue-500 shadow-xl" : ""}`}
              >
                <h3 className="font-semibold">{s.name}</h3>
                <p className="text-xs text-gray-500 mt-2">{s.desc}</p>
              </Card>
            ))}
          </div>

          {/* ===== 出场策略 ===== */}
          <h3 className="text-xl font-semibold mb-4">📤 选择出场策略</h3>
          <div className="grid grid-cols-5 gap-4 mb-8">
            {exitStrategies.map((s) => (
              <Card
                key={s.value}
                onClick={() => setExitStrategy(s.value)}
                className={`cursor-pointer p-4 border-2 transition-all 
                ${exitStrategy === s.value ? "border-blue-500 shadow-xl" : ""}`}
              >
                <h3 className="font-semibold">{s.name}</h3>
                <p className="text-xs text-gray-500 mt-2">{s.desc}</p>
              </Card>
            ))}
          </div>

          <div className="flex gap-4 items-center">
            <Button onClick={fetchBacktest}>
              运行回测
            </Button>
            {loading && <span>回测中...</span>}
          </div>
          <p className="text-sm text-gray-500 mt-4">
            注：本页面入场价格与出场价格均为当日收盘价，仅用于策略回测示例。
          </p>

        </Card>

        {/* ===== K线图 ===== */}
        <Card className="p-6 mb-6 shadow-xl rounded-2xl">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-6">
            📈 买卖点回测

            <span className="flex items-center gap-2 text-sm text-gray-600">
              <span className="text-green-600 text-lg">▲</span> 买入
            </span>

            <span className="flex items-center gap-2 text-sm text-gray-600">
              <span className="text-red-600 text-lg">▼</span> 卖出
            </span>
          </h2>
          <ReactECharts option={klineOption} style={{ height: 400 }} />
        </Card>

        {/* ===== 收益曲线 ===== */}
        <Card className="p-6 shadow-xl rounded-2xl">
          <h2 className="text-xl font-bold mb-4">💰 策略资金曲线(初始资金10000)</h2>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <Card className="p-4 text-center">
              <p className="text-gray-500 text-sm">总收益率</p>
              <p className="text-2xl font-bold">
                {(totalReturn * 100).toFixed(2)}%
              </p>
            </Card>

            <Card className="p-4 text-center">
              <p className="text-gray-500 text-sm">最大回撤</p>
              <p className="text-2xl font-bold text-red-500">
                {(maxDD * 100).toFixed(2)}%
              </p>
            </Card>

            <Card className="p-4 text-center">
              <p className="text-gray-500 text-sm">夏普比率</p>
              <p className="text-2xl font-bold text-green-600">
                {sharpe.toFixed(2)}
              </p>
            </Card>
          </div>

          <ReactECharts option={equityOption} style={{ height: 350 }} />
        </Card>

        {/* ===== 收益率曲线 ===== */}
        <Card className="p-6 mt-6 shadow-xl rounded-2xl">

          <h2 className="text-xl font-bold mb-4">
            📊 累计收益率曲线
          </h2>

          <ReactECharts
            option={returnOption}
            style={{ height: 350 }}
          />

        </Card>

      </div>
    );
  };


  /* ===================== AI分析界面 ===================== */
  const AIPage = () => {

    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [seconds, setSeconds] = useState(0);   // 👈 新增
    const [error, setError] = useState(null);

    const [open, setOpen] = useState({
      fundamentals: true,
      technical: false,
      news: false,
      plan: false,
      decision: true
    });

    const [tradeDate, setTradeDate] = useState("");

    const toggle = (key) => {
      setOpen(prev => ({
        ...prev,
        [key]: !prev[key]
      }));
    };

    /* ================= 获取AI分析 ================= */

    const fetchAIAnalysis = async () => {
        if (!tradeDate) {
          setError("请先选择交易日期");
          return;
        }
      setSeconds(0);
      setLoading(true);
      setError(null);     // 清空旧错误
      setAnalysis(null);

      try {
        const res = await fetch(
          `http://127.0.0.1:8000/api/ai_analysis?code=${code}&trade_date=${tradeDate}`
        );
        if (!res.ok) {
          throw new Error(`服务器错误: ${res.status}`);
        }
        const json = await res.json();
        if (json.error) {
          throw new Error(json.error);
        }
        setAnalysis(json);
      } catch (err) {
        setError(err.message || "AI分析失败");
      } finally {
        setLoading(false);
      }
    };



    useEffect(() => {
      if (!loading) return;
      const timer = setInterval(() => {
        setSeconds((prev) => prev + 1);
      }, 1000);
      return () => clearInterval(timer);
    }, [loading]);

    if (error) {
      return (
        <div>
          <BackBtn />
          <Card className="p-8 shadow-xl rounded-2xl border-red-500 border-2">
            <p className="text-lg font-bold text-red-600">AI分析失败</p>
            <p className="text-gray-600 mt-2">{error}</p>

            <button
              onClick={fetchAIAnalysis}
              className="mt-4 bg-red-500 text-white px-4 py-2 rounded-lg"
            >
              重新尝试
            </button>
          </Card>
        </div>
      );
    }

    if (loading) {
      return (
        <div>
          <BackBtn />
          <Card className="p-8 shadow-xl rounded-2xl">
            <p className="text-lg font-medium">AI分析生成中(预计时间7min)...</p>
            <p className="text-gray-500 mt-2">
              已等待 {seconds} 秒
            </p>
          </Card>
        </div>
      );
    }

    if (!analysis) {
      return (
        <div>
          <BackBtn />
          <Card className="p-8 shadow-xl rounded-2xl">
            <h2 className="text-2xl font-bold mb-4">
              🤖 AI 智能分析
            </h2>

            <p className="text-gray-500 mb-6">
              请选择交易日期并点击分析按钮
            </p>

            <div className="flex items-center gap-4">
              <label className="font-medium">交易日期：</label>
              <input
                type="date"
                value={tradeDate}
                onChange={(e) => setTradeDate(e.target.value)}
                className="border rounded-lg px-3 py-2"
              />

              <button
                onClick={fetchAIAnalysis}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
              >
                开始分析
              </button>
            </div>
          </Card>
        </div>
      );
    }

    const modules = [
      {
        key: "fundamentals",
        title: "📊 基本面分析",
        content: analysis.fundamentals_report
      },
      {
        key: "technical",
        title: "📈 技术面分析",
        content: analysis.market_report
      },
      {
        key: "news",
        title: "📰 新闻消息面",
        content: analysis.news_report
      },
      {
        key: "plan",
        title: "📑 交易计划",
        content: analysis.trader_investment_plan
      },
      {
        key: "decision",
        title: "🎯 最终决策",
        content: analysis.final_trade_decision
      }
    ];

    return (
      <div>
        <BackBtn />
        {/* 标题 */}
        <Card className="p-8 mb-6 shadow-xl rounded-2xl">
          <h2 className="text-2xl font-bold mb-2">
            🤖 AI 智能分析
            <span className="ml-3 text-blue-600">
              {analysis.code} {analysis.stock_name}
            </span>
          </h2>
          <p className="text-gray-600 mb-4">
            本页面底层架构基于开源项目TradingAgents(https://github.com/TauricResearch/TradingAgents)扩展开发而成，内容由 AI 基于公开信息自动生成，仅供参考，不构成任何投资建议或买卖推荐。
            AI 分析可能存在误差或信息滞后，请投资者结合自身情况独立判断并自行承担投资风险。市场有风险，投资需谨慎。
          </p>
          {/* 日期输入 */}
          <div className="flex items-center gap-4">
            <label className="font-medium">交易日期：</label>
            <input
              type="date"
              value={tradeDate}
              onChange={(e) => setTradeDate(e.target.value)}
              className="border rounded-lg px-3 py-2"
            />
            <button
              onClick={fetchAIAnalysis}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
            >
              重新分析
            </button>
          </div>
        </Card>

        {/* 模块 */}
        <div className="grid grid-cols-1 gap-6">

          {modules.map((m) => (

            <Card
              key={m.key}
              className={`shadow-lg rounded-2xl ${
                m.key === "decision" ? "border-2 border-blue-500" : ""
              }`}
            >

              <div
                className="flex justify-between items-center p-6 cursor-pointer"
                onClick={() => toggle(m.key)}
              >
                <h3 className="text-xl font-bold">{m.title}</h3>

                <span className="text-gray-500 text-lg">
                  {open[m.key] ? "▲" : "▼"}
                </span>
              </div>

              {open[m.key] && (

                <div className="p-6 pt-0">

                  <div className="markdown-body bg-white rounded-xl p-4">

                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {m.content || ""}
                    </ReactMarkdown>

                  </div>

                </div>

              )}

            </Card>

          ))}

        </div>

      </div>
    );
  };


  /* ===================== 财报分析界面 ===================== */
  const ReportPage = () => (
    <div>
      <BackBtn />
      <Card className="p-8 shadow-xl rounded-2xl">
        <h2 className="text-2xl font-bold mb-4">📑 财报分析</h2>
        <p className="text-gray-600">未来接入真实财报</p>
      </Card>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50  to-slate-200 p-10">
      <div className="max-w-5xl mx-auto">
        <Header code={code} setCode={setCode} setPage={setPage} />

        {page === "menu" && (
          <div className="grid grid-cols-4 gap-6">
            <OptionCard title="K线图" value="kline" icon={LineChart} desc="查看行情" />
            <OptionCard title="量化策略" value="strategy" icon={BarChart2} desc="策略回测" />
            <OptionCard title="AI分析" value="ai" icon={BrainCircuit} desc="muti-agents建议" />
            <OptionCard title="财报分析" value="report" icon={FileText} desc="基本面" />
          </div>
        )}

        {page === "kline" && <KLinePage />}
        {page === "strategy" && <StrategyPage />}
        {page === "ai" && <AIPage />}
        {page === "report" && <ReportPage />}
      </div>
    </div>
  );
}