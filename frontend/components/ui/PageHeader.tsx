export default function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className="topbar">
      <div>
        <h1>{title}</h1>
        {subtitle && <span className="crumb">{subtitle}</span>}
      </div>
      {actions && <div className="row-actions">{actions}</div>}
    </div>
  );
}
