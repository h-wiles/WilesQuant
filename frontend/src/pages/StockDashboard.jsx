import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LineChart, BarChart2, BrainCircuit } from "lucide-react";
import { motion } from "framer-motion";

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

  const Header = () => (
    <div className="text-center mb-8">
      <h1 className="text-4xl font-bold mb-3">AI 股票分析平台</h1>
      <p className="text-gray-500">输入股票代码，选择你想要的分析方式</p>
      <div className="flex justify-center gap-3 mt-6">
        <Input
          placeholder="例如：AAPL / 600519"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="max-w-xs"
        />
        <Button onClick={() => setPage("menu")}>开始分析</Button>
      </div>
    </div>
  );

  const BackBtn = () => (
    <Button variant="outline" className="mb-6" onClick={() => setPage("menu")}>返回</Button>
  );

  const KLinePage = () => (
    <div>
      <BackBtn />
      <Card className="p-8 shadow-xl rounded-2xl">
        <h2 className="text-2xl font-bold mb-4">📈 {code} K线图</h2>
        <div className="h-72 flex items-center justify-center text-gray-400">
          这里接入K线图组件 (TradingView / ECharts)
        </div>
      </Card>
    </div>
  );

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
        <div className="h-64 mt-6 flex items-center justify-center text-gray-400">
          回测收益曲线图位置
        </div>
      </Card>
    </div>
  );

  const AIPage = () => (
    <div>
      <BackBtn />
      <Card className="p-8 shadow-xl rounded-2xl">
        <h2 className="text-2xl font-bold mb-4">🤖 AI 智能分析</h2>
        <div className="space-y-4 text-gray-600">
          <p>📌 趋势判断：中期上涨趋势</p>
          <p>📌 风险提示：短期可能震荡</p>
          <p>📌 AI建议：逢回调分批买入</p>
        </div>
      </Card>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200 p-10">
      <div className="max-w-5xl mx-auto">
        <Header />

        {page === "menu" && (
          <div className="grid grid-cols-3 gap-6">
            <OptionCard
              title="K线图"
              value="kline"
              icon={LineChart}
              desc="查看实时与历史行情走势"
            />
            <OptionCard
              title="量化策略"
              value="strategy"
              icon={BarChart2}
              desc="策略回测与收益分析"
            />
            <OptionCard
              title="AI分析"
              value="ai"
              icon={BrainCircuit}
              desc="AI 自动生成投资建议"
            />
          </div>
        )}

        {page === "kline" && <KLinePage />}
        {page === "strategy" && <StrategyPage />}
        {page === "ai" && <AIPage />}
      </div>
    </div>
  );
}
