import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../api/client';
import { ArrowLeft, CheckCircle2, AlertTriangle, ShieldCheck, FileCheck2, TrendingUp } from 'lucide-react';

const RecommendationDetailsPage = () => {
  const { id } = useParams();
  const [rec, setRec] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecDetails();
  }, [id]);

  const fetchRecDetails = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/approvals/all');
      const target = res.data.find((item) => item.recommendation?.id === parseInt(id));
      if (target) {
        setRec(target);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading recommendation details...</div>;
  }

  if (!rec) {
    return (
      <div className="p-8 text-center text-xs text-rose-400">
        Recommendation not found. <Link to="/approvals" className="underline">Back to Approvals</Link>
      </div>
    );
  }

  const recommendation = rec.recommendation;

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <Link to="/approvals" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white">
        <ArrowLeft className="h-4 w-4" />
        <span>Back to Approval Center</span>
      </Link>

      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5 shadow-xl">
        <div className="flex items-center justify-between gap-2 pb-3 border-b border-slate-800">
          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
            {recommendation.category}
          </span>
          <span className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${
            rec.decision === 'Approved' ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' :
            rec.decision === 'Rejected' ? 'bg-rose-500/15 text-rose-400 border-rose-500/30' :
            'bg-amber-500/15 text-amber-400 border-amber-500/30'
          }`}>
            {rec.decision}
          </span>
        </div>

        <h1 className="text-lg font-bold text-white">{recommendation.title}</h1>
        <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">{recommendation.description}</p>

        <div className="grid grid-cols-2 gap-3 p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs">
          <div>
            <span className="text-slate-500 block text-[11px]">Expected ROI</span>
            <strong className="text-emerald-400 font-semibold">{recommendation.expected_roi || 'N/A'}</strong>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px]">Risk Rating</span>
            <strong className="text-amber-400 font-semibold">{recommendation.risk_level}</strong>
          </div>
        </div>

        {recommendation.supporting_evidence && (
          <div>
            <h3 className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
              Supporting Empirical Evidence
            </h3>
            <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-400 font-mono overflow-x-auto">
              {JSON.stringify(recommendation.supporting_evidence, null, 2)}
            </pre>
          </div>
        )}

        {rec.manager_comments && (
          <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700 text-xs text-slate-200">
            <span className="text-slate-400 font-bold block text-[10px] uppercase">Manager Decision Comments:</span>
            <p className="mt-1">"{rec.manager_comments}"</p>
            <span className="block text-[10px] text-slate-500 mt-2">
              Decision Date: {new Date(rec.decision_date).toLocaleString()}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationDetailsPage;
