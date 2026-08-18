import React from 'react';
import { Clock, Tag, FileText } from 'lucide-react';

export default function AccessLogsTable({ logs, events }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      {/* Recent Access Logs Table (2 cols) */}
      <div className="lg:col-span-2 glass-panel p-5 rounded-2xl">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <Clock className="w-4 h-4 text-indigo-400" /> Recent File Access Logs
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/60 uppercase text-slate-400 text-[10px] font-semibold tracking-wider">
              <tr>
                <th className="py-2.5 px-3">File Name</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Latency</th>
                <th className="py-2.5 px-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {logs && logs.length > 0 ? (
                logs.slice(0, 10).map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition-all">
                    <td className="py-2.5 px-3 font-medium text-slate-200 flex items-center gap-2">
                      <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate max-w-[200px]" title={log.filepath}>{log.filename}</span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                          log.cache_status === 'CACHE_HIT'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}
                      >
                        {log.cache_status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-300">
                      {log.latency_ms} ms
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="py-6 text-center text-slate-500">
                    No access logs available. Access files using GET /file?path=...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cache Events Log (1 col) */}
      <div className="glass-panel p-5 rounded-2xl">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <Tag className="w-4 h-4 text-purple-400" /> Cache Event Feed
        </h3>
        <div className="space-y-3 max-h-[340px] overflow-y-auto pr-1">
          {events && events.length > 0 ? (
            events.slice(0, 15).map((evt) => (
              <div
                key={evt.id}
                className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs"
              >
                <div>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase ${
                      evt.event_type === 'PRELOAD'
                        ? 'bg-purple-500/20 text-purple-300'
                        : evt.event_type === 'EVICT'
                        ? 'bg-amber-500/20 text-amber-300'
                        : evt.event_type === 'CACHE_HIT'
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    {evt.event_type}
                  </span>
                  <p className="text-slate-300 font-medium mt-1 truncate max-w-[150px]">
                    {evt.filename}
                  </p>
                </div>
                <span className="text-[10px] text-slate-500 font-mono">
                  {new Date(evt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500 text-center py-6">No recent cache events.</p>
          )}
        </div>
      </div>
    </div>
  );
}
