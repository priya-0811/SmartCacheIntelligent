import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function TelemetryCharts({ history, cachedFiles }) {
  const timestamps = history.map(h => new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));

  // Chart 1: Cache Hit Trend (Hits vs Misses)
  const hitTrendData = {
    labels: timestamps,
    datasets: [
      {
        label: 'Cache Hits',
        data: history.map(h => h.cache_hits),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Cache Misses',
        data: history.map(h => h.cache_misses),
        borderColor: '#F43F5E',
        backgroundColor: 'rgba(244, 63, 94, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  };

  // Chart 2: Latency Graph (ms)
  const latencyData = {
    labels: timestamps,
    datasets: [
      {
        label: 'Average Read Latency (ms)',
        data: history.map(h => h.avg_read_latency),
        borderColor: '#6366F1',
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        fill: true,
        tension: 0.3
      }
    ]
  };

  // Chart 3: RAM Memory Usage (MB) & Evictions
  const ramUsageData = {
    labels: timestamps,
    datasets: [
      {
        label: 'RAM Usage (MB)',
        data: history.map(h => h.current_ram_usage),
        borderColor: '#F59E0B',
        backgroundColor: 'rgba(245, 158, 11, 0.2)',
        yAxisID: 'y'
      },
      {
        label: 'Evictions Count',
        data: history.map(h => h.eviction_count),
        borderColor: '#EC4899',
        backgroundColor: 'rgba(236, 72, 153, 0.6)',
        type: 'bar',
        yAxisID: 'y1'
      }
    ]
  };

  // Chart 4: Access Frequency distribution across top files
  const topFiles = (cachedFiles || []).slice(0, 8);
  const accessFreqData = {
    labels: topFiles.map(f => f.filepath.split(/[/\\]/).pop()),
    datasets: [
      {
        label: 'Access Frequency',
        data: topFiles.map(f => f.access_frequency),
        backgroundColor: '#06B6D4',
        borderRadius: 8
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#94A3B8', font: { family: 'Inter', size: 11 } }
      },
      tooltip: {
        backgroundColor: '#1E293B',
        titleColor: '#F8FAFC',
        bodyColor: '#CBD5E1',
        borderColor: '#334155',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        ticks: { color: '#64748B', font: { size: 10 } },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      },
      y: {
        ticks: { color: '#64748B', font: { size: 10 } },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      }
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      {/* Chart 1: Hit Trend */}
      <div className="glass-panel p-5 rounded-2xl">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center justify-between">
          <span>Cache Hit vs Miss Trend</span>
          <span className="text-xs font-normal text-slate-400">Real-time</span>
        </h3>
        <div className="h-64">
          <Line data={hitTrendData} options={chartOptions} />
        </div>
      </div>

      {/* Chart 2: Latency Graph */}
      <div className="glass-panel p-5 rounded-2xl">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center justify-between">
          <span>Average Read Latency (ms)</span>
          <span className="text-xs font-normal text-slate-400">Lower is better</span>
        </h3>
        <div className="h-64">
          <Line data={latencyData} options={chartOptions} />
        </div>
      </div>

      {/* Chart 3: RAM Usage & Evictions */}
      <div className="glass-panel p-5 rounded-2xl">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center justify-between">
          <span>RAM Usage & Eviction Count</span>
          <span className="text-xs font-normal text-slate-400">Capacity tracking</span>
        </h3>
        <div className="h-64">
          <Bar
            data={ramUsageData}
            options={{
              ...chartOptions,
              scales: {
                ...chartOptions.scales,
                y1: {
                  position: 'right',
                  ticks: { color: '#EC4899', font: { size: 10 } },
                  grid: { drawOnChartArea: false }
                }
              }
            }}
          />
        </div>
      </div>

      {/* Chart 4: Access Frequency */}
      <div className="glass-panel p-5 rounded-2xl">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center justify-between">
          <span>File Access Frequency Distribution</span>
          <span className="text-xs font-normal text-slate-400">Top Cached Files</span>
        </h3>
        <div className="h-64">
          <Bar data={accessFreqData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
}
