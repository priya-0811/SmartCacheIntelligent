import React from 'react';
import { CheckCircle2, XCircle, Activity, HardDrive, FileText, Layers } from 'lucide-react';

export default function StatsCards({ stats }) {
  const hitRatioPct = stats ? (stats.hit_ratio * 100).toFixed(1) : '0.0';
  const memUsageMb = stats ? stats.memory_usage_mb : 0;
  const maxMemMb = stats ? stats.max_memory_mb : 100;
  const memUtilPct = stats ? stats.memory_utilization_pct : 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* Cache Hits Card */}
      <div className="glass-panel p-5 rounded-2xl relative overflow-hidden group border-emerald-500/20 hover:border-emerald-500/40 transition-all">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cache Hits</p>
            <h3 className="text-2xl font-bold text-emerald-400 mt-1">{stats?.hit_count ?? 0}</h3>
          </div>
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 text-xs text-slate-400 flex items-center gap-1">
          <span>Successful RAM reads</span>
        </div>
      </div>

      {/* Cache Misses Card */}
      <div className="glass-panel p-5 rounded-2xl relative overflow-hidden group border-rose-500/20 hover:border-rose-500/40 transition-all">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cache Misses</p>
            <h3 className="text-2xl font-bold text-rose-400 mt-1">{stats?.miss_count ?? 0}</h3>
          </div>
          <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400">
            <XCircle className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 text-xs text-slate-400 flex items-center gap-1">
          <span>Disk fallback reads</span>
        </div>
      </div>

      {/* Hit Ratio Card */}
      <div className="glass-panel p-5 rounded-2xl relative overflow-hidden group border-indigo-500/20 hover:border-indigo-500/40 transition-all">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Hit Ratio</p>
            <h3 className="text-2xl font-bold text-indigo-400 mt-1">{hitRatioPct}%</h3>
          </div>
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400">
            <Activity className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-500"
            style={{ width: `${hitRatioPct}%` }}
          />
        </div>
      </div>

      {/* Memory Usage Card */}
      <div className="glass-panel p-5 rounded-2xl relative overflow-hidden group border-amber-500/20 hover:border-amber-500/40 transition-all">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Memory Usage</p>
            <h3 className="text-2xl font-bold text-amber-400 mt-1">{memUsageMb} <span className="text-sm font-normal text-slate-400">/ {maxMemMb} MB</span></h3>
          </div>
          <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400">
            <HardDrive className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-amber-500 h-full rounded-full transition-all duration-500"
            style={{ width: `${Math.min(100, memUtilPct)}%` }}
          />
        </div>
      </div>

      {/* Cached Files Card */}
      <div className="glass-panel p-5 rounded-2xl relative overflow-hidden group border-cyan-500/20 hover:border-cyan-500/40 transition-all">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cached Files</p>
            <h3 className="text-2xl font-bold text-cyan-400 mt-1">{stats?.cached_files_count ?? 0}</h3>
          </div>
          <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400">
            <FileText className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-3 text-xs text-slate-400 flex items-center justify-between">
          <span>Policy: <strong className="text-slate-200 uppercase">{stats?.eviction_algorithm ?? 'HYBRID'}</strong></span>
          <span>Evicts: <strong className="text-rose-300">{stats?.eviction_count ?? 0}</strong></span>
        </div>
      </div>
    </div>
  );
}
