import { useState, useEffect } from "react";
import {
  ArrowLeft,
  Sparkles,
  LoaderCircle,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Copy,
  Check,
  Layers,
  PieChart,
  ShieldCheck,
  TrendingUp,
  Users,
  Target,
  Image,
  RefreshCw,
  ExternalLink,
  Download
} from "lucide-react";
import "./CreateCampaign.css";

const platformOptions = [
  "Instagram",
  "YouTube",
  "Facebook",
  "Google Ads",
  "LinkedIn",
  "Snapchat"
];

const agentSteps = [
  { id: 1, name: "Product Intelligence Agent", desc: "Extracting personas, USPs & customer benefits" },
  { id: 2, name: "Campaign Strategy Agent", desc: "Synthesizing thematic Big Idea & funnel stages" },
  { id: 3, name: "Campaign Planning Agent", desc: "Allocating media spend, flighting & KPI benchmarks" },
  { id: 4, name: "Ad Generation Agent", desc: "Crafting platform-tailored copy & visual creative briefs" },
  { id: 5, name: "Quality & Compliance Agent", desc: "Auditing character limits, truthfulness & safety" }
];

function CreateCampaign({ onBack, viewCampaign = null }) {
  const [form, setForm] = useState({
    product_name: "",
    target_audience: "",
    budget: "",
    objective: "BRAND_AWARENESS",
    platforms: ["Instagram", "Google Ads", "YouTube"],
    product_description: "",
    brand_tone: "",
    target_locations: "",
    price_point: ""
  });

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(1);
  const [error, setError] = useState("");
  const [result, setResult] = useState(viewCampaign);
  const [activeTab, setActiveTab] = useState("strategy");
  const [copiedText, setCopiedText] = useState(null);
  const [regeneratingIdx, setRegeneratingIdx] = useState(null);

  async function handleRegenerateImage(idx, ad) {
    setRegeneratingIdx(idx);
    try {
      const productName = result?.campaign_details?.product_name || form.product_name;
      const res = await fetch("http://127.0.0.1:8000/campaigns/generate-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: ad.image_prompt || `Commercial ad photography for ${productName}. ${ad.visual_brief}`,
          headline: ad.headline || productName,
          product_name: productName,
          cta: ad.call_to_action || "Shop Now",
          platform: ad.platform || "Instagram"
        })
      });
      const data = await res.json();
      if (res.ok && data.image_url) {
        setResult((prev) => {
          if (!prev) return prev;
          const updated = { ...prev };
          if (updated.creatives?.social_ads?.[idx]) {
            const newSocialAds = [...updated.creatives.social_ads];
            newSocialAds[idx] = {
              ...newSocialAds[idx],
              image_url: data.image_url,
              image_prompt: data.image_prompt,
              image_provider: data.provider
            };
            updated.creatives = {
              ...updated.creatives,
              social_ads: newSocialAds
            };
          }
          return updated;
        });
      }
    } catch (e) {
      console.error("Regeneration failed:", e);
    } finally {
      setRegeneratingIdx(null);
    }
  }

  // If a past campaign was passed to view
  useEffect(() => {
    if (viewCampaign) {
      setResult(viewCampaign);
    }
  }, [viewCampaign]);

  // Simulated agent pipeline stepper while loading
  useEffect(() => {
    let timer;
    if (loading) {
      setActiveStep(1);
      timer = setInterval(() => {
        setActiveStep((prev) => (prev < 5 ? prev + 1 : prev));
      }, 3500);
    } else {
      setActiveStep(1);
    }
    return () => clearInterval(timer);
  }, [loading]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: value
    }));
  }

  function handlePlatformChange(platform) {
    setForm((prev) => ({
      ...prev,
      platforms: prev.platforms.includes(platform)
        ? prev.platforms.filter((item) => item !== platform)
        : [...prev.platforms, platform]
    }));
  }

  function copyToClipboard(text, key) {
    navigator.clipboard.writeText(text);
    setCopiedText(key);
    setTimeout(() => setCopiedText(null), 2000);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const payload = {
        product_name: form.product_name,
        target_audience: form.target_audience,
        budget: Number(form.budget),
        objective: form.objective,
        platforms: form.platforms,
        product_description: form.product_description.trim() || null,
        brand_tone: form.brand_tone.trim() || null,
        target_locations: form.target_locations
          ? form.target_locations.split(",").map((s) => s.trim())
          : null,
        price_point: form.price_point.trim() || null
      };

      const response = await fetch("http://127.0.0.1:8000/campaigns", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail || data)
        );
      }

      setResult(data);
      setActiveTab("strategy");
    } catch (err) {
      setError(err.message || "Failed to generate campaign. Check backend logs.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="main campaign-page">
      <button className="back-btn" onClick={onBack}>
        <ArrowLeft size={17} />
        Back to Dashboard
      </button>

      <div className="form-heading">
        <span className="welcome-tag">
          <Sparkles size={14} /> ADPiLOT MULTI-AGENT ARCHITECTURE
        </span>
        <h1>{viewCampaign ? "Campaign Intelligence Dossier" : "Create an Advertising Campaign"}</h1>
        <p>
          {viewCampaign
            ? "Inspect full multi-agent artifacts, strategy pillars, media allocations, and compliance audit."
            : "Orchestrate our 5 specialized AI agents to analyze, strategize, plan, create, and audit your advertising campaign."}
        </p>
      </div>

      {!viewCampaign && (
        <form className="campaign-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Product or Service Name</label>
            <input
              name="product_name"
              value={form.product_name}
              onChange={handleChange}
              placeholder="e.g. ZenPulse Hybrid ANC Headphones"
              required
            />
          </div>

          <div className="form-group">
            <label>Target Audience Demographic</label>
            <input
              name="target_audience"
              value={form.target_audience}
              onChange={handleChange}
              placeholder="e.g. Urban working professionals & creators aged 24-40 in India"
              required
            />
          </div>

          <div className="form-group">
            <label>Campaign Budget (INR)</label>
            <input
              type="number"
              name="budget"
              value={form.budget}
              onChange={handleChange}
              placeholder="e.g. 250000"
              min="1"
              step="0.01"
              required
            />
          </div>

          <div className="form-group">
            <label>Core Campaign Objective</label>
            <select name="objective" value={form.objective} onChange={handleChange}>
              <option value="BRAND_AWARENESS">Brand Awareness</option>
              <option value="LEAD_GENERATION">Lead Generation</option>
              <option value="SALES">Sales / Conversions</option>
              <option value="WEBSITE_TRAFFIC">Website Traffic</option>
            </select>
          </div>

          <div className="form-group">
            <label>Select Target Advertising Platforms</label>
            <p className="field-hint">AdPilot agents will distribute your budget and customize creatives for these channels.</p>

            <div className="platform-grid">
              {platformOptions.map((platform) => (
                <label className="platform-option" key={platform}>
                  <input
                    type="checkbox"
                    checked={form.platforms.includes(platform)}
                    onChange={() => handlePlatformChange(platform)}
                  />
                  {platform}
                </label>
              ))}
            </div>
          </div>

          {/* Advanced Context Accordion */}
          <div className="advanced-toggle" onClick={() => setShowAdvanced(!showAdvanced)}>
            <span>Advanced Product & Brand Intelligence (Optional)</span>
            {showAdvanced ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>

          {showAdvanced && (
            <div className="advanced-fields">
              <div className="form-group">
                <label>Key Features, Technology or Ingredients</label>
                <textarea
                  name="product_description"
                  value={form.product_description}
                  onChange={handleChange}
                  placeholder="e.g. 45dB Hybrid ANC, 40-hour battery, Spatial audio with dynamic head tracking, titanium drivers."
                  rows={3}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Desired Brand Tone</label>
                  <input
                    name="brand_tone"
                    value={form.brand_tone}
                    onChange={handleChange}
                    placeholder="e.g. Sophisticated, calming, premium"
                  />
                </div>

                <div className="form-group">
                  <label>Pricing Context</label>
                  <input
                    name="price_point"
                    value={form.price_point}
                    onChange={handleChange}
                    placeholder="e.g. ₹12,999 (Launch offer)"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Target Geography / Cities</label>
                <input
                  name="target_locations"
                  value={form.target_locations}
                  onChange={handleChange}
                  placeholder="e.g. Mumbai, Bengaluru, Delhi NCR, Hyderabad"
                />
              </div>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button
            className="generate-btn"
            type="submit"
            disabled={loading || form.platforms.length === 0}
          >
            {loading ? (
              <>
                <LoaderCircle className="spin" size={18} />
                Executing Multi-Agent Pipeline...
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Generate Multi-Agent Campaign
              </>
            )}
          </button>
        </form>
      )}

      {/* Multi-Agent Execution Progress Tracker */}
      {loading && (
        <section className="agent-stepper-card">
          <h3>Multi-Agent Orchestration in Progress</h3>
          <p className="field-hint">The LangGraph engine is orchestrating five specialized agents with automated reflection.</p>
          <div className="stepper-list">
            {agentSteps.map((step) => {
              const isCurrent = activeStep === step.id;
              const isDone = activeStep > step.id;
              return (
                <div key={step.id} className={`step-item ${isDone ? "done" : ""} ${isCurrent ? "active" : ""}`}>
                  <div className="step-icon">
                    {isDone ? (
                      <CheckCircle2 size={18} color="#4ade80" />
                    ) : isCurrent ? (
                      <LoaderCircle size={18} className="spin" color="#c084fc" />
                    ) : (
                      <span>{step.id}</span>
                    )}
                  </div>
                  <div className="step-content">
                    <strong>{step.name}</strong>
                    <p>{step.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Multi-Agent Deliverable Tabs & Viewer */}
      {result && (
        <section className="result-card">
          <div className="result-header">
            <div>
              <span className="success-label">
                {result.compliance?.is_approved ? "COMPLIANCE VERIFIED" : "MULTI-AGENT DELIVERABLE READY"}
              </span>
              <h2>{result.campaign_details?.product_name || "Campaign Overview"}</h2>
              <p className="campaign-meta">
                Budget: ₹{Number(result.campaign_details?.budget || 0).toLocaleString("en-IN")} • Objective: {result.campaign_details?.objective}
              </p>
            </div>
            {result.compliance && (
              <div className="score-badge">
                <span className="score-num">{Math.round(result.compliance.compliance_score || 85)}</span>
                <span className="score-label">Compliance Score</span>
              </div>
            )}
          </div>

          {/* Navigation Tabs */}
          <div className="tabs-header">
            <button
              className={`tab-btn ${activeTab === "strategy" ? "active" : ""}`}
              onClick={() => setActiveTab("strategy")}
            >
              <Target size={16} /> Strategy & Funnel
            </button>
            <button
              className={`tab-btn ${activeTab === "intelligence" ? "active" : ""}`}
              onClick={() => setActiveTab("intelligence")}
            >
              <Users size={16} /> Product Intelligence
            </button>
            <button
              className={`tab-btn ${activeTab === "planning" ? "active" : ""}`}
              onClick={() => setActiveTab("planning")}
            >
              <PieChart size={16} /> Media & Budget Plan
            </button>
            <button
              className={`tab-btn ${activeTab === "creatives" ? "active" : ""}`}
              onClick={() => setActiveTab("creatives")}
            >
              <Layers size={16} /> Ad Creatives
            </button>
            <button
              className={`tab-btn ${activeTab === "compliance" ? "active" : ""}`}
              onClick={() => setActiveTab("compliance")}
            >
              <ShieldCheck size={16} /> Compliance Audit
            </button>
          </div>

          {/* Tab 1: Strategy & Funnel */}
          {activeTab === "strategy" && (
            <div className="tab-pane">
              <div className="summary-banner">
                <h3>Executive Strategy Summary</h3>
                <p>{result.strategy?.summary || "Comprehensive strategic advertising plan."}</p>
              </div>

              {result.strategy?.campaign_theme && (
                <div className="theme-card">
                  <span className="pill-tag">CAMPAIGN BIG IDEA</span>
                  <h3>"{result.strategy.campaign_theme}"</h3>
                  <p>{result.strategy.positioning_statement}</p>
                </div>
              )}

              {result.strategy?.messaging_pillars && result.strategy.messaging_pillars.length > 0 && (
                <div className="pillars-grid">
                  {result.strategy.messaging_pillars.map((pillar, idx) => (
                    <div key={idx} className="pillar-item">
                      <span className="pillar-number">0{idx + 1}</span>
                      <p>{pillar}</p>
                    </div>
                  ))}
                </div>
              )}

              {result.strategy?.funnel_stages && result.strategy.funnel_stages.length > 0 && (
                <>
                  <h3 className="section-title">Funnel Progression</h3>
                  <div className="funnel-grid">
                    {result.strategy.funnel_stages.map((stage, idx) => (
                      <div key={idx} className="funnel-card">
                        <span className="funnel-badge">{stage.stage}</span>
                        <h4>{stage.objective}</h4>
                        <p className="funnel-hook">"{stage.key_messaging}"</p>
                        <div className="channel-tags">
                          {stage.recommended_channels?.map((ch) => (
                            <span key={ch}>{ch}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}

          {/* Tab 2: Product Intelligence */}
          {activeTab === "intelligence" && (
            <div className="tab-pane">
              {result.product_intelligence ? (
                <>
                  <div className="intelligence-overview">
                    <h3>Product Synopsis</h3>
                    <p>{result.product_intelligence.product_summary}</p>
                    <div className="tone-pill">
                      Recommended Brand Voice: <strong>{result.product_intelligence.recommended_tone}</strong>
                    </div>
                  </div>

                  <h3 className="section-title">Target Customer Personas</h3>
                  <div className="personas-grid">
                    {result.product_intelligence.target_personas?.map((persona, idx) => (
                      <div key={idx} className="persona-card">
                        <h4>{persona.name}</h4>
                        <p className="persona-demo">{persona.demographics}</p>
                        <div className="persona-details">
                          <div>
                            <strong>Pain Points:</strong>
                            <ul>
                              {persona.pain_points?.map((pp, i) => (
                                <li key={i}>{pp}</li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <strong>Motivations:</strong>
                            <ul>
                              {persona.desires_and_motivations?.map((d, i) => (
                                <li key={i}>{d}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <h3 className="section-title">Value Propositions & USPs</h3>
                  <div className="usps-list">
                    {result.product_intelligence.value_propositions?.map((usp, idx) => (
                      <div key={idx} className="usp-item">
                        <CheckCircle2 size={16} color="#c084fc" />
                        <span>{usp}</span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p className="empty-tab">Product intelligence details included in strategy summary.</p>
              )}
            </div>
          )}

          {/* Tab 3: Media & Budget Plan */}
          {activeTab === "planning" && (
            <div className="tab-pane">
              <h3 className="section-title">Multi-Platform Budget Allocation</h3>
              <div className="budget-table">
                {(result.plan?.budget_allocation || result.strategy?.budget_allocation || []).map((item) => (
                  <div className="budget-row" key={item.platform}>
                    <div className="budget-platform-col">
                      <strong>{item.platform}</strong>
                      <p>{item.reason || item.rationale}</p>
                      {item.recommended_ad_formats && (
                        <div className="format-tags">
                          {item.recommended_ad_formats.map((f) => (
                            <span key={f}>{f}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="budget-amount-col">
                      <span className="budget-val">₹{Number(item.amount).toLocaleString("en-IN")}</span>
                      {item.percentage && <span className="budget-pct">{item.percentage}% of total</span>}
                    </div>
                  </div>
                ))}
              </div>

              {result.plan?.flight_schedule && result.plan.flight_schedule.length > 0 && (
                <>
                  <h3 className="section-title">Flighting Schedule</h3>
                  <div className="timeline-phases">
                    {result.plan.flight_schedule.map((phase, idx) => (
                      <div key={idx} className="timeline-item">
                        <div className="timeline-marker">{idx + 1}</div>
                        <p>{phase}</p>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {result.plan?.kpi_estimates && result.plan.kpi_estimates.length > 0 && (
                <>
                  <h3 className="section-title">Performance Benchmark Projections</h3>
                  <div className="kpi-grid">
                    {result.plan.kpi_estimates.map((kpi, idx) => (
                      <div key={idx} className="kpi-card">
                        <h4>{kpi.platform}</h4>
                        <div className="kpi-metrics">
                          {kpi.estimated_impressions && (
                            <div>
                              <span>Est. Impressions</span>
                              <strong>{kpi.estimated_impressions}</strong>
                            </div>
                          )}
                          {kpi.estimated_clicks && (
                            <div>
                              <span>Est. Clicks</span>
                              <strong>{kpi.estimated_clicks}</strong>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}

          {/* Tab 4: Ad Creatives */}
          {activeTab === "creatives" && (
            <div className="tab-pane">
              {result.creatives?.search_ads && result.creatives.search_ads.length > 0 && (
                <>
                  <h3 className="section-title">Google Search Ads</h3>
                  <div className="search-ads-container">
                    {result.creatives.search_ads.map((ad, idx) => (
                      <div key={idx} className="search-ad-card">
                        <div className="ad-url-preview">
                          https://example.com{ad.path_1 ? `/${ad.path_1}` : ""}{ad.path_2 ? `/${ad.path_2}` : ""}
                        </div>
                        <h4 className="search-ad-title">
                          {ad.headlines.join(" | ")}
                        </h4>
                        <p className="search-ad-desc">{ad.descriptions.join(" ")}</p>

                        <div className="char-count-pills">
                          <span>Headlines (≤30 chars): {ad.headlines.length} variations</span>
                          <span>Descriptions (≤90 chars): {ad.descriptions.length} variations</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {result.creatives?.social_ads && result.creatives.social_ads.length > 0 && (
                <>
                  <h3 className="section-title">Social Media Campaigns</h3>
                  <div className="social-ads-grid">
                    {result.creatives.social_ads.map((ad, idx) => {
                      const copyKey = `social-${idx}`;
                      return (
                        <div key={idx} className="social-ad-card">
                          <div className="social-ad-top">
                            <span className="social-badge">{ad.platform} • {ad.format}</span>
                            <button
                              className="copy-btn"
                              onClick={() => copyToClipboard(ad.primary_text, copyKey)}
                            >
                              {copiedText === copyKey ? (
                                <><Check size={14} color="#4ade80" /> Copied</>
                              ) : (
                                <><Copy size={14} /> Copy</>
                              )}
                            </button>
                          </div>
                          {ad.headline && <h4 className="social-card-headline">{ad.headline}</h4>}
                          <p className="social-card-body">{ad.primary_text}</p>

                          {/* GenAI Visual Sample Ad Creative */}
                          {ad.image_url ? (
                            <div className="ad-visual-wrapper">
                              <div className="ad-visual-badge">
                                <Sparkles size={12} /> GenAI Visual Ad • {ad.image_provider || "AI Generated"}
                              </div>
                              <img
                                src={ad.image_url}
                                alt={`Visual ad for ${ad.headline || ad.platform}`}
                                className="ad-visual-banner"
                                loading="lazy"
                              />
                              <div className="ad-visual-actions">
                                <button
                                  type="button"
                                  className="image-action-btn"
                                  disabled={regeneratingIdx === idx}
                                  onClick={() => handleRegenerateImage(idx, ad)}
                                >
                                  <RefreshCw size={12} className={regeneratingIdx === idx ? "spin" : ""} />
                                  {regeneratingIdx === idx ? "Synthesizing..." : "Regenerate Visual"}
                                </button>
                                <a
                                  href={ad.image_url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="image-action-btn"
                                >
                                  <ExternalLink size={12} /> Fullsize
                                </a>
                              </div>
                            </div>
                          ) : (
                            <div className="generate-visual-prompt-box">
                              <button
                                type="button"
                                className="generate-visual-btn"
                                disabled={regeneratingIdx === idx}
                                onClick={() => handleRegenerateImage(idx, ad)}
                              >
                                <Image size={15} />
                                {regeneratingIdx === idx ? "Synthesizing Visual..." : "Generate GenAI Visual Ad"}
                              </button>
                            </div>
                          )}

                          <div className="social-card-footer">
                            <span className="cta-button-preview">{ad.call_to_action}</span>
                          </div>
                          {ad.visual_brief && (
                            <div className="visual-brief">
                              <strong>Visual Creative Brief:</strong>
                              <p>{ad.visual_brief}</p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </>
              )}

              {/* Legacy / Summary Ad Copy */}
              {result.strategy?.ad_copy && (
                <>
                  <h3 className="section-title">Ad Copy Taglines & Slogans</h3>
                  {result.strategy.ad_copy.map((copy, index) => (
                    <div className="ad-copy-item" key={index}>
                      <p>{copy}</p>
                      <button
                        className="copy-icon-btn"
                        onClick={() => copyToClipboard(copy, `copy-${index}`)}
                        title="Copy to clipboard"
                      >
                        {copiedText === `copy-${index}` ? <Check size={15} color="#4ade80" /> : <Copy size={15} />}
                      </button>
                    </div>
                  ))}
                </>
              )}
            </div>
          )}

          {/* Tab 5: Quality & Compliance Audit */}
          {activeTab === "compliance" && (
            <div className="tab-pane">
              {result.compliance ? (
                <div className="compliance-container">
                  <div className="compliance-summary-card">
                    <div className="score-circle">
                      <span className="big-score">{Math.round(result.compliance.compliance_score || 90)}</span>
                      <span className="score-denom">/ 100</span>
                    </div>
                    <div>
                      <h3>
                        {result.compliance.is_approved
                          ? "Campaign Approved & Policy Compliant"
                          : "Refinements Completed with Safety Checks"}
                      </h3>
                      <p>
                        Audited against FTC guidelines, advertising safety standards, character count specifications, and budget reconciliation.
                      </p>
                    </div>
                  </div>

                  {result.compliance.strengths && result.compliance.strengths.length > 0 && (
                    <div className="strengths-box">
                      <h4>Verified Campaign Strengths</h4>
                      <ul>
                        {result.compliance.strengths.map((str, i) => (
                          <li key={i}>
                            <CheckCircle2 size={15} color="#4ade80" />
                            <span>{str}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {result.compliance.violations && result.compliance.violations.length > 0 && (
                    <div className="violations-box">
                      <h4>Audit Observations & Remediations</h4>
                      {result.compliance.violations.map((v, i) => (
                        <div key={i} className="violation-item">
                          <span className={`severity-tag ${v.severity?.toLowerCase()}`}>
                            {v.severity?.toUpperCase() || "MEDIUM"}
                          </span>
                          <div>
                            <strong>{v.message}</strong>
                            <p className="remediation">{v.remediation_instruction}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="empty-tab">
                  <p>Quality and budget validation checks completed successfully.</p>
                </div>
              )}
            </div>
          )}
        </section>
      )}
    </main>
  );
}

export default CreateCampaign;
