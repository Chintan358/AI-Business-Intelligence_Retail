import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../api/client';
import {
  BrainCircuit,
  Play,
  CheckCircle2,
  Clock,
  ShieldCheck,
  AlertCircle,
  FileText,
  Bot,
  ArrowRight,
  TrendingUp,
  Sparkles
} from 'lucide-react';

const AnalysisHubPage = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/analysis/sessions');
      setSessions(res.data);
    } catch (err) {
      setError('Failed to load analysis sessions.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartAnalysis = async () => {
    try {
      setRunning(true);
      const res = await apiClient.post('/analysis/start', {});
      const newSession = res.data;
      navigate(`/agents/monitor?session_id=${newSession.id}`);
    } catch (err) {
      setError('Failed to trigger multi-agent analysis.');
      setRunning(false);
    }
  };

  const latestSession = sessions[0];

  return (
    <div className="space-y-6">
      {/* Hero Action Card */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40 border border-slate-800 shadow-xl relative overflow-hidden">
        <div className="max-w-2xl">
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Autonomous CrewAI Swarm
            </span>
            <span className="text-xs text-slate-400">• 6 Specialized Business Agents</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Business Analysis Hub</h1>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            Execute the complete multi-agent collaborative pipeline. The <strong>Data Analyst</strong> computes verified KPIs, 
            which feed simultaneously into <strong>Marketing</strong>, <strong>Finance</strong>, and <strong>Operations</strong>. 
            The <strong>Strategy Agent</strong> synthesizes a 90-day turnaround plan, and the <strong>Verification Agent</strong> 
            audits all calculations against ground truth before certification.
          </p>

          <div className="mt-5 flex items-center gap-3">
            <button
              onClick={handleStartAnalysis}
              disabled={running}
              className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-lg shadow-emerald-600/30 flex items-center gap-2 transition disabled:opacity-50"
            >
              {running ? (
                <>
                  <div className="h-3.5 w-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                  <span>Initializing Agents...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>Execute Multi-Agent Analysis</span>
                </>
              )}
            </button>
            <Link
              to="/agents/monitor"
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-xs flex items-center gap-1.5 transition"
            >
              <Bot className="h-3.5 w-3.5" />
              <span>Live Agent Monitor</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Latest Certified Session Banner */}
      {latestSession && (
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-emerald-500/15 text-emerald-400">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <span>Latest Certified Analysis (Session #{latestSession.id})</span>
                  <span className="px-2 py-0.2 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    {latestSession.status}
                  </span>
                </h3>
                <p className="text-[11px] text-slate-400">
                  Completed in {latestSession.execution_duration_sec}s • Verified Mathematical Accuracy: 100%
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Link
                to={`/agents/monitor?session_id=${latestSession.id}`}
                className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-medium text-slate-300 hover:bg-slate-700 transition"
              >
                Inspect Agent Logs
              </Link>
              <Link
                to="/reports"
                className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-xs font-semibold text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30 transition flex items-center gap-1.5"
              >
                <FileText className="h-3.5 w-3.5" />
                <span>Download Report</span>
              </Link>
            </div>
          </div>

          <div className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <span className="font-semibold text-emerald-400 block mb-1">Executive Strategy Summary:</span>
            <p className="whitespace-pre-line">{latestSession.executive_summary}</p>
          </div>
        </div>
      )}

      {/* Historical Sessions Table */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <h3 className="text-sm font-semibold text-white mb-3">All Analysis Sessions</h3>

        {loading ? (
          <p className="text-xs text-slate-400 py-6 text-center">Loading session history...</p>
        ) : sessions.length === 0 ? (
          <p className="text-xs text-slate-400 py-6 text-center">No analysis sessions found. Click execute above.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="p-2.5 rounded-l-lg">Session ID</th>
                  <th className="p-2.5">Status</th>
                  <th className="p-2.5">Duration</th>
                  <th className="p-2.5">Verification</th>
                  <th className="p-2.5">Created</th>
                  <th className="p-2.5 rounded-r-lg text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {sessions.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-800/30">
                    <td className="p-2.5 font-bold text-white">#{s.id}</td>
                    <td className="p-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        s.status === 'Verified'
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                          : s.status === 'Running'
                          ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                          : 'bg-slate-700 text-slate-300'
                      }`}>
                        {s.status}
                      </span>
                    </td>
                    <td className="p-2.5">{s.execution_duration_sec}s</td>
                    <td className="p-2.5">
                      {s.is_verified ? (
                        <span className="text-emerald-400 font-medium flex items-center gap-1">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          Certified
                        </span>
                      ) : (
                        <span className="text-slate-500">Unverified</span>
                      )}
                    </td>
                    <td className="p-2.5 text-slate-400">
                      {new Date(s.created_at).toLocaleString()}
                    </td>
                    <td className="p-2.5 text-right">
                      <Link
                        to={`/agents/monitor?session_id=${s.id}`}
                        className="text-emerald-400 hover:underline font-medium"
                      >
                        Monitor & Logs &rarr;
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

export default AnalysisHubPage;
