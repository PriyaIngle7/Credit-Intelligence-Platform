import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios from 'axios';

async function fetchLatest(ticker) {
  const { data } = await axios.get(`/api/v1/credit-scores/company/${ticker}/latest`);
  return data;
}

export default function CompanyDetail() {
  const { ticker } = useParams();
  const { data, isLoading, error } = useQuery(['latest-score', ticker], () => fetchLatest(ticker));

  if (error) return <div className="text-red-400">{error?.response?.data?.detail || 'Error loading'}</div>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">{ticker} — Latest Score</h1>
      {isLoading ? (
        <div className="text-slate-400">Loading…</div>
      ) : (
        <div className="bg-slate-900 p-4 rounded-lg border border-slate-800 space-y-2">
          <div className="text-4xl font-bold">{data?.score?.toFixed(1)}</div>
          <div className="capitalize">Risk: {data?.risk_level} • Confidence: {Math.round((data?.confidence || 0) * 100)}%</div>
          <div className="text-slate-300">{data?.explanation}</div>
          <div className="text-slate-400 text-sm">Key factors: {(data?.key_factors || []).join(', ')}</div>
        </div>
      )}
    </div>
  );
} 