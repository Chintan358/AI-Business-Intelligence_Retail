import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { ShieldAlert, Database, Server, Cpu, FileText, CheckCircle2 } from 'lucide-react';

const AdminOverviewPage = () => {
  const [telemetry, setTelemetry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTelemetry();
  }, []);

  const fetchTelemetry = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/admin/overview');
      setTelemetry(res.data);
    } catch (err) {
      setError('Access restricted to administrators.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading system telemetry...</div>;
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
        {error}
      </div>
    );
  }

  const statCards = [
    { label: 'Registered Users', value: telemetry?.users_count, icon: Cpu },
    { label: 'Customer Accounts', value: telemetry?.customers_count, icon: Database },
    { label: 'Product Catalog SKUs', value: telemetry?.products_count, icon: Database },
    { label: 'Point-of-Sale Transactions', value: telemetry?.transactions_count, icon: Database },
    { label: 'Transaction Items', value: telemetry?.transaction_items_count, icon: Database },
    { label: 'Inventory Movement Logs', value: telemetry?.inventory_movements_count, icon: Server },
    { label: 'Operating Expense Vouchers', value: telemetry?.expenses_count, icon: Server },
    { label: 'Multi-Agent Sessions Run', value: telemetry?.analysis_sessions_count, icon: Cpu },
    { label: 'Agent Execution Logs', value: telemetry?.agent_logs_count, icon: Cpu },
    { label: 'Approval Governance Requests', value: telemetry?.approval_requests_count, icon: ShieldAlert },
    { label: 'Generated PDF Reports', value: telemetry?.reports_count, icon: FileText },
  ];

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            System Telemetry
          </span>
          <span className="text-xs text-slate-400">• Database & Agent Infrastructure</span>
        </div>
        <h1 className="text-xl font-bold text-white tracking-tight">Admin Telemetry & System Health</h1>
        <p className="text-xs text-slate-400 mt-1">Live database table row counts, execution metrics, and infrastructure health.</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {statCards.map((c, idx) => {
          const Icon = c.icon;
          return (
            <div key={idx} className="p-4 rounded-2xl bg-slate-900 border border-slate-800">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-xs">{c.label}</span>
                <Icon className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="text-xl font-bold text-white">{c.value?.toLocaleString() || 0}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AdminOverviewPage;
