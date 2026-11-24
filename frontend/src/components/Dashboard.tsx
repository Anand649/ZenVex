import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  TrendingUp, 
  Clock, 
  Terminal, 
  Globe, 
  ExternalLink,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  Database
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import { api } from '../services/api';
import { IntelligenceStats } from '../types/intelligence';

interface DashboardProps {
  onScanMessage: (sampleText?: string) => void;
  onScanUrl: (sampleUrl?: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onScanMessage, onScanUrl }) => {
  const [stats, setStats] = useState<IntelligenceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const [searchQuery, setSearchQuery] = useState('');

  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await api.getStats();
      setStats(data);
      setLastRefreshed(new Date());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const COLORS = ['#ef4444', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#10b981'];

  const filteredThreats = stats?.recent_threats.filter(t => 
    t.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.id.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="space-y-8 py-6">
      {/* Header bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Command Centre Intelligence
            </h1>
            <span className="px-2 py-0.5 text-xs font-mono bg-violet-500/20 text-violet-300 border border-violet-500/30 rounded">
              DEMO DATA
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Illustrative scan counts, category trends, and sample events.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={loadStats}
            disabled={loading}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-navy-850 hover:bg-slate-800 text-slate-300 text-xs border border-slate-700/80 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <div className="text-[11px] font-mono text-slate-500">
            Updated: {lastRefreshed.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Total Analyses */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Inbound Scanned</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-white font-mono">
            {stats ? stats.total_analyses.toLocaleString() : '24,890'}
          </div>
          <div className="flex items-center text-[11px] text-emerald-400 space-x-1">
            <TrendingUp className="w-3 h-3" />
            <span>+14.2% activity this week</span>
          </div>
        </div>

        {/* Threats Detected */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Flagged Scans</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-3xl font-extrabold text-rose-400 font-mono">
            {stats ? stats.threats_detected.toLocaleString() : '16,420'}
          </div>
          <div className="text-[11px] text-slate-400">
            {stats ? `${((stats.threats_detected / stats.total_analyses) * 100).toFixed(1)}% flagged in this sample` : '65.9% flagged in this sample'}
          </div>
        </div>

        {/* High Risk Detections */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Critical & High Risk</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400 font-mono">
            {stats ? stats.high_risk_detections.toLocaleString() : '6,830'}
          </div>
          <div className="text-[11px] text-slate-400">
            Illustrative high-risk count
          </div>
        </div>

        {/* Safe Analyses */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Low Detected Risk</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400 font-mono">
            {stats ? stats.safe_analyses.toLocaleString() : '8,470'}
          </div>
          <div className="text-[11px] text-slate-400">
            Based on detected warning signs
          </div>
        </div>
      </div>

      {/* Quick Launch Action Ribbon */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-violet-950/40 via-navy-900 to-indigo-950/40 border border-violet-500/30 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-violet-600 flex items-center justify-center text-white shrink-0">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Investigate an Unverified Message or Link</h4>
            <p className="text-xs text-slate-400">Run immediate stateless forensic analysis on suspicious inbound text or URLs.</p>
          </div>
        </div>
        <div className="flex items-center space-x-2.5 shrink-0">
          <button
            onClick={() => onScanMessage()}
            className="px-4 py-2 text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white rounded-lg transition-colors shadow-sm"
          >
            Launch Message Scanner
          </button>
          <button
            onClick={() => onScanUrl()}
            className="px-4 py-2 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg transition-colors"
          >
            Launch URL Intelligence
          </button>
        </div>
      </div>

      {/* Visualisation Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Timeline Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">Scan Activity & Detection Rate</h3>
              <p className="text-xs text-slate-400">Hourly throughput vs intercepted threats</p>
            </div>
            <div className="flex items-center space-x-3 text-[11px] font-mono">
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded bg-violet-500 inline-block"></span>
                <span className="text-slate-300">Total Scans</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded bg-rose-500 inline-block"></span>
                <span className="text-slate-300">Threats</span>
              </span>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.timeline_activity || []}>
                <defs>
                  <linearGradient id="colorScans" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorThreats" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.5}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#0F172A', 
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }} 
                />
                <Area type="monotone" dataKey="scans" stroke="#8b5cf6" strokeWidth={2} fillOpacity={1} fill="url(#colorScans)" />
                <Area type="monotone" dataKey="threats" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorThreats)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Scam Category Breakdown BarChart */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">Scam Category Distribution</h3>
              <p className="text-xs text-slate-400">Prevalent deception vectors detected in India</p>
            </div>
            <span className="text-[11px] font-mono text-cyan-400">9 Indian Playbooks</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.scam_category_distribution || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
                <XAxis type="number" stroke="#64748B" fontSize={11} />
                <YAxis dataKey="name" type="category" stroke="#94A3B8" fontSize={11} width={130} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#0F172A', 
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }} 
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {(stats?.scam_category_distribution || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Live Threat Activity Log Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-white">Recent Investigation Activity</h3>
            <p className="text-xs text-slate-400">Illustrative examples of flagged activity</p>
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter by threat or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-navy-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-900/80 text-slate-400 font-mono text-[11px] uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-5">Investigation ID</th>
                <th className="py-3 px-5">Threat Category</th>
                <th className="py-3 px-5">Risk Band</th>
                <th className="py-3 px-5">Evidence Score</th>
                <th className="py-3 px-5">Detected Language</th>
                <th className="py-3 px-5">Timestamp</th>
                <th className="py-3 px-5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredThreats.map((threat) => {
                const isCrit = threat.risk === 'Critical';
                const isHigh = threat.risk === 'High';
                return (
                  <tr key={threat.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-5 font-semibold text-slate-200">{threat.id}</td>
                    <td className="py-3 px-5 text-slate-300 font-sans">{threat.category}</td>
                    <td className="py-3 px-5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        isCrit ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                        isHigh ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                        'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                      }`}>
                        {threat.risk}
                      </span>
                    </td>
                    <td className="py-3 px-5">
                      <span className={`font-bold ${
                        isCrit ? 'text-rose-400' : isHigh ? 'text-amber-400' : 'text-violet-400'
                      }`}>
                        {threat.score} / 100
                      </span>
                    </td>
                    <td className="py-3 px-5 uppercase text-slate-400">{threat.language}</td>
                    <td className="py-3 px-5 text-slate-500">{threat.timestamp}</td>
                    <td className="py-3 px-5 text-right">
                      <button 
                        onClick={() => onScanMessage(`Sample ${threat.category} inspection trigger`)}
                        className="text-cyan-400 hover:text-cyan-300 transition-colors text-[11px]"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
