import React, { useState } from 'react';
import { Settings, Sliders, Trash2, Save, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function ConfigPanel({ stats, onConfigUpdated }) {
  const [maxSizeMb, setMaxSizeMb] = useState(stats?.max_memory_mb || 100);
  const [evictionAlgo, setEvictionAlgo] = useState(stats?.eviction_algorithm || 'hybrid');
  const [threshold, setThreshold] = useState(0.70);
  const [isSaving, setIsSaving] = useState(false);
  const [msg, setMsg] = useState(null);

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setMsg(null);

    try {
      const res = await axios.post('/api/cache/config', {
        max_size_mb: parseFloat(maxSizeMb),
        eviction_algorithm: evictionAlgo,
        preload_threshold: parseFloat(threshold)
      });

      setMsg({ type: 'success', text: 'Cache settings updated successfully!' });
      if (onConfigUpdated) onConfigUpdated();
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to update config.' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleClearCache = async () => {
    if (!window.confirm('Are you sure you want to clear all in-memory RAM cached entries?')) return;
    try {
      await axios.post('/api/cache/clear');
      setMsg({ type: 'success', text: 'RAM Cache cleared successfully.' });
      if (onConfigUpdated) onConfigUpdated();
    } catch (err) {
      setMsg({ type: 'error', text: 'Failed to clear RAM cache.' });
    }
  };

  return (
    <div className="glass-panel p-6 rounded-2xl mt-6 max-w-3xl mx-auto">
      <h3 className="text-lg font-bold text-slate-200 mb-6 flex items-center gap-2">
        <Settings className="w-5 h-5 text-indigo-400" /> Cache Manager Settings & Engine Controls
      </h3>

      {msg && (
        <div
          className={`p-4 rounded-xl mb-6 flex items-center gap-3 text-xs font-semibold ${
            msg.type === 'success'
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
          }`}
        >
          {msg.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          {msg.text}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Config 1: Max Cache Size */}
        <div>
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
            Max RAM Cache Capacity (MB)
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="10"
              max="1000"
              step="10"
              value={maxSizeMb}
              onChange={(e) => setMaxSizeMb(e.target.value)}
              className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer"
            />
            <span className="text-sm font-mono font-bold text-indigo-400 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800 min-w-[80px] text-center">
              {maxSizeMb} MB
            </span>
          </div>
        </div>

        {/* Config 2: Eviction Algorithm Selector */}
        <div>
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
            Eviction Policy Engine
          </label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'lru', label: 'LRU (Least Recently Used)', desc: 'Evicts oldest last access' },
              { id: 'lfu', label: 'LFU (Least Frequently Used)', desc: 'Evicts lowest access frequency' },
              { id: 'hybrid', label: 'Hybrid Scoring', desc: '0.6 × Freq + 0.4 × Recency Weight' }
            ].map((algo) => (
              <button
                type="button"
                key={algo.id}
                onClick={() => setEvictionAlgo(algo.id)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  evictionAlgo === algo.id
                    ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800'
                }`}
              >
                <div className="font-bold text-xs capitalize">{algo.label}</div>
                <div className="text-[10px] text-slate-500 mt-1">{algo.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Config 3: Markov Threshold */}
        <div>
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
            Markov Preloader Probability Threshold: <span className="text-purple-400 font-mono">{(threshold * 100).toFixed(0)}%</span>
          </label>
          <input
            type="number"
            min="0.1"
            max="1.0"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          />
          <p className="text-[11px] text-slate-500 mt-1">
            Preloads target file into RAM in background thread when P(B|A) &ge; threshold.
          </p>
        </div>

        {/* Form Controls */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
          <button
            type="button"
            onClick={handleClearCache}
            className="px-4 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-semibold flex items-center gap-2 transition-all"
          >
            <Trash2 className="w-4 h-4" /> Clear RAM Cache
          </button>

          <button
            type="submit"
            disabled={isSaving}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all"
          >
            <Save className="w-4 h-4" /> {isSaving ? 'Saving...' : 'Apply Settings'}
          </button>
        </div>
      </form>
    </div>
  );
}
