import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import apiClient from '../api/client';
import {
  Bot,
  Clock,
  CheckCircle2,
  AlertCircle,
  Terminal,
  ShieldCheck,
  ChevronDown,
  ChevronRight,
  Sparkles,
  RefreshCw
} from 'lucide-react';

const AgentMonitorPage = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [logs, setLogs] = useState([]);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchSessionAndLogs();
    const interval = setInterval(() => {
      fetchSessionAndLogs(true);
    }, 3000);
    return () => clearInterval(interval);
  }, [sessionId]);

  const fetchSessionAndLogs = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      let targetId = sessionId;

      // If no session_id in query params, get the latest session
      if (!targetId) {
        const sRes = await apiClient.get('/analysis/sessions');
        if (sRes.data.length > 0) {
          targetId = sRes.data[0].id;
        }
      }

      if (targetId) {
        const [sessionRes, logsRes] = await Promise.all([
          apiClient.get(`/analysis/sessions/${targetId}`),
          apiClient.get(`/analysis/sessions/${targetId}/logs`)
        ]);
        setSession(sessionRes.data);
        setLogs(logsRes.data);
        if (logsRes.data.length > 0 && expandedId === null) {
          setExpandedId(logsRes.data[logsRes.data.length - 1].id);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const getAgentColor = (name) => {
    if (name.includes('Data Analyst')) return 'border-blue-500/40 text-blue-400 bg-blue-500/10';
    if (name.includes('Marketing')) return 'border-purple-500/40 text-purple-400 bg-purple-500/10';
    if (name.includes('Finance')) return 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10';
    if (name.includes('Operations')) return 'border-amber-500/40 text-amber-400 bg-amber-500/10';
    if (name.includes('Strategy')) return 'border-indigo-500/40 text-indigo-400 bg-indigo-500/10';
    if (name.includes('Verification')) return 'border-rose-500/40 text-rose-400 bg-rose-500/10';
    return 'border-slate-700 text-slate-300 bg-slate-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Live Telemetry
            </span>
            <span className="text-xs text-slate-400">
              Session #{session ? session.id : '...'} • Status: <strong className="text-white">{session?.status || 'Active'}</strong>
            </span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">Agent Execution & Progress Monitor</h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchSessionAndLogs(false)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-medium text-slate-300 hover:bg-slate-700 flex items-center gap-1.5 transition"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Refresh</span>
          </button>
          <Link
            to="/approvals"
            className="px-3.5 py-1.5 rounded-lg bg-emerald-600 text-xs font-semibold text-white hover:bg-emerald-500 transition"
          >
            View Proposals &rarr;
          </Link>
        </div>
      </div>

      {/* Progress Cards */}
      {loading && logs.length === 0 ? (
        <div className="p-8 text-center text-xs text-slate-400">Loading agent telemetry...</div>
      ) : logs.length === 0 ? (
        <div className="p-8 text-center text-xs text-slate-400 bg-slate-900 rounded-xl border border-slate-800">
          No agent execution logs found. Please start an analysis session from the{' '}
          <Link to="/analysis" className="text-emerald-400 underline">
            Analysis Hub
          </Link>.
        </div>
      ) : (
        <div className="space-y-3.5">
          {logs.map((log, index) => {
            const isExpanded = expandedId === log.id;
            const colorClass = getAgentColor(log.agent_name);

            return (
              <div
                key={log.id}
                className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden shadow-sm transition-all"
              >
                {/* Agent Card Header */}
                <div
                  onClick={() => setExpandedId(isExpanded ? null : log.id)}
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-800/40 select-none"
                >
                  <div className="flex items-center space-x-3.5">
                    <div className="h-7 w-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300">
                      {index + 1}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-white">{log.agent_name}</span>
                        <span className={`px-2 py-0.2 rounded text-[10px] font-semibold border ${colorClass}`}>
                          {log.agent_role}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">Task: {log.task_name}</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-1.5 text-xs text-slate-400">
                      <Clock className="h-3.5 w-3.5" />
                      <span>{log.execution_duration_sec}s</span>
                    </div>

                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-semibold flex items-center gap-1.5 ${
                        log.status === 'Completed'
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                          : log.status === 'Running'
                          ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30 animate-pulse'
                          : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                      }`}
                    >
                      {log.status === 'Completed' && <CheckCircle2 className="h-3.5 w-3.5" />}
                      <span>{log.status}</span>
                    </span>

                    {isExpanded ? (
                      <ChevronDown className="h-4 w-4 text-slate-400" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-slate-400" />
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="border-t border-slate-800/80 bg-slate-950/70 p-5 space-y-4">
                    {/* Output Text */}
                    <div>
                      <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 mb-2">
                        <Terminal className="h-3.5 w-3.5 text-emerald-400" />
                        <span>Agent Reasoning & Findings:</span>
                      </div>
                      <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-line">
                        {log.output_text || 'No output text recorded.'}
                      </div>
                    </div>

                    {/* Structured Data */}
                    {log.structured_data && Object.keys(log.structured_data).length > 0 && (
                      <div>
                        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                          Structured Telemetry Payload:
                        </span>
                        <pre className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] text-slate-400 font-mono overflow-x-auto max-h-56">
                          {JSON.stringify(log.structured_data, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AgentMonitorPage;
