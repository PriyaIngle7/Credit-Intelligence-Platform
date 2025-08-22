import React from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

async function fetchSummary() {
  const { data } = await axios.get('/api/v1/credit-scores/dashboard/summary');
  return data;
}

export default function Dashboard() {
  const { data, isLoading } = useQuery(['dashboard-summary'], fetchSummary);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
          <div className="text-slate-400 text-sm">Total Companies</div>
          <div className="text-3xl font-bold">{isLoading ? '…' : data?.total_companies ?? 0}</div>
        </div>
        <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
          <div className="text-slate-400 text-sm">Total Scores</div>
          <div className="text-3xl font-bold">{isLoading ? '…' : data?.total_scores ?? 0}</div>
        </div>
        <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
          <div className="text-slate-400 text-sm">Recent Scores (24h)</div>
          <div className="text-3xl font-bold">{isLoading ? '…' : data?.recent_scores ?? 0}</div>
        </div>
      </div>

      <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
        <div className="text-slate-300 mb-2">Score Trend (example)</div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={[{x: 'T-4', y: 62},{x: 'T-3', y: 64},{x: 'T-2', y: 61},{x: 'T-1', y: 66},{x: 'T', y: 65}]}> 
              <Line type="monotone" dataKey="y" stroke="#60a5fa" strokeWidth={2} />
              <CartesianGrid stroke="#1f2937" strokeDasharray="3 3" />
              <XAxis dataKey="x" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
} 