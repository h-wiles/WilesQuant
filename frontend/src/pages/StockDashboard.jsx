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
              formatter: function (params) {
                const k = params[0];
                const v = k.data;
                return `
                  ${k.axisValue}<br/>
                  开: ${v[1].toFixed(2)}<br/>
                  收: ${v[2].toFixed(2)}<br/>
                  低: ${v[3].toFixed(2)}<br/>
                  高: ${v[4].toFixed(2)}
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
            large: true
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

  /* ===================== 其他页面保持不变 ===================== */

  const StrategyPage = () => (
    <div>
      <BackBtn />
      <Card className="p-8 shadow-xl rounded-2xl">
        <h2 className="text-2xl font-bold mb-4">📊 量化策略回测</h2>
        <div className="grid grid-cols-3 gap-4">
          <Card className="p-4">收益率: 35%</Card>
          <Card className="p-4">最大回撤: 8%</Card>
          <Card className="p-4">胜率: 62%</Card>
        </div>
      </Card>
    </div>
  );

  const AIPage = () => (
    <div>
      <BackBtn />
      <Card className="p-8 shadow-xl rounded-2xl">
        <h2 className="text-2xl font-bold mb-4">🤖 AI 智能分析</h2>
        <p className="text-gray-600">AI 自动生成投资建议</p>
      </Card>
    </div>
  );

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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200 p-10">
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
