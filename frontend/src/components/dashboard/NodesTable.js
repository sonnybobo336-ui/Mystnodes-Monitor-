import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/useApi";
import { fmtNum, fmtRelTime } from "@/lib/api";
import { Server, Settings, ExternalLink } from "lucide-react";

export function NodesTable({ refreshKey, onOpenSettings }) {
    const { data, loading, error } = useApi(`/nodes?_=${refreshKey}`, { intervalMs: 60_000 });
    const connected = data?.connected;
    const nodes = data?.nodes || [];

    return (
        <Card
            className="card-elev rounded-xl bg-card border border-border"
            data-testid="nodes-table-panel"
        >
            <CardHeader className="pb-2 flex flex-row items-start justify-between gap-3">
                <div>
                    <CardTitle className="text-sm font-medium tracking-wide flex items-center gap-2">
                        <Server className="w-4 h-4" /> Nodes
                    </CardTitle>
                    <div className="text-[11px] text-muted-foreground mt-1">
                        {connected === false ? "Mystnodes not connected" : `${nodes.length} node(s)`}
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                {loading ? (
                    <div className="space-y-2">
                        {Array.from({ length: 3 }).map((_, i) => (
                            <Skeleton key={i} className="h-12 w-full bg-[hsl(var(--muted))]" />
                        ))}
                    </div>
                ) : connected === false ? (
                    <EmptyConnect onOpenSettings={onOpenSettings} hint={data?.hint} />
                ) : error || data?.error ? (
                    <div className="text-sm text-[hsl(0_72%_72%)] py-4">Failed to load nodes. {data?.error || ""}</div>
                ) : nodes.length === 0 ? (
                    <div className="text-sm text-muted-foreground py-6">No nodes found on your account.</div>
                ) : (
                    <NodesTableInner nodes={nodes} />
                )}
            </CardContent>
        </Card>
    );
}

function EmptyConnect({ onOpenSettings, hint }) {
    return (
        <div
            className="flex flex-col items-center text-center py-10 px-4"
            data-testid="panel-empty-state"
        >
            <Server className="w-8 h-8 text-muted-foreground mb-3" />
            <div className="text-sm font-medium">Connect Mystnodes</div>
            <p className="text-xs text-muted-foreground mt-1 max-w-[420px]">
                {hint || "Sign in with your mystnodes.com email and password to monitor your nodes here."}
            </p>
            <Button
                onClick={onOpenSettings}
                className="mt-4 gap-2"
                size="sm"
                data-testid="nodes-empty-open-settings"
            >
                <Settings className="w-4 h-4" /> Open settings
            </Button>
        </div>
    );
}

function NodesTableInner({ nodes }) {
    return (
        <div className="overflow-x-auto -mx-4 sm:mx-0">
            <table className="w-full min-w-[920px] text-sm" data-testid="nodes-table">
                <thead>
                    <tr className="text-left text-[11px] font-medium tracking-wide text-muted-foreground border-b border-border">
                        <th className="px-4 py-2">Node</th>
                        <th className="px-3 py-2">Status</th>
                        <th className="px-3 py-2">Services</th>
                        <th className="px-3 py-2 text-right">24h Earnings</th>
                        <th className="px-3 py-2 text-right">Lifetime</th>
                        <th className="px-3 py-2 text-right">Quality</th>
                        <th className="px-3 py-2 text-right">Uptime 24h</th>
                        <th className="px-3 py-2">Last Seen</th>
                        <th className="px-3 py-2">Tailscale</th>
                    </tr>
                </thead>
                <tbody>
                    {nodes.map((n) => (
                        <NodeRow key={n.id} n={n} />
                    ))}
                </tbody>
            </table>
        </div>
    );
}

function NodeRow({ n }) {
    const lifetime = Number(n.lifetime_earnings?.totalEther || 0);
    const quality = n.quality === undefined || n.quality === null ? null : Number(n.quality);
    const uptimeMin = Number(n.uptime_min_24h || 0);
    const uptimePct = Math.min(100, (uptimeMin / 1440) * 100).toFixed(1);
    const ts = n.tailscale_device;
    return (
        <tr
            className="border-b border-border hover:bg-[hsl(var(--muted))] transition-colors"
            data-testid="nodes-table-row"
        >
            <td className="px-4 py-3 align-top">
                <div className="font-medium">{n.name || "(unnamed)"}</div>
                <div className="text-[11px] text-muted-foreground mono truncate max-w-[220px]" title={n.identity}>{n.identity}</div>
            </td>
            <td className="px-3 py-3 align-top">
                <span
                    className={`pill ${n.online ? "pill-healthy" : "pill-offline"}`}
                    data-testid="nodes-table-status-pill"
                >
                    <span className="dot" /> {n.online ? "Online" : "Offline"}
                </span>
            </td>
            <td className="px-3 py-3 align-top">
                <div className="flex flex-wrap gap-1">
                    {(n.service_types || []).map((s) => (
                        <span key={s} className="pill pill-muted text-[10px]">{s}</span>
                    ))}
                </div>
            </td>
            <td className="px-3 py-3 align-top text-right mono">{fmtNum(n.earnings_24h_myst, 4)}</td>
            <td className="px-3 py-3 align-top text-right mono">{fmtNum(lifetime, 4)}</td>
            <td className="px-3 py-3 align-top text-right mono">{quality === null ? "—" : quality.toFixed(2)}</td>
            <td className="px-3 py-3 align-top text-right mono">{uptimePct}%</td>
            <td className="px-3 py-3 align-top text-muted-foreground">{fmtRelTime(n.online_last_at)}</td>
            <td className="px-3 py-3 align-top">
                {ts ? (
                    <div className="flex items-center gap-1.5">
                        <span className="pill pill-info text-[10px]">{ts.name}</span>
                        <ExternalLink className="w-3 h-3 text-muted-foreground" />
                    </div>
                ) : (
                    <span className="text-[11px] text-muted-foreground">—</span>
                )}
            </td>
        </tr>
    );
}
