import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import {
  FileCheck2,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  User,
  ShieldCheck,
  TrendingUp,
  MessageSquare
} from 'lucide-react';

const ApprovalsPage = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReq, setSelectedReq] = useState(null);
  const [decisionType, setDecisionType] = useState('Approved');
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [filter, setFilter] = useState('All'); // All, Pending, Approved, Rejected

  useEffect(() => {
    fetchApprovals();
  }, []);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/approvals/all');
      setRequests(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const openDecisionModal = (req, type) => {
    setSelectedReq(req);
    setDecisionType(type);
    setComments('');
  };

  const handleDecisionSubmit = async (e) => {
    e.preventDefault();
    if (!selectedReq) return;
    setSubmitting(true);
    try {
      await apiClient.post(`/approvals/${selectedReq.id}/decision`, {
        decision: decisionType,
        manager_comments: comments
      });
      setSelectedReq(null);
      fetchApprovals();
    } catch (err) {
      alert('Failed to submit approval decision: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const filteredRequests = requests.filter((r) => {
    if (filter === 'All') return true;
    return r.decision === filter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Human-in-the-Loop Governance
            </span>
            <span className="text-xs text-slate-400">• Executive Sign-off Required</span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">Recommendation & Approval Center</h1>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1.5 p-1 bg-slate-950 border border-slate-800 rounded-xl text-xs">
          {['All', 'Pending', 'Approved', 'Rejected'].map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-3 py-1 rounded-lg font-medium transition ${
                filter === tab ? 'bg-slate-800 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Requests Grid */}
      {loading ? (
        <div className="p-8 text-center text-xs text-slate-400">Loading approval queue...</div>
      ) : filteredRequests.length === 0 ? (
        <div className="p-10 text-center text-xs text-slate-400 bg-slate-900 rounded-2xl border border-slate-800">
          No approval requests match the selected filter.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredRequests.map((req) => {
            const rec = req.recommendation;
            const isPending = req.decision === 'Pending';

            return (
              <div
                key={req.id}
                className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between space-y-4 hover:border-slate-700 transition"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      {rec?.category || 'Strategic'}
                    </span>
                    <span
                      className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${
                        req.decision === 'Approved'
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                          : req.decision === 'Rejected'
                          ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                          : 'bg-amber-500/15 text-amber-400 border-amber-500/30 animate-pulse'
                      }`}
                    >
                      {req.decision}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white mb-1.5">{rec?.title}</h3>
                  <p className="text-xs text-slate-300 leading-relaxed mb-3">{rec?.description}</p>

                  <div className="grid grid-cols-2 gap-2 p-2.5 rounded-lg bg-slate-950/70 border border-slate-800/80 text-[11px]">
                    <div>
                      <span className="text-slate-500 block">Expected ROI / Impact</span>
                      <strong className="text-emerald-400 font-medium">{rec?.expected_roi || 'N/A'}</strong>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Risk Rating</span>
                      <strong className="text-amber-400 font-medium">{rec?.risk_level || 'Medium'}</strong>
                    </div>
                  </div>

                  {req.manager_comments && (
                    <div className="mt-3 p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/60 text-xs text-slate-300">
                      <strong className="text-slate-400 block text-[10px] uppercase font-bold">Manager Rationale:</strong>
                      "{req.manager_comments}"
                      <span className="block text-[10px] text-slate-500 mt-1">
                        Decided on {new Date(req.decision_date).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {/* Actions */}
                {isPending ? (
                  <div className="flex items-center gap-2 pt-3 border-t border-slate-800">
                    <button
                      onClick={() => openDecisionModal(req, 'Approved')}
                      className="flex-1 py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-emerald-600/20 transition"
                    >
                      <CheckCircle className="h-4 w-4" />
                      <span>Approve Proposal</span>
                    </button>
                    <button
                      onClick={() => openDecisionModal(req, 'Rejected')}
                      className="flex-1 py-2 px-3 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 font-semibold text-xs flex items-center justify-center gap-1.5 transition"
                    >
                      <XCircle className="h-4 w-4" />
                      <span>Reject</span>
                    </button>
                  </div>
                ) : (
                  <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-800 flex items-center gap-1">
                    <ShieldCheck className="h-3.5 w-3.5 text-slate-400" />
                    <span>Decision recorded in immutable audit log</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Decision Modal */}
      {selectedReq && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl relative">
            <h2 className="text-base font-bold text-white mb-1">
              Confirm {decisionType === 'Approved' ? 'Approval' : 'Rejection'}
            </h2>
            <p className="text-xs text-slate-400 mb-4">{selectedReq.recommendation?.title}</p>

            <form onSubmit={handleDecisionSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Manager Rationale & Audit Comments <span className="text-rose-400">*</span>
                </label>
                <textarea
                  required
                  rows={4}
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  placeholder="Enter authorized manager notes, rollout schedule, or reasons for rejection..."
                  className="w-full p-3 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedReq(null)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !comments.trim()}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold text-white shadow-lg transition ${
                    decisionType === 'Approved'
                      ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/30'
                      : 'bg-rose-600 hover:bg-rose-500 shadow-rose-600/30'
                  } disabled:opacity-50`}
                >
                  {submitting ? 'Recording...' : `Confirm ${decisionType}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApprovalsPage;
