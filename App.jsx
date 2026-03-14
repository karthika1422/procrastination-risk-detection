import { useState, useEffect } from "react";
import RiskForm from "./components/RiskForm";
import Dashboard from "./components/Dashboard";
import StudentList from "./components/StudentList";

const API = "http://localhost:8000";

export default function App() {
  const [tab, setTab] = useState("dashboard");
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      const [sRes, stRes] = await Promise.all([
        fetch(`${API}/stats`),
        fetch(`${API}/students`),
      ]);
      setStats(await sRes.json());
      setStudents(await stRes.json());
    } catch {
      // Backend may not be running — use mock data
      setStats({ total_students: 5, avg_risk_score: 58.4, risk_distribution: { Low: 1, Medium: 2, High: 1, Critical: 1 }, high_risk_count: 2 });
      setStudents([
        { student_id: "STU0001", name: "Arjun Sharma", risk_score: 82, risk_level: "Critical", last_updated: new Date().toISOString() },
        { student_id: "STU0002", name: "Priya Patel", risk_score: 12, risk_level: "Low", last_updated: new Date().toISOString() },
        { student_id: "STU0003", name: "Rahul Verma", risk_score: 55, risk_level: "Medium", last_updated: new Date().toISOString() },
        { student_id: "STU0004", name: "Sneha Reddy", risk_score: 91, risk_level: "Critical", last_updated: new Date().toISOString() },
        { student_id: "STU0005", name: "Kiran Rao", risk_score: 28, risk_level: "Low", last_updated: new Date().toISOString() },
      ]);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handlePredict = async (formData) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      setPrediction(data);
      setTab("result");
      fetchData();
    } catch {
      // Demo mode: simulate a prediction
      const score = Math.round(
        (formData.days_since_last_study / 14 * 25) +
        ((1 - formData.task_completion_rate) * 25) +
        (formData.idle_ratio * 20) +
        (formData.missed_deadlines_count / 10 * 15) +
        ((formData.self_reported_stress - 1) / 9 * 15)
      );
      const level = score <= 30 ? "Low" : score <= 60 ? "Medium" : score <= 80 ? "High" : "Critical";
      setPrediction({
        student_id: formData.student_id || "DEMO001",
        risk_score: score,
        risk_level: level,
        risk_probability: score / 100,
        top_risk_factors: ["Demo mode — backend not running"],
        interventions: [
          { title: "Start Backend", description: "Run `uvicorn main:app --reload` in the backend folder.", category: "habit", priority: 1 }
        ],
        timestamp: new Date().toISOString(),
      });
      setTab("result");
    } finally {
      setLoading(false);
    }
  };

  const RISK_COLOR = { Low: "#22c55e", Medium: "#f59e0b", High: "#f97316", Critical: "#ef4444" };

  return (
    <div style={{ minHeight: "100vh", background: "#0f1117", color: "#e2e8f0", fontFamily: "'Inter', sans-serif" }}>
      {/* Header */}
      <header style={{ background: "#1a1d2e", borderBottom: "1px solid #2d3748", padding: "16px 32px", display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ width: 36, height: 36, borderRadius: 8, background: "linear-gradient(135deg,#6366f1,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>🧠</div>
        <div>
          <h1 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: "#fff" }}>ProcrastiDetect</h1>
          <p style={{ margin: 0, fontSize: 12, color: "#94a3b8" }}>Early Risk Detection & Habit Intervention System</p>
        </div>
        <nav style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          {["dashboard", "predict", "students"].map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{ padding: "8px 16px", borderRadius: 8, border: "none", cursor: "pointer", fontSize: 13, fontWeight: 600,
                background: tab === t ? "#6366f1" : "transparent",
                color: tab === t ? "#fff" : "#94a3b8" }}>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </nav>
      </header>

      {/* Content */}
      <main style={{ padding: "32px", maxWidth: 1100, margin: "0 auto" }}>
        {tab === "dashboard" && <Dashboard stats={stats} students={students} RISK_COLOR={RISK_COLOR} onNavigate={setTab} />}
        {tab === "predict" && <RiskForm onSubmit={handlePredict} loading={loading} />}
        {tab === "result" && prediction && <ResultView prediction={prediction} RISK_COLOR={RISK_COLOR} onBack={() => setTab("predict")} />}
        {tab === "students" && <StudentList students={students} RISK_COLOR={RISK_COLOR} />}
      </main>
    </div>
  );
}


function ResultView({ prediction, RISK_COLOR, onBack }) {
  const color = RISK_COLOR[prediction.risk_level] || "#6366f1";
  const percent = prediction.risk_score;

  return (
    <div>
      <button onClick={onBack} style={{ background: "transparent", border: "1px solid #374151", color: "#94a3b8", padding: "8px 16px", borderRadius: 8, cursor: "pointer", marginBottom: 24 }}>
        ← New Prediction
      </button>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* Risk Score Card */}
        <div style={{ background: "#1a1d2e", borderRadius: 16, padding: 32, border: `2px solid ${color}20` }}>
          <h2 style={{ margin: "0 0 24px", color: "#fff" }}>Risk Assessment</h2>
          <div style={{ textAlign: "center", marginBottom: 24 }}>
            <div style={{ fontSize: 72, fontWeight: 800, color, lineHeight: 1 }}>{percent}</div>
            <div style={{ fontSize: 14, color: "#94a3b8", marginTop: 4 }}>/ 100</div>
            <div style={{ display: "inline-block", marginTop: 12, padding: "6px 20px", borderRadius: 20, background: color + "20", color, fontWeight: 700, fontSize: 16 }}>
              {prediction.risk_level} Risk
            </div>
          </div>
          {/* Progress bar */}
          <div style={{ background: "#2d3748", borderRadius: 8, height: 12, overflow: "hidden" }}>
            <div style={{ width: `${percent}%`, height: "100%", background: `linear-gradient(90deg, ${color}80, ${color})`, borderRadius: 8, transition: "width 1s ease" }} />
          </div>
          <div style={{ marginTop: 16, fontSize: 12, color: "#94a3b8" }}>Student: {prediction.student_id}</div>
        </div>

        {/* Risk Factors */}
        <div style={{ background: "#1a1d2e", borderRadius: 16, padding: 32 }}>
          <h2 style={{ margin: "0 0 16px", color: "#fff" }}>⚠️ Top Risk Factors</h2>
          {prediction.top_risk_factors.map((f, i) => (
            <div key={i} style={{ padding: "10px 14px", marginBottom: 8, background: "#0f1117", borderRadius: 8, borderLeft: `3px solid ${color}`, fontSize: 13, color: "#e2e8f0" }}>
              {f}
            </div>
          ))}
        </div>

        {/* Interventions */}
        <div style={{ gridColumn: "1/-1", background: "#1a1d2e", borderRadius: 16, padding: 32 }}>
          <h2 style={{ margin: "0 0 20px", color: "#fff" }}>💡 Recommended Interventions</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(260px,1fr))", gap: 16 }}>
            {prediction.interventions.map((iv, i) => (
              <div key={i} style={{ background: "#0f1117", borderRadius: 12, padding: 20, border: "1px solid #2d3748" }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: "#fff", marginBottom: 8 }}>{iv.title}</div>
                <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.6 }}>{iv.description}</div>
                <div style={{ marginTop: 12 }}>
                  <span style={{ fontSize: 11, padding: "3px 10px", borderRadius: 20, background: "#6366f120", color: "#818cf8" }}>{iv.category}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
