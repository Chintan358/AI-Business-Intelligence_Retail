import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../api/client';
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Database,
  Layers,
  Sparkles
} from 'lucide-react';

const DatasetUploadPage = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
      setResult(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await apiClient.post('/datasets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload and process dataset.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            Data Ingestion
          </span>
          <span className="text-xs text-slate-400">• Multi-Sheet Workbook Importer</span>
        </div>
        <h1 className="text-xl font-bold text-white tracking-tight">Dataset Ingestion & Validation</h1>
        <p className="text-xs text-slate-400 mt-1">
          Upload an updated Excel workbook (`.xlsx`, `.xls`) or CSV. The backend validates schema headers, foreign key links, and imports clean rows into PostgreSQL.
        </p>
      </div>

      {/* Upload Box */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5 shadow-xl">
        {error && (
          <div className="p-3 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {result && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-2 text-xs">
            <div className="flex items-center gap-2 text-emerald-400 font-bold">
              <CheckCircle2 className="h-4 w-4" />
              <span>{result.message}</span>
            </div>
            {result.ingestion_result && (
              <div className="grid grid-cols-3 gap-2 mt-2 pt-2 border-t border-emerald-500/20 text-[11px] text-slate-300">
                <div>Customers: <strong>{result.ingestion_result.customers}</strong></div>
                <div>Products: <strong>{result.ingestion_result.products}</strong></div>
                <div>Transactions: <strong>{result.ingestion_result.transactions}</strong></div>
                <div>Items: <strong>{result.ingestion_result.items}</strong></div>
                <div>Inventory: <strong>{result.ingestion_result.inventory}</strong></div>
                <div>Expenses: <strong>{result.ingestion_result.expenses}</strong></div>
              </div>
            )}
            <div className="pt-2">
              <Link to="/analysis" className="text-emerald-400 hover:underline font-semibold">
                Proceed to AI Multi-Agent Analysis &rarr;
              </Link>
            </div>
          </div>
        )}

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="border-2 border-dashed border-slate-700 hover:border-emerald-500 rounded-2xl p-8 text-center transition cursor-pointer relative bg-slate-950/40">
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex flex-col items-center justify-center space-y-2">
              <div className="h-12 w-12 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400">
                <FileSpreadsheet className="h-6 w-6 text-emerald-400" />
              </div>
              <p className="text-xs font-semibold text-white">
                {file ? file.name : 'Click to select or drag & drop retail Excel workbook'}
              </p>
              <p className="text-[11px] text-slate-500">
                Supports .xlsx, .xls, .csv (Must contain Customers, Products, Transactions sheets)
              </p>
              {file && (
                <span className="text-[10px] text-emerald-400 font-mono mt-1">
                  Selected size: {(file.size / 1024).toFixed(1)} KB
                </span>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={!file || uploading}
            className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 transition disabled:opacity-50"
          >
            {uploading ? (
              <span>Validating & Ingesting into PostgreSQL...</span>
            ) : (
              <>
                <UploadCloud className="h-4 w-4" />
                <span>Upload and Ingest Dataset</span>
              </>
            )}
          </button>
        </form>

        <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-400 space-y-1">
          <strong className="text-slate-300 block">Current Active Dataset:</strong>
          <p>
            The system currently runs on <code>03_Retail.xlsx</code> (6 sheets, 2,500 transactions, May 1 – Oct 31, 2026). 
            Uploading a new file updates the underlying database tables and triggers fresh KPI recalculations.
          </p>
        </div>
      </div>
    </div>
  );
};

export default DatasetUploadPage;
