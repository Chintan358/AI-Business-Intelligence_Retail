import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Store, Save, CheckCircle2, AlertCircle } from 'lucide-react';

const BusinessProfilePage = () => {
  const [profile, setProfile] = useState({
    company_name: '',
    industry: 'Retail',
    team_size: '',
    target_margin: 25.0,
    business_goals: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/business/profile');
      setProfile(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSaved(false);
    try {
      const res = await apiClient.put('/business/profile', profile);
      setProfile(res.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError('Failed to update business profile.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading business profile...</div>;
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            Enterprise Settings
          </span>
          <span className="text-xs text-slate-400">• Business Configuration</span>
        </div>
        <h1 className="text-xl font-bold text-white tracking-tight">Business Profile & Strategic Targets</h1>
        <p className="text-xs text-slate-400 mt-1">
          The autonomous CrewAI agents leverage these business goals and target margins to contextualize analytical findings and turnaround plans.
        </p>
      </div>

      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
        {saved && (
          <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            <span>Business profile updated successfully!</span>
          </div>
        )}

        {error && (
          <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Company Name</label>
            <input
              type="text"
              required
              value={profile.company_name}
              onChange={(e) => setProfile({ ...profile, company_name: e.target.value })}
              className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-300 mb-1.5">Industry Domain</label>
              <input
                type="text"
                disabled
                value={profile.industry}
                className="w-full p-2.5 bg-slate-900 border border-slate-800 rounded-xl text-slate-400 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-300 mb-1.5">Target Gross Margin (%)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                value={profile.target_margin}
                onChange={(e) => setProfile({ ...profile, target_margin: parseFloat(e.target.value) || 0 })}
                className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              />
            </div>
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Team Size</label>
            <input
              type="text"
              value={profile.team_size || ''}
              onChange={(e) => setProfile({ ...profile, team_size: e.target.value })}
              placeholder="e.g. 50-100 employees"
              className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1.5">Primary Strategic Business Goals</label>
            <textarea
              rows={4}
              value={profile.business_goals || ''}
              onChange={(e) => setProfile({ ...profile, business_goals: e.target.value })}
              placeholder="Describe current quarter operational goals, return reduction priorities, or cost-cutting objectives..."
              className="w-full p-2.5 bg-slate-950 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 transition disabled:opacity-50"
          >
            {saving ? (
              <span>Saving Changes...</span>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>Save Profile Configuration</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default BusinessProfilePage;
