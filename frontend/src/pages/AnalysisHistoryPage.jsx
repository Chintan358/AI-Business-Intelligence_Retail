import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { History, BrainCircuit, CheckCircle2, Clock, FileText } from 'lucide-react';

const AnalysisHistoryPage = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/analysis/sessions');
      setSessions(res.data);
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
            Audit Archive
          </span>
          <span className="text-xs text-slate-400">• Multi-Agent Session History</span>
        </div>
        <h1 className="text-xl font-bold text-white tracking-tight">Analysis History & Historical Logs</h1>
        <p className="text-xs text-slate-400 mt-1">Review historical multi-agent execution runs, verification scores, and executive summaries.</p>
      </div>

      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading analysis history...</div>
        ) : sessions.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">No previous sessions found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-2.5 rounded-l-lg">Session ID</th>
                  <th className="p-2.5">Status</th>
                  <th className="p-2.5">Verification</th>
                  <th className="p-2.5">Duration</th>
                  <th className="p-2.5">Date Executed</th>
                  <th className="p-2.5 rounded-r-lg text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {sessions.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-800/30">
                    <td className="p-2.5 font-bold text-white">#{s.id}</td>
                    <td className="p-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        s.status === 'Verified' ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' :
                        s.status === 'Running' ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30' :
                        'bg-slate-700 text-slate-300'
                      }`}>
                        {s.status}
                      </span>
                    </td>
                    <td className="p-2.5">
                      {s.is_verified ? (
                        <span className="text-emerald-400 font-medium flex items-center gap-1">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          Certified 100%
                        </span>
                      ) : (
                        <span className="text-slate-500">Uncertified</span>
                      )}
                    </td>
                    <td className="p-2.5">{s.execution_duration_sec}s</td>
                    <td className="p-2.5 text-slate-400">{new Date(s.created_at).toLocaleString()}</td>
                    <td className="p-2.5 text-right space-x-2">
                      <Link
                        to={`/agents/monitor?session_id=${s.id}`}
                        className="text-emerald-400 hover:underline font-semibold"
                      >
                        Inspect Logs
                      </Link>
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

export default AnalysisHistoryPage;
