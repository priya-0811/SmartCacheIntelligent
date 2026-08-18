import React, { useState } from 'react';
import { Zap, Play, HardDrive, Cpu, CheckCircle2, TrendingUp } from 'lucide-react';
import axios from 'axios';

export default function BenchmarkPanel() {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [iterations, setIterations] = useState(100);

  const handleRunBenchmark = async () => {
    setIsRunning(true);
    setResult(null);

    try {
      let res;
      try {
        res = await axios.post(`/api/benchmark/run?iterations=${iterations}`);
      } catch (e1) {
        res = await axios.post(`http://localhost:8000/benchmark/run?iterations=${iterations}`);
      }
      setResult(res.data);
    } catch (err) {
      alert('Error running benchmark: ' + (err.response?.data?.detail || err.message || 'Make sure backend is running on http://localhost:8000'));
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="glass-panel p-6 rounded-2xl mt-6 max-w-4xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6 border-b border-slate-800 pb-6">
        <div>
          <h3 className="text-lg font-bold text-slate-200 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" /> Performance Evaluation Benchmark Engine
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Empirically measures and compares cold disk I/O latency against SmartCache in-memory RAM latency.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={iterations}
            onChange={(e) => setIterations(Number(e.target.value))}
            className="bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 rounded-xl px-3 py-2.5 focus:outline-none"
          >
            <option value={50}>50 Iterations</option>
            <option value={100}>100 Iterations</option>
            <option value={250}>250 Iterations</option>
          </select>

          <button
            onClick={handleRunBenchmark}
            disabled={isRunning}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/20 flex items-center gap-2 transition-all disabled:opacity-50"
          >
            <Play className={`w-4 h-4 ${isRunning ? 'animate-spin' : ''}`} />
            {isRunning ? 'Benchmarking...' : 'Run Benchmark'}
          </button>
        </div>
      </div>

      {/* Benchmark Results */}
      {result ? (
        <div className="space-y-6">
          {/* Comparison Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Without SmartCache */}
            <div className="p-5 rounded-2xl bg-rose-500/5 border border-rose-500/20 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
                  <HardDrive className="w-4 h-4" /> Without SmartCache (Disk Read)
                </span>
                <h4 className="text-3xl font-extrabold text-slate-100 mt-2">
                  {result.without_smartcache.average_disk_read_time_ms} <span className="text-sm font-normal text-slate-400">ms / read</span>
                </h4>
              </div>
              <div className="px-3 py-1.5 rounded-xl bg-rose-500/10 text-rose-400 font-mono text-xs font-bold">
                Cold Disk I/O
              </div>
            </div>

            {/* With SmartCache */}
            <div className="p-5 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                  <Cpu className="w-4 h-4" /> With SmartCache (RAM Read)
                </span>
                <h4 className="text-3xl font-extrabold text-slate-100 mt-2">
                  {result.with_smartcache.average_ram_read_time_ms} <span className="text-sm font-normal text-slate-400">ms / read</span>
                </h4>
              </div>
              <div className="px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-400 font-mono text-xs font-bold">
                In-Memory RAM
              </div>
            </div>
          </div>

          {/* 4 Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium">Speedup %</p>
              <h5 className="text-2xl font-bold text-indigo-400 mt-1">+{result.results.speedup_percentage}%</h5>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium">Hit Ratio %</p>
              <h5 className="text-2xl font-bold text-emerald-400 mt-1">{result.results.hit_ratio_percentage}%</h5>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium">Latency Reduction</p>
              <h5 className="text-2xl font-bold text-amber-400 mt-1">{result.results.latency_reduction_ms} ms</h5>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium">Memory Savings</p>
              <h5 className="text-2xl font-bold text-cyan-400 mt-1">{result.results.memory_savings_mb} MB</h5>
            </div>
          </div>
        </div>
      ) : (
        <div className="py-12 text-center text-slate-500 flex flex-col items-center justify-center">
          <TrendingUp className="w-12 h-12 text-slate-700 mb-3" />
          <p className="text-sm font-medium">Click "Run Benchmark" to execute live disk vs RAM latency comparison.</p>
        </div>
      )}
    </div>
  );
}
