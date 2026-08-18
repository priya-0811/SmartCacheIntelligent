import React from 'react';
import { HardDrive, File, Database } from 'lucide-react';

export default function CachedFilesTable({ files }) {
  return (
    <div className="glass-panel p-6 rounded-2xl mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
          <HardDrive className="w-5 h-5 text-cyan-400" /> Active RAM Cache Residency
        </h3>
        <span className="text-xs text-slate-400 bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700">
          Total Cached: <strong>{files ? files.length : 0}</strong>
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 uppercase text-slate-400 text-[10px] font-semibold tracking-wider">
            <tr>
              <th className="py-3 px-4">Absolute File Path</th>
              <th className="py-3 px-4">Size</th>
              <th className="py-3 px-4">Frequency</th>
              <th className="py-3 px-4">Hit Count</th>
              <th className="py-3 px-4">Last Accessed</th>
              <th className="py-3 px-4">Cached At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {files && files.length > 0 ? (
              files.map((file, idx) => (
                <tr key={idx} className="hover:bg-slate-800/50 transition-all">
                  <td className="py-3 px-4 font-mono text-cyan-300 flex items-center gap-2">
                    <File className="w-4 h-4 text-slate-400 shrink-0" />
                    <span className="truncate max-w-[400px]" title={file.filepath}>
                      {file.filepath}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-semibold text-slate-200">
                    {(file.filesize / 1024).toFixed(2)} KB
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold">
                      {file.access_frequency}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-emerald-400 font-bold">
                    {file.hit_count}
                  </td>
                  <td className="py-3 px-4 text-slate-400">
                    {new Date(file.last_accessed_timestamp * 1000).toLocaleTimeString()}
                  </td>
                  <td className="py-3 px-4 text-slate-500">
                    {new Date(file.cached_timestamp * 1000).toLocaleTimeString()}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="py-8 text-center text-slate-500">
                  RAM Cache is currently empty. Access files via API or run benchmark to populate cache.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
