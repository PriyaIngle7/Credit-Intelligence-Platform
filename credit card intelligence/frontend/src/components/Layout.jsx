import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, Home, Activity, Database, Layers } from 'lucide-react';

const NavItem = ({ to, icon: Icon, label }) => {
  const location = useLocation();
  const active = location.pathname === to;
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
        active ? 'bg-primary-600 text-white' : 'text-slate-300 hover:bg-slate-800'
      }`}
    >
      <Icon size={18} />
      <span className="text-sm font-medium">{label}</span>
    </Link>
  );
};

export default function Layout({ children }) {
  return (
    <div className="min-h-screen grid grid-cols-[260px_1fr]">
      <aside className="bg-slate-900 border-r border-slate-800 p-4 space-y-4">
        <div className="text-xl font-bold flex items-center gap-2">
          <BarChart3 />
          <span>Credit Intel</span>
        </div>
        <nav className="space-y-1">
          <NavItem to="/" icon={Home} label="Dashboard" />
          <NavItem to="/credit-scores" icon={Activity} label="Credit Scores" />
          <NavItem to="/data-ingestion" icon={Database} label="Data Ingestion" />
          <NavItem to="/model-performance" icon={Layers} label="Model Performance" />
        </nav>
      </aside>
      <main className="p-6 bg-slate-950">
        {children}
      </main>
    </div>
  );
} 