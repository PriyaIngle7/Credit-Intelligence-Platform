import React, { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { Link } from 'react-router-dom';

async function fetchScores(params) {
  const { data } = await axios.get('/api/v1/credit-scores', { params });
  return data;
}

export default function CreditScores() {
  const [filters, setFilters] = useState({ score_type: 'issuer', risk_level: '' });
  const { data, isLoading, refetch } = useQuery(['credit-scores', filters], () => fetchScores(filters));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Credit Scores</h1>

      <div className="bg-slate-900 p-4 rounded-lg border border-slate-800 grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label className="block text-sm text-slate-400 mb-1">Score Type</label>
          <select
            value={filters.score_type}
            onChange={e => setFilters({ ...filters, score_type: e.target.value })}
            className="bg-slate-800 border border-slate-700 rounded px-3 py-2 w-full"
          >
            <option value="issuer">Issuer</option>
            <option value="asset_class">Asset Class</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-1">Risk Level</label>
          <select
            value={filters.risk_level}
            onChange={e => setFilters({ ...filters, risk_level: e.target.value })}
            className="bg-slate-800 border border-slate-700 rounded px-3 py-2 w-full"
          >
            <option value="">All</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div className="flex items-end">
          <button onClick={() => refetch()} className="bg-primary-600 hover:bg-primary-700 text-white rounded px-4 py-2">Apply</button>
        </div>
      </div>

      <div className="bg-slate-900 rounded-lg border border-slate-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-800 text-slate-300">
            <tr>
              <th className="text-left px-4 py-2">Company</th>
              <th className="text-left px-4 py-2">Ticker</th>
              <th className="text-left px-4 py-2">Score</th>
              <th className="text-left px-4 py-2">Risk</th>
              <th className="text-left px-4 py-2">Confidence</th>
              <th className="text-left px-4 py-2">Top Factors</th>
            </tr>
          </thead>
          <tbody>
            {(data || []).map((item) => (
              <tr key={item.id} className="border-t border-slate-800 hover:bg-slate-800/50">
                <td className="px-4 py-2"><Link className="text-primary-400 hover:underline" to={`/company/${item.company_id}`}>{item.company_id}</Link></td>
                <td className="px-4 py-2">—</td>
                <td className="px-4 py-2 font-semibold">{item.score.toFixed(1)}</td>
                <td className="px-4 py-2 capitalize">{item.risk_level}</td>
                <td className="px-4 py-2">{Math.round(item.confidence * 100)}%</td>
                <td className="px-4 py-2">{(item.key_factors || []).join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 