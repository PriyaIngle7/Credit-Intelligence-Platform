import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

export default function DataIngestion() {
  const [ticker, setTicker] = useState('AAPL');
  const [busy, setBusy] = useState(false);

  async function triggerIngestion() {
    try {
      setBusy(true);
      await axios.post(`/api/v1/data/ingest/${ticker}`);
      toast.success(`Ingestion started for ${ticker}`);
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Failed to start ingestion');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Data Ingestion</h1>

      <div className="bg-slate-900 p-4 rounded-lg border border-slate-800 flex gap-3 items-end">
        <div className="flex-1">
          <label className="block text-sm text-slate-400 mb-1">Ticker</label>
          <input value={ticker} onChange={e => setTicker(e.target.value)} className="bg-slate-800 border border-slate-700 rounded px-3 py-2 w-full" placeholder="e.g. AAPL" />
        </div>
        <button onClick={triggerIngestion} disabled={busy} className="bg-primary-600 hover:bg-primary-700 text-white rounded px-4 py-2">
          {busy ? 'Starting…' : 'Start Ingestion'}
        </button>
      </div>
    </div>
  );
} 