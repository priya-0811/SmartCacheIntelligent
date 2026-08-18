import React from 'react';
import { Cpu, ArrowRight, Zap } from 'lucide-react';

export default function MarkovPredictionsTable({ transitionsData }) {
  const transitions = transitionsData?.transitions || [];
  const threshold = transitionsData?.threshold || 0.70;

  return (
    <div className="glass-panel p-6 rounded-2xl mt-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" /> Markov Chain Predictive Preloader Matrix
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Formula: <code>P(B|A) = Transition(A→B) / TotalTransitions(A)</code>
          </p>
        </div>
        <span className="text-xs text-purple-300 bg-purple-500/10 px-3 py-1.5 rounded-xl border border-purple-500/20 font-semibold flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-purple-400" />
          Preload Trigger Threshold: <strong>{(threshold * 100).toFixed(0)}%</strong>
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 uppercase text-slate-400 text-[10px] font-semibold tracking-wider">
            <tr>
              <th className="py-3 px-4">Source File (A)</th>
              <th className="py-3 px-4 text-center">Transition</th>
              <th className="py-3 px-4">Target File (B)</th>
              <th className="py-3 px-4">Transitions Count</th>
              <th className="py-3 px-4">Total A Transitions</th>
              <th className="py-3 px-4">Probability P(B|A)</th>
              <th className="py-3 px-4">Preload Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {transitions.length > 0 ? (
              transitions.map((item) => {
                const probPct = (item.probability * 100).toFixed(1);
                const isTriggered = item.probability >= threshold;

                return (
                  <tr key={item.id} className="hover:bg-slate-800/50 transition-all">
                    <td className="py-3 px-4 font-medium text-slate-200 truncate max-w-[200px]" title={item.previous_file}>
                      {item.previous_file.split(/[/\\]/).pop()}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <ArrowRight className="w-4 h-4 text-slate-500 inline-block" />
                    </td>
                    <td className="py-3 px-4 font-medium text-indigo-300 truncate max-w-[200px]" title={item.next_file}>
                      {item.next_file.split(/[/\\]/).pop()}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-200">
                      {item.transition_count}
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {item.total_source_transitions}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className={`font-bold ${isTriggered ? 'text-purple-400' : 'text-slate-300'}`}>
                          {probPct}%
                        </span>
                        <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${isTriggered ? 'bg-purple-500' : 'bg-slate-600'}`}
                            style={{ width: `${Math.min(100, item.probability * 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {isTriggered ? (
                        <span className="px-2.5 py-1 rounded-lg text-[10px] font-extrabold bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1 w-fit">
                          <Zap className="w-3 h-3" /> PRELOAD ACTIVE
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-lg text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
                          Below Threshold
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="7" className="py-8 text-center text-slate-500">
                  No Markov transitions recorded yet. Access sequence files A -&gt; B to build state matrix.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
