import React, { useState } from 'react';
import { Settings, Shield, Key, Database, Server, CheckCircle2 } from 'lucide-react';

const SettingsPage = () => {
  const [geminiKey, setGeminiKey] = useState('');
  const [model, setModel] = useState('gemini-1.5-flash');
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    if (geminiKey) {
      localStorage.setItem('GEMINI_API_KEY', geminiKey);
    }
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            System Configuration
          </span>
          <span className="text-xs text-slate-400">• Environment & Integration Settings</span>
        </div>
        <h1 className="text-xl font-bold text-white tracking-tight">System Settings & LLM Configuration</h1>
        <p className="text-xs text-slate-400 mt-1">Configure Gemini API keys, provider parameters, and backend connectivity.</p>
      </div>

      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6 shadow-xl text-xs">
        {saved && (
          <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            <span>Settings saved successfully!</span>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-5">
          <div>
            <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
              <Key className="h-4 w-4 text-emerald-400" />
              <span>Google Gemini API Key</span>
            </h3>
            <p className="text-slate-400 text-[11px] mb-2">
              Enter your Google Gemini API key to activate natural language reasoning for CrewAI agents and AI Chat.
            </p>
            <input
              type="password"
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              placeholder="AIzaSy..."
              className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 font-mono"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Preferred Gemini Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="gemini-1.5-flash">Gemini 1.5 Flash (Recommended - High Speed)</option>
              <option value="gemini-1.5-pro">Gemini 1.5 Pro (Deep Strategic Analysis)</option>
              <option value="gemini-2.5-flash">Gemini 2.5 Flash (Next-Gen)</option>
            </select>
          </div>

          <button
            type="submit"
            className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-lg shadow-emerald-600/20 transition"
          >
            Save Configuration
          </button>
        </form>

        <div className="pt-5 border-t border-slate-800 space-y-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Server className="h-4 w-4 text-emerald-400" />
            <span>Deployment Architecture Status</span>
          </h3>
          <div className="grid grid-cols-2 gap-3 text-[11px]">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-500 block">Backend Service</span>
              <strong className="text-emerald-400">FastAPI (Render Web Service)</strong>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-500 block">Database</span>
              <strong className="text-emerald-400">PostgreSQL (Render Managed)</strong>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-500 block">Frontend Host</span>
              <strong className="text-emerald-400">React 18 + Vite (Vercel)</strong>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-500 block">Multi-Agent Engine</span>
              <strong className="text-emerald-400">CrewAI 0.86+ (6 Agents)</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
