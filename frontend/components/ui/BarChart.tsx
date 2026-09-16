type BarraDato = {
  label: string;
  value: number;
  color?: string;
  href?: string;
};

export default function BarChart({
  data,
  valueFormatter = (v) => String(v),
  color = "var(--blue)",
  orientation = "horizontal",
}: {
  data: BarraDato[];
  valueFormatter?: (v: number) => string;
  color?: string;
  orientation?: "horizontal" | "vertical";
}) {
  if (data.length === 0) return null;
  const max = Math.max(...data.map((d) => d.value), 1);

  if (orientation === "vertical") {
    return (
      <div style={{ display: "flex", alignItems: "flex-end", gap: 16, height: 240, paddingTop: 24 }}>
        {data.map((d, index) => (
          <div
            key={`${d.label}-${index}`}
            style={{
              flex: 1,
              minWidth: 0,
              height: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "flex-end",
            }}
          >
            <strong style={{ fontSize: 13, marginBottom: 6, whiteSpace: "nowrap" }}>
              {valueFormatter(d.value)}
            </strong>
            <div
              style={{
                width: "60%",
                background: d.color ?? color,
                height: `${Math.max((d.value / max) * 100, 2)}%`,
                borderRadius: "6px 6px 0 0",
                transition: "height 0.3s ease",
              }}
            />
            <span
              style={{
                marginTop: 8,
                fontSize: 13,
                fontWeight: 600,
                textAlign: "center",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                maxWidth: "100%",
              }}
              title={d.label}
            >
              {d.label}
            </span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {data.map((d, index) => (
        <div key={`${d.label}-${index}`} style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span
            style={{
              width: 160,
              flex: "0 0 160px",
              fontWeight: 600,
              fontSize: 14,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            title={d.label}
          >
            {d.label}
          </span>
          <div style={{ flex: 1, background: "var(--bg)", borderRadius: 6, overflow: "hidden", height: 22 }}>
            <div
              style={{
                width: `${Math.max((d.value / max) * 100, 2)}%`,
                background: d.color ?? color,
                height: "100%",
                borderRadius: 6,
                transition: "width 0.3s ease",
              }}
            />
          </div>
          <strong style={{ width: 90, flex: "0 0 90px", textAlign: "right", fontSize: 14 }}>
            {valueFormatter(d.value)}
          </strong>
        </div>
      ))}
    </div>
  );
}
