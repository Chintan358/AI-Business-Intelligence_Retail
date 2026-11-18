import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import {
  FileText,
  Download,
  PlusCircle,
  Eye,
  CheckCircle2,
  Calendar,
  Layers,
  Sparkles
} from 'lucide-react';

const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/reports');
      setReports(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInstant = async () => {
    try {
      setGenerating(true);
      // Fetch latest session to generate report for
      const sRes = await apiClient.get('/analysis/sessions');
      if (sRes.data.length === 0) {
        alert('Please run an analysis session first before generating a report.');
        return;
      }
      const latestId = sRes.data[0].id;
      await apiClient.post(`/reports/generate-instant/${latestId}`);
      fetchReports();
    } catch (err) {
      alert('Failed to generate instant report.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Download Center
            </span>
            <span className="text-xs text-slate-400">• Publication-Quality Vector PDFs</span>
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">Business Intelligence Reports</h1>
        </div>

        <button
          onClick={handleGenerateInstant}
          disabled={generating}
          className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-lg shadow-emerald-600/20 flex items-center gap-2 transition disabled:opacity-50"
        >
          {generating ? (
            <span>Compiling PDF...</span>
          ) : (
            <>
              <PlusCircle className="h-4 w-4" />
              <span>Generate On-Demand PDF</span>
            </>
          )}
        </button>
      </div>

      {/* Reports Grid */}
      {loading ? (
        <div className="p-8 text-center text-xs text-slate-400">Loading reports directory...</div>
      ) : reports.length === 0 ? (
        <div className="p-10 text-center text-xs text-slate-400 bg-slate-900 rounded-2xl border border-slate-800">
          No generated reports found. Click "Generate On-Demand PDF" above.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((rep) => (
            <div
              key={rep.id}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-4"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {rep.report_type} Report
                  </span>
                  <span className="text-[10px] text-slate-500">
                    {(rep.file_size_bytes / 1024).toFixed(1)} KB
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white mb-1 leading-snug">{rep.title}</h3>
                <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-2">
                  <Calendar className="h-3.5 w-3.5 text-slate-500" />
                  <span>Coverage: May 1, 2026 – Oct 31, 2026</span>
                </p>
                <p className="text-[11px] text-slate-500 mt-1">
                  Generated: {new Date(rep.created_at).toLocaleString()}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
                <Link
                  to={`/reports/${rep.id}`}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 flex items-center gap-1.5 transition"
                >
                  <Eye className="h-3.5 w-3.5" />
                  <span>View Details</span>
                </Link>

                <a
                  href={`/api/v1/reports/${rep.id}/download`}
                  download
                  className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white flex items-center gap-1.5 shadow-md shadow-emerald-600/20 transition"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span>Download PDF</span>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReportsPage;
