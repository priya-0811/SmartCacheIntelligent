import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from './components/Navbar';
import StatsCards from './components/StatsCards';
import TelemetryCharts from './components/TelemetryCharts';
import AccessLogsTable from './components/AccessLogsTable';
import CachedFilesTable from './components/CachedFilesTable';
import MarkovPredictionsTable from './components/MarkovPredictionsTable';
import ConfigPanel from './components/ConfigPanel';
import BenchmarkPanel from './components/BenchmarkPanel';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // System State Data
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [accessLogs, setAccessLogs] = useState([]);
  const [cacheEvents, setCacheEvents] = useState([]);
  const [cachedFiles, setCachedFiles] = useState([]);
  const [transitionsData, setTransitionsData] = useState({ transitions: [], threshold: 0.70 });

  const fetchAllData = async () => {
    setIsRefreshing(true);
    try {
      const [statsRes, historyRes, logsRes, eventsRes, filesRes, transRes] = await Promise.all([
        axios.get('/api/cache/stats'),
        axios.get('/api/telemetry/history?limit=30'),
        axios.get('/api/logs/access?limit=20'),
        axios.get('/api/logs/events?limit=20'),
        axios.get('/api/cache/files'),
        axios.get('/api/predictor/transitions')
      ]);

      setStats(statsRes.data);
      setHistory(historyRes.data);
      setAccessLogs(logsRes.data);
      setCacheEvents(eventsRes.data);
      setCachedFiles(filesRes.data.files);
      setTransitionsData(transRes.data);
    } catch (err) {
      console.error('Error fetching SmartCache metrics:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000); // Polling every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-dark-900 text-slate-100 pb-16">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRefresh={fetchAllData}
        isRefreshing={isRefreshing}
      />

      <main className="max-w-7xl mx-auto px-6 pt-6">
        {/* Always render Top Stats Cards */}
        <StatsCards stats={stats} />

        {/* Tab 1: Overview Dashboard */}
        {activeTab === 'overview' && (
          <>
            <TelemetryCharts history={history} cachedFiles={cachedFiles} />
            <AccessLogsTable logs={accessLogs} events={cacheEvents} />
          </>
        )}

        {/* Tab 2: RAM Files Residency */}
        {activeTab === 'files' && (
          <CachedFilesTable files={cachedFiles} />
        )}

        {/* Tab 3: Markov Engine */}
        {activeTab === 'markov' && (
          <MarkovPredictionsTable transitionsData={transitionsData} />
        )}

        {/* Tab 4: Performance Benchmark */}
        {activeTab === 'benchmark' && (
          <BenchmarkPanel />
        )}

        {/* Tab 5: Configuration */}
        {activeTab === 'config' && (
          <ConfigPanel stats={stats} onConfigUpdated={fetchAllData} />
        )}
      </main>
    </div>
  );
}
