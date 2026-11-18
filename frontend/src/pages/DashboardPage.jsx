import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import {
  TrendingUp,
  TrendingDown,
  ShoppingBag,
  DollarSign,
  PackageX,
  Users,
  AlertTriangle,
  BrainCircuit,
  ArrowUpRight,
  RotateCcw,
  Store,
  FileText
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';

const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/analytics/dashboard-payload');
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load live dashboard analytics.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center space-y-3">
          <div className="h-10 w-10 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400 font-medium">Computing deterministic retail analytics...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm">
        <p className="font-semibold mb-1">Failed to load dashboard data</p>
        <p className="text-xs text-rose-400">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="mt-4 px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-medium text-white hover:bg-slate-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const { kpis, monthly, categories, channels, stores, stockout_alerts } = data;

  // Formatting helpers
  const formatINR = (val) =>
    new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);

  const statusPieData = [
    { name: 'Completed', value: kpis.completed_orders, color: '#10B981' },
    { name: 'Returned', value: kpis.returned_orders, color: '#F59E0B' },
    { name: 'Cancelled', value: kpis.cancelled_orders, color: '#EF4444' }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800/80 border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Live Production BI
            </span>
            <span className="text-xs text-slate-400">• Retail Sales & Inventory Intelligence</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Executive Operations Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">
            Empirical calculations across 2,500 transactions, 1,200 customers, and 300 products (May 1 – Oct 31, 2026).
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            to="/chat"
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            Ask AI Assistant
          </Link>
          <Link
            to="/analysis"
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/25 flex items-center gap-1.5 transition"
          >
            <BrainCircuit className="h-4 w-4" />
            <span>Run 6-Agent AI</span>
          </Link>
        </div>
      </div>

      {/* Critical Business Alert Banner */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/25 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5 text-amber-200">
          <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0" />
          <span>
            <strong>Operational Attention Required:</strong> 50.24% of placed orders are leaked due to returns (₹54.54M) and cancellations (₹51.35M), resulting in a net operating loss of <strong>-₹3.92M</strong>. 
          </span>
        </div>
        <Link
          to="/approvals"
          className="text-amber-300 hover:text-white font-semibold underline shrink-0"
        >
          Review Turnaround Proposals &rarr;
        </Link>
      </div>

      {/* KPI Cards Grid (4 columns) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Net Revenue */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 relative overflow-hidden shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Completed Net Revenue</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <DollarSign className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">{formatINR(kpis.net_revenue)}</div>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-emerald-400 font-medium">
            <TrendingUp className="h-3 w-3" />
            <span>₹{kpis.gross_revenue.toLocaleString()} Gross (-₹{kpis.discount_amount.toLocaleString()} Disct)</span>
          </div>
        </div>

        {/* Gross Profit & Margin */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 relative overflow-hidden shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Gross Profit & Margin</span>
            <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">{formatINR(kpis.gross_profit)}</div>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-teal-400 font-medium">
            <span>{kpis.gross_profit_margin_pct}% Gross Margin (COGS: {formatINR(kpis.cogs)})</span>
          </div>
        </div>

        {/* Operating Profit */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 relative overflow-hidden shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Operating Profit (EBIT)</span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <TrendingDown className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-rose-400 tracking-tight">
            -{formatINR(Math.abs(kpis.net_operating_profit))}
          </div>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-slate-400 font-medium">
            <span>OpEx: {formatINR(kpis.total_operating_expenses)} ({kpis.operating_margin_pct}% margin)</span>
          </div>
        </div>

        {/* Completed Orders & AOV */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 relative overflow-hidden shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Completed Orders & AOV</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <ShoppingBag className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">{kpis.completed_orders.toLocaleString()}</div>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-indigo-300 font-medium">
            <span>AOV: {formatINR(kpis.aov)} ({kpis.total_units_sold.toLocaleString()} units sold)</span>
          </div>
        </div>
      </div>

      {/* Secondary KPI Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 block mb-0.5">Order Completion Rate</span>
          <span className="text-lg font-bold text-emerald-400">{kpis.order_completion_rate_pct}%</span>
          <span className="text-[10px] text-slate-500 block">1,244 of 2,500 total orders</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 block mb-0.5">Return Rate (Leakage)</span>
          <span className="text-lg font-bold text-amber-400">{kpis.order_return_rate_pct}%</span>
          <span className="text-[10px] text-slate-500 block">645 orders ({formatINR(kpis.returned_revenue_lost)})</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 block mb-0.5">Repeat Customer Rate</span>
          <span className="text-lg font-bold text-teal-400">{kpis.repeat_purchase_rate_pct}%</span>
          <span className="text-[10px] text-slate-500 block">341 repeat / 739 active</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 block mb-0.5">Stockout Risk SKUs</span>
          <span className="text-lg font-bold text-rose-400">{kpis.stockout_risk_count} SKUs</span>
          <span className="text-[10px] text-slate-500 block">Operating at/below reorder level</span>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monthly Revenue vs OpEx (2 cols) */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Monthly Net Revenue vs Operating Expenses</h3>
              <p className="text-xs text-slate-400">May 2026 – October 2026 Trajectory (₹ in Millions)</p>
            </div>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              September Dip (-14%) / October (+22%)
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthly} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="colorExp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="month" stroke="#64748B" fontSize={11} />
                <YAxis
                  stroke="#64748B"
                  fontSize={11}
                  tickFormatter={(v) => `₹${(v / 1000000).toFixed(1)}M`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px' }}
                  formatter={(val) => [formatINR(val)]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="net_revenue" name="Net Revenue" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#colorRev)" />
                <Area type="monotone" dataKey="operating_expenses" name="Store Expenses" stroke="#EF4444" strokeWidth={2} fillOpacity={1} fill="url(#colorExp)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Order Status Distribution (1 col) */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Fulfillment Status Distribution</h3>
            <p className="text-xs text-slate-400">Total 2,500 transactions placed</p>
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {statusPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-800 text-xs">
            {statusPieData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-slate-300">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span>{item.name}</span>
                </div>
                <span className="font-semibold">{item.value.toLocaleString()} ({((item.value / 2500) * 100).toFixed(1)}%)</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Category Breakdown & Channel Returns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Performance */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Merchandise Department Mix</h3>
              <p className="text-xs text-slate-400">Net Revenue & Gross Profit Margin %</p>
            </div>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categories} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="category" stroke="#64748B" fontSize={11} />
                <YAxis
                  stroke="#64748B"
                  fontSize={11}
                  tickFormatter={(v) => `₹${(v / 1000000).toFixed(0)}M`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px' }}
                  formatter={(val, name) => [formatINR(val), name]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="total_revenue" name="Revenue" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="gross_profit" name="Gross Profit" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Channel Returns */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Omnichannel Fulfillment & Return Rate</h3>
              <p className="text-xs text-slate-400">Online & Mobile App suffer from elevated returns</p>
            </div>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={channels} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="channel" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px' }}
                  formatter={(val) => [`${val}%`, 'Rate']}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="completion_rate_pct" name="Completion Rate %" fill="#10B981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="return_rate_pct" name="Return Rate %" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                <Bar dataKey="cancellation_rate_pct" name="Cancellation Rate %" fill="#EF4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Section: Top Stockout Risks & Store P&L */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stockout Hazards */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-white">Priority Inventory Stockout Hazards</h3>
              <p className="text-xs text-slate-400">Current stock below safety reorder level</p>
            </div>
            <Link to="/datasets/preview" className="text-xs text-emerald-400 hover:underline">
              View All &rarr;
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-2.5 rounded-l-lg">SKU / Product</th>
                  <th className="p-2.5">Category</th>
                  <th className="p-2.5">Current</th>
                  <th className="p-2.5">Reorder</th>
                  <th className="p-2.5 rounded-r-lg text-right">Deficit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {stockout_alerts.map((item) => (
                  <tr key={item.product_id} className="hover:bg-slate-800/30">
                    <td className="p-2.5">
                      <span className="font-semibold text-white block truncate max-w-[150px]">{item.product_name}</span>
                      <span className="text-[10px] text-slate-500">{item.product_id}</span>
                    </td>
                    <td className="p-2.5 text-slate-400">{item.category}</td>
                    <td className="p-2.5 font-bold text-rose-400">{item.current_stock}</td>
                    <td className="p-2.5 text-slate-400">{item.reorder_level}</td>
                    <td className="p-2.5 text-right font-bold text-amber-400">+{item.deficit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Store Contribution Margins */}
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-white">Store Branch Contribution Margins</h3>
              <p className="text-xs text-slate-400">Net Revenue vs Operating Expenses by store</p>
            </div>
            <Link to="/reports" className="text-xs text-emerald-400 hover:underline">
              P&L Reports &rarr;
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-2.5 rounded-l-lg">Store ID</th>
                  <th className="p-2.5">Revenue</th>
                  <th className="p-2.5">Gross Profit</th>
                  <th className="p-2.5">OpEx</th>
                  <th className="p-2.5 rounded-r-lg text-right">EBIT</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {stores.map((s) => (
                  <tr key={s.store_id} className="hover:bg-slate-800/30">
                    <td className="p-2.5 font-bold text-white flex items-center gap-1.5">
                      <Store className="h-3.5 w-3.5 text-slate-500" />
                      <span>{s.store_id}</span>
                    </td>
                    <td className="p-2.5">{formatINR(s.net_revenue)}</td>
                    <td className="p-2.5 text-teal-400">{formatINR(s.gross_profit)}</td>
                    <td className="p-2.5 text-slate-400">{formatINR(s.operating_expenses)}</td>
                    <td className={`p-2.5 text-right font-semibold ${s.net_operating_profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {formatINR(s.net_operating_profit)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
