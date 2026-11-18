import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { Layers, Database, Calendar, CheckCircle2, Clock } from 'lucide-react';

const DatasetHistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/datasets/history');
      setHistory(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            Audit Trail
          </span>
          <span className="text-xs text-slate-400">• Dataset Ingestion History</span>
        </div>
        <h1 className="text-xl font-bold text-white tracking-tight">Dataset Processing History</h1>
        <p className="text-xs text-slate-400 mt-1">Audit log of all uploaded files, record counts, and ingestion statuses.</p>
      </div>

      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading history logs...</div>
        ) : history.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">No upload history records found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-2.5 rounded-l-lg">ID</th>
                  <th className="p-2.5">File Name</th>
                  <th className="p-2.5">File Size</th>
                  <th className="p-2.5">Total Records</th>
                  <th className="p-2.5">Status</th>
                  <th className="p-2.5 rounded-r-lg">Ingested Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {history.map((h) => (
                  <tr key={h.id} className="hover:bg-slate-800/30">
                    <td className="p-2.5 font-bold text-white">#{h.id}</td>
                    <td className="p-2.5 font-semibold text-emerald-400">{h.filename}</td>
                    <td className="p-2.5">{(h.file_size_bytes / 1024).toFixed(1)} KB</td>
                    <td className="p-2.5">{h.total_records?.toLocaleString() || '-'}</td>
                    <td className="p-2.5">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                        {h.status}
                      </span>
                    </td>
                    <td className="p-2.5 text-slate-400">
                      {new Date(h.created_at).toLocaleString()}
                    </td>
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

export default DatasetHistoryPage;
