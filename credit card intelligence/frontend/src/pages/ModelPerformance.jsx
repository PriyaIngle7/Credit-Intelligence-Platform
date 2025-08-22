import React from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';

async function fetchLatest() {
  const { data } = await axios.get('/api/v1/ml/performance/latest');
  return data;
}

export default function ModelPerformance() {
  const { data, isLoading, error } = useQuery(['model-latest'], fetchLatest);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Model Performance</h1>
      {error && <div className="text-red-400">{error?.response?.data?.detail || 'Error loading'}</div>}
      <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
        {isLoading ? (
          <div className="text-slate-400">Loading…</div>
        ) : data ? (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div><div className="text-slate-400 text-sm">Version</div><div className="text-xl font-semibold">{data.model_version}</div></div>
            <div><div className="text-slate-400 text-sm">Accuracy</div><div className="text-xl font-semibold">{Math.round((data.accuracy || 0) * 100)}%</div></div>
            <div><div className="text-slate-400 text-sm">F1 Score</div><div className="text-xl font-semibold">{Math.round((data.f1_score || 0) * 100)}%</div></div>
            <div><div className="text-slate-400 text-sm">AUC-ROC</div><div className="text-xl font-semibold">{Math.round((data.auc_roc || 0) * 100)}%</div></div>
            <div><div className="text-slate-400 text-sm">SHAP Consistency</div><div className="text-xl font-semibold">{Math.round((data.shap_consistency || 0) * 100)}%</div></div>
            <div><div className="text-slate-400 text-sm">FI Stability</div><div className="text-xl font-semibold">{Math.round((data.feature_importance_stability || 0) * 100)}%</div></div>
          </div>
        ) : (
          <div className="text-slate-400">No performance data yet.</div>
        )}
      </div>
    </div>
  );
} 