import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  BrainCircuit,
  Bot,
  MessageSquare,
  FileCheck2,
  FileText,
  UploadCloud,
  History,
  TableProperties,
  Store,
  Users,
  ShieldAlert,
  Settings,
  LogOut,
  Menu,
  X,
  Sparkles,
  Layers
} from 'lucide-react';

const DashboardLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { section: 'Analytics & Insights' },
    { to: '/', label: 'Executive Dashboard', icon: LayoutDashboard },
    { to: '/analysis', label: 'AI Business Analysis', icon: BrainCircuit, badge: '6 Agents' },
    { to: '/agents/monitor', label: 'Agent Monitoring', icon: Bot },
    { to: '/chat', label: 'AI Business Chat', icon: MessageSquare },
    { to: '/approvals', label: 'Approval Management', icon: FileCheck2, badge: 'HITL' },
    { to: '/reports', label: 'Reports & Analytics', icon: FileText },
    { to: '/history', label: 'Analysis History', icon: History },

    { section: 'Retail Operations' },
    { to: '/datasets/upload', label: 'Dataset Upload', icon: UploadCloud },
    { to: '/datasets/preview', label: 'Data Preview', icon: TableProperties },
    { to: '/datasets/history', label: 'Upload History', icon: Layers },
    { to: '/profile', label: 'Business Profile', icon: Store },

    { section: 'Administration' },
    { to: '/admin', label: 'Admin Telemetry', icon: ShieldAlert, adminOnly: true },
    { to: '/admin/users', label: 'User Management', icon: Users, adminOnly: true },
    { to: '/settings', label: 'System Settings', icon: Settings }
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Mobile Sidebar Overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 flex flex-col transition-transform duration-300 lg:static lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white block">RetailIntelligence</span>
              <span className="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider">Multi-Agent AI</span>
            </div>
          </div>
          <button
            className="lg:hidden text-slate-400 hover:text-white"
            onClick={() => setMobileOpen(false)}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {navItems.map((item, idx) => {
            if (item.section) {
              return (
                <div key={idx} className="pt-4 pb-1 px-3">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                    {item.section}
                  </span>
                </div>
              );
            }

            if (item.adminOnly && user?.role !== 'admin') {
              return null;
            }

            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <div className="flex items-center space-x-3">
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* User Card */}
        <div className="p-3 border-t border-slate-800 bg-slate-900/50">
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-800/40 border border-slate-800">
            <div className="flex items-center space-x-2.5 overflow-hidden">
              <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center font-bold text-xs text-emerald-400">
                {user?.full_name ? user.full_name[0].toUpperCase() : 'U'}
              </div>
              <div className="truncate">
                <p className="text-xs font-semibold text-slate-200 truncate">{user?.full_name || 'User'}</p>
                <span className="inline-block px-1.5 py-0.2 text-[9px] uppercase font-bold tracking-wider rounded bg-slate-700 text-slate-300">
                  {user?.role || 'Manager'}
                </span>
              </div>
            </div>
            <button
              onClick={handleLogout}
              title="Logout"
              className="text-slate-400 hover:text-rose-400 p-1.5 transition-colors"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top bar */}
        <header className="h-14 border-b border-slate-800 bg-slate-900/40 backdrop-blur px-4 flex items-center justify-between lg:px-8">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setMobileOpen(true)}
              className="lg:hidden text-slate-400 hover:text-white p-1"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Dataset Period: <strong className="text-slate-200">May 1 – Oct 31, 2026</strong></span>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              PostgreSQL Active
            </span>
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
              <BrainCircuit className="h-3 w-3" />
              6 CrewAI Agents
            </span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-8 bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
