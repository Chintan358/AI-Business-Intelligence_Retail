import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { TableProperties, Database, Filter, RefreshCw } from 'lucide-react';

const DataPreviewPage = () => {
  const [selectedTable, setSelectedTable] = useState('transactions');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const tables = [
    { key: 'transactions', label: 'Transactions (2,500)' },
    { key: 'transaction_items', label: 'Transaction Items (6,269)' },
    { key: 'products', label: 'Products (300)' },
    { key: 'customers', label: 'Customers (1,200)' },
    { key: 'inventory_movements', label: 'Inventory Movements (1,800)' },
    { key: 'expenses', label: 'Expenses (600)' }
  ];

  useEffect(() => {
    fetchTableData();
  }, [selectedTable]);

  const fetchTableData = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get(`/datasets/preview?table=${selectedTable}&limit=50`);
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Database Inspector
            </span>
            <span className="text-xs text-slate-400">• Raw PostgreSQL Records</span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">Dataset Record Preview</h1>
        </div>

        <button
          onClick={fetchTableData}
          className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-medium text-slate-300 hover:bg-slate-700 flex items-center gap-1.5 self-start sm:self-auto"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Refresh Records</span>
        </button>
      </div>

      {/* Table Selector Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1">
        {tables.map((t) => (
          <button
            key={t.key}
            onClick={() => setSelectedTable(t.key)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition ${
              selectedTable === t.key
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Records Table */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="flex items-center justify-between mb-3 text-xs text-slate-400">
          <span>
            Viewing sample of first <strong>50 rows</strong> from table: <code className="text-emerald-400">{selectedTable}</code>
          </span>
          <span className="text-[11px] text-slate-500">Grounded in PostgreSQL</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Querying database records...</div>
        ) : !data || data.data.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">No records found.</div>
        ) : (
          <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-800 text-slate-300 uppercase text-[10px] tracking-wider sticky top-0 z-10">
                <tr>
                  {Object.keys(data.data[0]).map((col) => (
                    <th key={col} className="p-2.5 whitespace-nowrap border-b border-slate-700">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {data.data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    {Object.values(row).map((val, cIdx) => (
                      <td key={cIdx} className="p-2.5 whitespace-nowrap max-w-[200px] truncate">
                        {val !== null && val !== undefined ? String(val) : <span className="text-slate-600">NULL</span>}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataPreviewPage;
