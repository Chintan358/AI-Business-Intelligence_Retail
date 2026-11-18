import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Users, Shield, CheckCircle2, UserCheck, AlertCircle } from 'lucide-react';

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/users/');
      setUsers(res.data);
    } catch (err) {
      setError('Access restricted to administrators.');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await apiClient.put(`/users/${userId}/role?role=${newRole}`);
      fetchUsers();
    } catch (err) {
      alert('Failed to update user role.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            Access Control
          </span>
          <span className="text-xs text-slate-400">• Role-Based User Management</span>
        </div>
        <h1 className="text-xl font-bold text-white tracking-tight">Enterprise User Management</h1>
        <p className="text-xs text-slate-400 mt-1">Manage system administrators, retail managers, and analytical users.</p>
      </div>

      {error ? (
        <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
          {error}
        </div>
      ) : (
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading user directory...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider">
                  <tr>
                    <th className="p-2.5 rounded-l-lg">ID</th>
                    <th className="p-2.5">Full Name</th>
                    <th className="p-2.5">Email</th>
                    <th className="p-2.5">Role</th>
                    <th className="p-2.5">Status</th>
                    <th className="p-2.5 rounded-r-lg text-right">Modify Role</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-300">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-800/30">
                      <td className="p-2.5 font-bold text-white">#{u.id}</td>
                      <td className="p-2.5 font-semibold text-white">{u.full_name}</td>
                      <td className="p-2.5 text-slate-400">{u.email}</td>
                      <td className="p-2.5">
                        <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-800 text-slate-300 border border-slate-700">
                          {u.role}
                        </span>
                      </td>
                      <td className="p-2.5">
                        {u.is_active ? (
                          <span className="text-emerald-400 flex items-center gap-1">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            Active
                          </span>
                        ) : (
                          <span className="text-slate-500">Inactive</span>
                        )}
                      </td>
                      <td className="p-2.5 text-right">
                        <select
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          className="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-[11px] text-white focus:outline-none focus:border-emerald-500"
                        >
                          <option value="admin">admin</option>
                          <option value="manager">manager</option>
                          <option value="analyst">analyst</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UserManagementPage;
