import { useState, useEffect } from "react";
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
  ArrowUpRight,
  Calendar,
  Layers
} from "lucide-react";

import "./App.css";

function App() {
  const [page, setPage] = useState("dashboard");
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCampaign, setSelectedCampaign] = useState(null);

  // Fetch campaigns from backend
  async function fetchCampaigns() {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/campaigns");
      if (res.ok) {
        const data = await res.json();
        setCampaigns(data);
      }
    } catch (err) {
      console.warn("Backend not yet connected or no campaigns found:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchCampaigns();
  }, []);

  // Compute live KPI statistics
  const totalCampaigns = campaigns.length;
  const totalBudget = campaigns.reduce((acc, c) => acc + Number(c.budget || 0), 0);
  const uniquePlatforms = new Set();
  campaigns.forEach((c) => {
    if (Array.isArray(c.platforms)) {
      c.platforms.forEach((p) => uniquePlatforms.add(p));
    }
  });

  function handleOpenCreate() {
    setSelectedCampaign(null);
    setPage("create");
  }

  function handleInspectCampaign(c) {
    setSelectedCampaign({
      campaign_details: {
        product_name: c.product_name,
        target_audience: c.target_audience,
        budget: c.budget,
        objective: c.objective,
        platforms: c.platforms
      },
      strategy: c.strategy,
      product_intelligence: c.product_intelligence,
      plan: c.plan,
      creatives: c.creatives,
      compliance: c.compliance
    });
    setPage("create");
  }

  // Show Create / Dossier View
  if (page === "create") {
    return (
      <CreateCampaign
        viewCampaign={selectedCampaign}
        onBack={() => {
          setSelectedCampaign(null);
          setPage("dashboard");
          fetchCampaigns();
        }}
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
          <a
            className={`nav-item ${page === "dashboard" ? "active" : ""}`}
            onClick={() => setPage("dashboard")}
          >
            <LayoutDashboard size={19} />
            Dashboard
          </a>

          <a
            className={`nav-item ${page === "campaigns" ? "active" : ""}`}
            onClick={() => setPage("dashboard")}
          >
            <Megaphone size={19} />
            Campaigns
          </a>

          <a className="nav-item">
            <History size={19} />
            Multi-Agent Logs
          </a>

          <a className="nav-item">
            <Settings size={19} />
            Settings
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="avatar">AI</div>
          <div>
            <strong>AdPilot 5-Agent Suite</strong>
            <p>LangGraph Orchestration</p>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="breadcrumb">Workspace / Multi-Agent Overview</p>
            <h1>Advertising Operations Dashboard</h1>
          </div>

          <button className="create-btn" onClick={handleOpenCreate}>
            <Plus size={18} />
            Create Campaign
          </button>
        </header>

        <section className="welcome">
          <div>
            <span className="welcome-tag">
              <Sparkles size={14} /> FIVE-AGENT AUTONOMOUS ARCHITECTURE
            </span>

            <h2>AI advertising, engineered for precision.</h2>

            <p>
              Product Intelligence • Campaign Strategy • Media Planning • Native Ad Generation • Compliance Auditing.
            </p>
          </div>

          <Sparkles className="welcome-icon" size={90} />
        </section>

        <section className="stats">
          <StatCard
            icon={<Megaphone />}
            label="Total Campaigns"
            value={totalCampaigns.toString()}
            note="Saved campaigns"
          />

          <StatCard
            icon={<Wallet />}
            label="Total Planned Budget"
            value={`₹${totalBudget.toLocaleString("en-IN")}`}
            note="Optimized across media plans"
          />

          <StatCard
            icon={<Target />}
            label="Active Media Channels"
            value={uniquePlatforms.size > 0 ? uniquePlatforms.size.toString() : "0"}
            note="Google, Meta, YouTube & more"
          />

          <StatCard
            icon={<TrendingUp />}
            label="AI Strategies Generated"
            value={totalCampaigns.toString()}
            note="Multi-agent dossiers compiled"
          />
        </section>

        <section className="campaign-section">
          <div className="section-heading">
            <div>
              <h2>Recent AI Campaigns</h2>
              <p>Generated campaigns and compliance audit dossiers</p>
            </div>

            <button className="view-btn" onClick={fetchCampaigns}>
              Refresh <ArrowUpRight size={16} />
            </button>
          </div>

          {campaigns.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">
                <Megaphone size={30} />
              </div>

              <h3>No campaigns generated yet</h3>

              <p>
                Launch your first campaign and let AdPilot's five specialized agents build your complete media strategy and creatives.
              </p>

              <button className="create-btn" onClick={handleOpenCreate}>
                <Plus size={17} />
                Create your first campaign
              </button>
            </div>
          ) : (
            <div className="campaigns-grid">
              {campaigns.map((c) => (
                <div
                  key={c.id}
                  className="campaign-card"
                  onClick={() => handleInspectCampaign(c)}
                >
                  <div className="campaign-card-header">
                    <span className="campaign-obj-badge">{c.objective}</span>
                    <span className="campaign-date">
                      <Calendar size={13} />
                      {c.created_at ? new Date(c.created_at).toLocaleDateString() : "Recent"}
                    </span>
                  </div>

                  <h3>{c.product_name}</h3>
                  <p className="campaign-audience">Target: {c.target_audience}</p>

                  <div className="campaign-budget-row">
                    <span className="budget-label">Budget</span>
                    <span className="budget-figure">
                      ₹{Number(c.budget).toLocaleString("en-IN")}
                    </span>
                  </div>

                  {c.strategy?.summary && (
                    <p className="campaign-excerpt">
                      {c.strategy.summary.slice(0, 110)}...
                    </p>
                  )}

                  <div className="campaign-card-footer">
                    <div className="campaign-platforms-pills">
                      {Array.isArray(c.platforms) &&
                        c.platforms.slice(0, 3).map((p) => <span key={p}>{p}</span>)}
                      {Array.isArray(c.platforms) && c.platforms.length > 3 && (
                        <span>+{c.platforms.length - 3}</span>
                      )}
                    </div>
                    <button className="inspect-btn">
                      Inspect Dossier <ArrowUpRight size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
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
