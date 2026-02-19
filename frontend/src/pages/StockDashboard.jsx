import { useState, useEffect } from "react";
import ReactECharts from "echarts-for-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LineChart, BarChart2, BrainCircuit, FileText } from "lucide-react";
import { motion } from "framer-motion";

const Header = ({ code, setCode, setPage }) => (
  <div className="text-center mb-8">
    <h1 className="text-4xl font-bold mb-3">AI 股票分析平台</h1>
    <p className="text-gray-500">输入股票代码，选择你想要的分析方式</p>

    <div className="flex justify-center gap-3 mt-6">
      <Input
        placeholder="例如：sh.600004"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        className="max-w-xs"
      />
      <Button onClick={() => setPage("menu")}>开始分析</Button>
    </div>
  </div>
);


export default function StockDashboard() {
  const [code, setCode] = useState("");
  const [page, setPage] = useState(null);

  // ===== 策略状态 =====
  const [strategy, setStrategy] = useState("ma");
  const [params, setParams] = useState({
    short: 5,
    long: 20,
  });


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
    const [strategy, setStrategy] = useState("ma");
    const [loading, setLoading] = useState(false);
    const strategies = [
      {
        value: "ma5_diverge",
        name: "MA5 乖离策略",
        desc: "价格远离均线后回归，适合震荡行情"
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


    /* ================= 拉取回测数据 ================= */
    const fetchBacktest = async () => {
      setLoading(true);
      const res = await fetch(`http://127.0.0.1:8000/api/backtest?code=${code}&strategy=${strategy}`);
      const json = await res.json();
      setData(json);
      setLoading(false);
    };

    useEffect(() => {
      if (code) fetchBacktest();
    }, [strategy]);

    /* ================= 数据转换 ================= */

    const dates = data.map(d => d.date);

    const klineData = data.map(d => [d.open, d.close, d.low, d.high]);
    const equity = data.map(d => d.equity);
    const maxDD = equity.length ? calcMaxDrawdown(equity) : 0;
    const sharpe = equity.length ? calcSharpeRatio(equity) : 0;
    const totalReturn = equity.length ? calcTotalReturn(equity) : 0;


    const buyPoints = data
      .map((d, i) => (d.signal === 1 ? [i, d.low] : null))
      .filter(Boolean);

    const sellPoints = data
      .map((d, i) => (d.signal === -1 ? [i, d.high] : null))
      .filter(Boolean);

    /* ================= K线图 + 买卖点 ================= */

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




    /* ================= UI ================= */

    return (
      <div>
        <BackBtn />

        {/* ===== ① 策略选择区 ===== */}
        <Card className="p-6 mb-6 shadow-xl rounded-2xl">
          <h2 className="text-2xl font-bold mb-4">⚙️ 策略选择</h2>

          <div className="flex gap-4 items-center">
            <Card className="p-6 mb-6 shadow-xl rounded-2xl">
              <h2 className="text-2xl font-bold mb-4">⚙️ 选择回测策略</h2>

              <div className="grid grid-cols-5 gap-4">
                {strategies.map((s) => (
                  <Card
                    key={s.value}
                    onClick={() => setStrategy(s.value)}
                    className={`cursor-pointer p-4 border-2 transition-all 
                    ${strategy === s.value ? "border-blue-500 shadow-xl" : ""}`}
                  >
                    <h3 className="font-semibold">{s.name}</h3>
                    <p className="text-xs text-gray-500 mt-2">{s.desc}</p>
                  </Card>
                ))}
              </div>

              <div className="mt-6 flex gap-4 items-center">
                <Button onClick={fetchBacktest}>
                  运行回测
                </Button>
                {loading && <span>回测中...</span>}
              </div>
            </Card>

          </div>

          <p className="text-gray-500 mt-4">
            策略说明：当产生买卖信号时在K线图中显示 ▲ ▼
          </p>
        </Card>

        {/* ===== ② K线图 ===== */}
        <Card className="p-6 mb-6 shadow-xl rounded-2xl">
          <h2 className="text-xl font-bold mb-4">📈 买卖点回测</h2>
          <ReactECharts option={klineOption} style={{ height: 400 }} />
        </Card>

        {/* ===== ③ 收益曲线 ===== */}
        <Card className="p-6 shadow-xl rounded-2xl">
          <h2 className="text-xl font-bold mb-4">💰 策略收益曲线(初始资金10000)</h2>

          {/* 指标卡片 */}
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

      </div>
    );
  };


  /* ===================== AI分析界面 ===================== */
  const AIPage = () => (
    <div>
      <BackBtn />
      <Card className="p-8 shadow-xl rounded-2xl">
        <h2 className="text-2xl font-bold mb-4">🤖 AI 智能分析</h2>
        <p className="text-gray-600">AI 自动生成投资建议</p>
      </Card>
    </div>
  );

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
            <OptionCard title="AI分析" value="ai" icon={BrainCircuit} desc="AI建议" />
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