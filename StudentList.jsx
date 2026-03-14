export default function StudentList({ students, RISK_COLOR }) {
  const sorted = [...(students || [])].sort((a, b) => b.risk_score - a.risk_score);

  return (
    <div>
      <h2 style={{ color: "#fff", marginBottom: 8 }}>All Students</h2>
      <p style={{ color: "#94a3b8", marginBottom: 24 }}>{sorted.length} students tracked</p>
      <div style={{ display: "grid", gap: 12 }}>
        {sorted.map(s => (
          <div key={s.student_id} style={{ background: "#1a1d2e", borderRadius: 12, padding: "20px 24px", display: "flex", alignItems: "center", gap: 20, border: `1px solid ${RISK_COLOR[s.risk_level]}15` }}>
            <div style={{ width: 48, height: 48, borderRadius: 12, background: RISK_COLOR[s.risk_level] + "20", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>
              {s.risk_level === "Critical" ? "🚨" : s.risk_level === "High" ? "⚠️" : s.risk_level === "Medium" ? "🟡" : "✅"}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, color: "#fff", fontSize: 15 }}>{s.name || "Unknown"}</div>
              <div style={{ color: "#94a3b8", fontSize: 12 }}>{s.student_id} · Updated {new Date(s.last_updated).toLocaleDateString()}</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: RISK_COLOR[s.risk_level] }}>{s.risk_score}</div>
              <span style={{ fontSize: 11, padding: "2px 10px", borderRadius: 10, background: RISK_COLOR[s.risk_level] + "20", color: RISK_COLOR[s.risk_level] }}>{s.risk_level}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
