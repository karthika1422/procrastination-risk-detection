import { useState } from "react";

const FIELDS = [
  { key: "student_id", label: "Student ID (optional)", type: "text", placeholder: "e.g. STU0042", required: false, min: null, max: null, step: null },
  { key: "days_since_last_study", label: "Days Since Last Study Session", type: "number", placeholder: "0–14", required: true, min: 0, max: 14, step: 0.5, help: "How many days ago was the last session?" },
  { key: "avg_session_duration", label: "Avg Study Session Duration (minutes)", type: "number", placeholder: "10–180", required: true, min: 0, max: 480, step: 5, help: "Average focus time per session" },
  { key: "task_completion_rate", label: "Task Completion Rate (0–1)", type: "number", placeholder: "0.0–1.0", required: true, min: 0, max: 1, step: 0.05, help: "Proportion of assigned tasks completed" },
  { key: "deadline_proximity_avg", label: "Avg Days Before Deadline at Submission", type: "number", placeholder: "0–14", required: true, min: 0, max: 14, step: 0.5, help: "Higher = better (submitting early)" },
  { key: "idle_ratio", label: "Idle / Distraction Ratio (0–1)", type: "number", placeholder: "0.0–1.0", required: true, min: 0, max: 1, step: 0.05, help: "Proportion of session time spent idle or distracted" },
  { key: "sessions_this_week", label: "Study Sessions This Week", type: "number", placeholder: "0–21", required: true, min: 0, max: 21, step: 1, help: "Number of sessions in the past 7 days" },
  { key: "missed_deadlines_count", label: "Missed Deadlines (this semester)", type: "number", placeholder: "0–20", required: true, min: 0, max: 20, step: 1 },
  { key: "self_reported_stress", label: "Self-Reported Stress Level (1–10)", type: "number", placeholder: "1–10", required: true, min: 1, max: 10, step: 0.5, help: "1 = relaxed, 10 = overwhelmed" },
];

const DEFAULT = {
  student_id: "",
  days_since_last_study: "",
  avg_session_duration: "",
  task_completion_rate: "",
  deadline_proximity_avg: "",
  idle_ratio: "",
  sessions_this_week: "",
  missed_deadlines_count: "",
  self_reported_stress: "",
};

export default function RiskForm({ onSubmit, loading }) {
  const [form, setForm] = useState(DEFAULT);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const e = {};
    FIELDS.filter(f => f.required).forEach(f => {
      const v = parseFloat(form[f.key]);
      if (form[f.key] === "" || isNaN(v)) e[f.key] = "Required";
      else if (f.min !== null && v < f.min) e[f.key] = `Min ${f.min}`;
      else if (f.max !== null && v > f.max) e[f.key] = `Max ${f.max}`;
    });
    return e;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    const payload = {};
    FIELDS.forEach(f => {
      if (f.key === "student_id") { if (form[f.key]) payload[f.key] = form[f.key]; }
      else payload[f.key] = parseFloat(form[f.key]);
    });
    onSubmit(payload);
  };

  const fillDemo = () => {
    setForm({
      student_id: "STU_DEMO",
      days_since_last_study: "5",
      avg_session_duration: "45",
      task_completion_rate: "0.50",
      deadline_proximity_avg: "0.8",
      idle_ratio: "0.42",
      sessions_this_week: "2",
      missed_deadlines_count: "3",
      self_reported_stress: "7.5",
    });
    setErrors({});
  };

  return (
    <div style={{ maxWidth: 680, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 32 }}>
        <div>
          <h2 style={{ color: "#fff", margin: "0 0 8px" }}>Predict Risk Score</h2>
          <p style={{ color: "#94a3b8", margin: 0 }}>Enter student behavioral data to get an instant risk assessment.</p>
        </div>
        <button onClick={fillDemo} style={{ background: "#1a1d2e", border: "1px solid #374151", color: "#94a3b8", padding: "8px 16px", borderRadius: 8, cursor: "pointer", fontSize: 12 }}>
          Load Demo Data
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
          {FIELDS.map(f => (
            <div key={f.key} style={{ gridColumn: f.key === "student_id" ? "1/-1" : "auto" }}>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#94a3b8", marginBottom: 6 }}>
                {f.label} {f.required && <span style={{ color: "#ef4444" }}>*</span>}
              </label>
              <input
                type={f.type}
                placeholder={f.placeholder}
                value={form[f.key]}
                min={f.min ?? undefined}
                max={f.max ?? undefined}
                step={f.step ?? undefined}
                onChange={e => { setForm({ ...form, [f.key]: e.target.value }); setErrors({ ...errors, [f.key]: null }); }}
                style={{
                  width: "100%", padding: "10px 14px", background: "#1a1d2e", border: `1px solid ${errors[f.key] ? "#ef4444" : "#2d3748"}`,
                  borderRadius: 8, color: "#e2e8f0", fontSize: 14, outline: "none", boxSizing: "border-box"
                }}
              />
              {f.help && <div style={{ fontSize: 11, color: "#4b5563", marginTop: 4 }}>{f.help}</div>}
              {errors[f.key] && <div style={{ fontSize: 11, color: "#ef4444", marginTop: 4 }}>{errors[f.key]}</div>}
            </div>
          ))}
        </div>

        <button type="submit" disabled={loading}
          style={{ marginTop: 32, width: "100%", padding: 16, background: loading ? "#374151" : "linear-gradient(135deg,#6366f1,#8b5cf6)", border: "none", borderRadius: 12, color: "#fff", fontSize: 16, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer" }}>
          {loading ? "Analyzing..." : "🔍 Analyze Risk"}
        </button>
      </form>
    </div>
  );
}
