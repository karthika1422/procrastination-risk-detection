export default function Dashboard({ stats, students, RISK_COLOR, onNavigate }) {
  if (!stats) return <div style={{ color: "#94a3b8", textAlign: "center", padding: 80 }}>Loading...</div>;

  const statCards = [
    { label: "Total Students", value: stats.total_students, icon: "👥", color: "#6366f1" },
    { label: "Avg Risk Score", value: stats.avg_risk_score, icon: "📊", color: "#f59e0b" },
    { label: "High / Critical", value: stats.high_risk_count, icon: "🚨", color: "#ef4444" },
    { label: "Low Risk", value: stats.risk_distribution?.Low || 0, icon: "✅", color: "#22c55e" },
  ];

  const sortedStudents = [...(students || [])].sort((a, b) => b.risk_score - a.risk_score).slice(0, 5);

  return (
    <div>
      <h2 style={{ color: "#fff", marginBottom: 8 }}>Overview Dashboard</h2>
      <p style={{ color: "#94a3b8", marginBottom: 32 }}>Real-time behavioral risk monitoring across all enrolled students.</p>

      {/* Stat cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {statCards.map((c, i) => (
          <div key={i} style={{ background: "#1a1d2e", borderRadius: 14, padding: 24, border: `1px solid ${c.color}20` }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>{c.icon}</div>
            <div style={{ fontSize: 32, fontWeight: 800, color: c.color }}>{c.value}</div>
            <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>{c.label}</div>
          </div>
        ))}
      </div>

      {/* Risk distribution bar */}
      <div style={{ background: "#1a1d2e", borderRadius: 14, padding: 24, marginBottom: 24 }}>
        <h3 style={{ margin: "0 0 16px", color: "#fff" }}>Risk Distribution</h3>
        <div style={{ display: "flex", gap: 4, height: 40, borderRadius: 8, overflow: "hidden" }}>
          {Object.entries(stats.risk_distribution || {}).map(([level, count]) => {
            const pct = stats.total_students > 0 ? (count / stats.total_students) * 100 : 0;
            return pct > 0 ? (
              <div key={level} style={{ flex: pct, background: RISK_COLOR[level], display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: "#fff", minWidth: 40 }} title={`${level}: ${count}`}>
                {count > 0 && `${level} (${count})`}
              </div>
            ) : null;
          })}
        </div>
        <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
          {Object.entries(RISK_COLOR).map(([level, color]) => (
            <span key={level} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "#94a3b8" }}>
              <span style={{ width: 10, height: 10, borderRadius: 2, background: color, display: "inline-block" }} />{level}
            </span>
          ))}
        </div>
      </div>

      {/* Top at-risk students */}
      <div style={{ background: "#1a1d2e", borderRadius: 14, padding: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h3 style={{ margin: 0, color: "#fff" }}>Top At-Risk Students</h3>
          <button onClick={() => onNavigate("students")} style={{ background: "transparent", border: "1px solid #374151", color: "#94a3b8", padding: "6px 14px", borderRadius: 8, cursor: "pointer", fontSize: 12 }}>
            View All →
          </button>
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ color: "#6b7280", fontSize: 12 }}>
              {["Student", "ID", "Risk Score", "Level", "Last Active"].map(h => (
                <th key={h} style={{ textAlign: "left", padding: "8px 12px", borderBottom: "1px solid #2d3748" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedStudents.map((s) => (
              <tr key={s.student_id} style={{ borderBottom: "1px solid #1f2937" }}>
                <td style={{ padding: "12px", color: "#fff", fontWeight: 500 }}>{s.name || "—"}</td>
                <td style={{ padding: "12px", color: "#94a3b8", fontSize: 12 }}>{s.student_id}</td>
                <td style={{ padding: "12px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ flex: 1, background: "#0f1117", borderRadius: 4, height: 6 }}>
                      <div style={{ width: `${s.risk_score}%`, height: "100%", background: RISK_COLOR[s.risk_level], borderRadius: 4 }} />
                    </div>
                    <span style={{ color: RISK_COLOR[s.risk_level], fontWeight: 700, fontSize: 13, minWidth: 30 }}>{s.risk_score}</span>
                  </div>
                </td>
                <td style={{ padding: "12px" }}>
                  <span style={{ padding: "3px 10px", borderRadius: 12, fontSize: 11, fontWeight: 600, background: RISK_COLOR[s.risk_level] + "20", color: RISK_COLOR[s.risk_level] }}>
                    {s.risk_level}
                  </span>
                </td>
                <td style={{ padding: "12px", color: "#6b7280", fontSize: 12 }}>{new Date(s.last_updated).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
