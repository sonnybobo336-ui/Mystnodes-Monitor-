import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/useApi";
import { useCountdown } from "@/hooks/useCountdown";
import { fmtNum, fmtUSD } from "@/lib/api";
import { TrendingUp, Wallet, Server, Clock, Activity, Sparkles } from "lucide-react";

export function KpiRow({ refreshKey }) {
    const { data, loading } = useApi(`/earnings/summary?_=${refreshKey}`, { intervalMs: 60_000 });
    const { data: wState } = useApi(`/withdrawal/state?_=${refreshKey}`, { intervalMs: 60_000 });
    const d = data?.derived || {};
    const countdown = useCountdown(wState?.next_run_at);

    const cards = [
        {
            id: "kpi-earnings-24h",
            label: "Earnings 24h",
            icon: TrendingUp,
            valueUsd: d.earnings_24h_usd,
            valueMyst: d.earnings_24h_myst,
        },
        {
            id: "kpi-earnings-30d",
            label: "Earnings 30d",
            icon: Activity,
            valueUsd: d.earnings_30d_usd,
            valueMyst: d.earnings_30d_myst,
        },
        {
            id: "kpi-earnings-projected-annual",
            label: "Projected Annual",
            icon: Sparkles,
            valueUsd: d.projected_annual_usd,
            valueMyst: d.projected_annual_myst,
        },
        {
            id: "kpi-earnings-lifetime",
            label: "Lifetime",
            icon: Wallet,
            valueUsd: d.earnings_lifetime_usd,
            valueMyst: d.earnings_lifetime_myst,
        },
        {
            id: "kpi-nodes-online",
            label: "Nodes Online",
            icon: Server,
            valueText: `${d.nodes_online ?? 0} / ${d.nodes_total ?? 0}`,
            sub: `Avg uptime ${d.avg_uptime_pct ?? 0}%`,
        },
        {
            id: "kpi-next-auto-withdrawal",
            label: "Next Auto-Withdrawal",
            icon: Clock,
            valueText: countdown,
            sub: `Threshold ${wState?.threshold_myst ?? 5} MYST`,
        },
    ];

    return (
        <div
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3"
            data-testid="kpi-row"
        >
            {cards.map((c) => (
                <KpiCard key={c.id} {...c} loading={loading} />
            ))}
        </div>
    );
}

function KpiCard({ id, label, icon: Icon, valueUsd, valueMyst, valueText, sub, loading }) {
    return (
        <Card className="card-elev rounded-xl bg-card border border-border">
            <CardContent className="p-4">
                <div className="flex items-center justify-between">
                    <span className="text-xs font-medium tracking-wide text-muted-foreground">{label}</span>
                    <Icon className="w-3.5 h-3.5 text-muted-foreground" />
                </div>
                <div className="mt-3">
                    {loading ? (
                        <Skeleton className="h-7 w-24 bg-[hsl(var(--muted))]" />
                    ) : valueText !== undefined ? (
                        <div className="text-2xl font-semibold mono" data-testid={id}>{valueText}</div>
                    ) : (
                        <div className="text-2xl font-semibold mono" data-testid={id}>{fmtUSD(valueUsd)}</div>
                    )}
                </div>
                <div className="mt-1 text-[11px] text-muted-foreground mono">
                    {sub ? sub : `${fmtNum(valueMyst, 4)} MYST`}
                </div>
            </CardContent>
        </Card>
    );
}
