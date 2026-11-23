
import { useState } from "react";
import CreateCampaign from "./CreateForm";

import {
  LayoutDashboard,
  Megaphone,
  History,
  Settings,
  Plus,
  TrendingUp,
  Wallet,
  Target,
  Sparkles,
  ArrowUpRight
} from "lucide-react";

import "./App.css";

function App() {
  const [page, setPage] = useState("dashboard");

  // Show the Create Campaign page
  if (page === "create") {
    return (
      <CreateCampaign
        onBack={() => setPage("dashboard")}
      />
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2 className="logo">
          <Sparkles size={23} /> AdPilot
        </h2>

        <p className="menu-label">WORKSPACE</p>

        <nav>
          <a className="nav-item active">
            <LayoutDashboard size={19} />
            Dashboard
          </a>

          <a className="nav-item">
            <Megaphone size={19} />
            Campaigns
          </a>

          <a className="nav-item">
            <History size={19} />
            History
          </a>

          <a className="nav-item">
            <Settings size={19} />
            Settings
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="avatar">AI</div>
          <div>
            <strong>AdPilot Workspace</strong>
            <p>AI Marketing Platform</p>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="breadcrumb">Workspace / Overview</p>
            <h1>Dashboard</h1>
          </div>

          <button
            className="create-btn"
            onClick={() => setPage("create")}
          >
            <Plus size={18} />
            Create Campaign
          </button>
        </header>

        <section className="welcome">
          <div>
            <span className="welcome-tag">
              <Sparkles size={14} /> AI POWERED MARKETING
            </span>

            <h2>Your campaigns, intelligently managed.</h2>

            <p>
              Plan, generate and optimize advertising
              campaigns with your AI agent.
            </p>
          </div>

          <Sparkles className="welcome-icon" size={90} />
        </section>

        <section className="stats">
          <StatCard
            icon={<Megaphone />}
            label="Total Campaigns"
            value="0"
            note="Your campaign history"
          />

          <StatCard
            icon={<Wallet />}
            label="Total Budget"
            value="₹0"
            note="Across all campaigns"
          />

          <StatCard
            icon={<Target />}
            label="Active Campaigns"
            value="0"
            note="Campaign overview"
          />

          <StatCard
            icon={<TrendingUp />}
            label="AI Generated"
            value="0"
            note="Strategies created"
          />
        </section>

        <section className="campaign-section">
          <div className="section-heading">
            <div>
              <h2>Recent Campaigns</h2>
              <p>Your latest AI-generated campaigns</p>
            </div>

            <button className="view-btn">
              View all <ArrowUpRight size={16} />
            </button>
          </div>

          <div className="empty-state">
            <div className="empty-icon">
              <Megaphone size={30} />
            </div>

            <h3>No campaigns yet</h3>

            <p>
              Create your first campaign and let
              AdPilot's AI agent do the planning.
            </p>

            <button
              className="create-btn"
              onClick={() => setPage("create")}
            >
              <Plus size={17} />
              Create your first campaign
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

function StatCard({ icon, label, value, note }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <div className="stat-icon">{icon}</div>
      </div>

      <h2>{value}</h2>
      <p>{note}</p>
    </div>
  );
}

export default App;
