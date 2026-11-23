
import { useState } from "react";
import { ArrowLeft, Sparkles, LoaderCircle } from "lucide-react";
import "./CreateCampaign.css";

const platformOptions = [
  "Instagram",
  "YouTube",
  "Facebook",
  "Google Ads",
  "LinkedIn",
  "Snapchat"
];

function CreateCampaign({ onBack }) {
  const [form, setForm] = useState({
    product_name: "",
    target_audience: "",
    budget: "",
    objective: "BRAND_AWARENESS",
    platforms: ["Instagram", "YouTube", "Facebook"]
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value
    }));
  }

  function handlePlatformChange(platform) {
    setForm((previous) => ({
      ...previous,
      platforms: previous.platforms.includes(platform)
        ? previous.platforms.filter((item) => item !== platform)
        : [...previous.platforms, platform]
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/campaigns", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ...form,
          budget: Number(form.budget)
        })
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
    } catch (err) {
      setError(err.message || "Something went wrong.");
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
          <Sparkles size={14} /> AI CAMPAIGN GENERATOR
        </span>
        <h1>Create a Campaign</h1>
        <p>
          Describe your campaign. AdPilot's AI agent will
          build an advertising strategy for you.
        </p>
      </div>

      <form className="campaign-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Product Name</label>
          <input
            name="product_name"
            value={form.product_name}
            onChange={handleChange}
            placeholder="e.g. Smartphone"
            required
          />
        </div>

        <div className="form-group">
          <label>Target Audience</label>
          <input
            name="target_audience"
            value={form.target_audience}
            onChange={handleChange}
            placeholder="e.g. 18-30 year olds in India"
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
            placeholder="e.g. 500000"
            min="1"
            step="0.01"
            required
          />
        </div>

        <div className="form-group">
          <label>Campaign Objective</label>
          <select
            name="objective"
            value={form.objective}
            onChange={handleChange}
          >
            <option value="BRAND_AWARENESS">Brand Awareness</option>
            <option value="LEAD_GENERATION">Lead Generation</option>
            <option value="SALES">Sales</option>
            <option value="WEBSITE_TRAFFIC">Website Traffic</option>
          </select>
        </div>

        <div className="form-group">
          <label>Allowed Advertising Platforms</label>
          <p className="field-hint">
            Select the platforms the AI agent can use.
          </p>

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

        {error && <div className="error-message">{error}</div>}

        <button
          className="generate-btn"
          type="submit"
          disabled={loading || form.platforms.length === 0}
        >
          {loading ? (
            <>
              <LoaderCircle className="spin" size={18} />
              Generating Strategy...
            </>
          ) : (
            <>
              <Sparkles size={18} />
              Generate Campaign Strategy
            </>
          )}
        </button>
      </form>

      {result && (
        <section className="result-card">
          <span className="success-label">CAMPAIGN GENERATED</span>
          <h2>Campaign Strategy</h2>

          <p>{result.strategy.summary}</p>

          <h3>Recommended Platforms</h3>
          <div className="result-platforms">
            {result.strategy.recommended_platforms.map((platform) => (
              <span key={platform}>{platform}</span>
            ))}
          </div>

          <h3>Budget Allocation</h3>
          {result.strategy.budget_allocation.map((item) => (
            <div className="allocation-row" key={item.platform}>
              <strong>{item.platform}</strong>
              <span>
                ₹{Number(item.amount).toLocaleString("en-IN")}
              </span>
              <p>{item.reason}</p>
            </div>
          ))}

          <h3>Generated Ad Copy</h3>
          {result.strategy.ad_copy.map((copy, index) => (
            <p className="ad-copy" key={index}>{copy}</p>
          ))}
        </section>
      )}
    </main>
  );
}

export default CreateCampaign;
