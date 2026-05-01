import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { RefreshCw, Settings, Activity } from "lucide-react";
import { useApi } from "@/hooks/useApi";
import { fmtNum, fmtPct, fmtRelTime } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

export function Header({ onOpenSettings, onRefresh, refreshKey }) {
    const { data, loading } = useApi(`/prices?_=${refreshKey}`, { intervalMs: 60_000 });
    const [now, setNow] = useState(Date.now());
    useEffect(() => {
        const t = setInterval(() => setNow(Date.now()), 30_000);
        return () => clearInterval(t);
    }, []);
    const prices = data?.prices || [];

    return (
        <header className="sticky top-0 z-40 border-b border-border bg-background">
            <div className="header-overlay">
                <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center gap-4">
                    <div className="flex items-center gap-3 shrink-0">
                        <div className="w-8 h-8 rounded-lg bg-[hsl(168_62%_44%)] flex items-center justify-center shadow-[var(--shadow-elev-1)]">
                            <Activity className="w-4 h-4 text-[hsl(222_18%_7%)]" />
                        </div>
                        <div className="leading-tight">
                            <div className="font-semibold tracking-tight">NodeForge</div>
                            <div className="text-[11px] text-muted-foreground -mt-0.5">Node operations</div>
                        </div>
                    </div>
                    <div
                        className="flex-1 overflow-x-auto no-scrollbar"
                        data-testid="header-ticker-row"
                    >
                        <div className="flex items-center gap-2 min-w-max px-2">
                            {loading && prices.length === 0
                                ? Array.from({ length: 4 }).map((_, i) => (
                                      <Skeleton key={i} className="h-8 w-32 rounded-full bg-card" />
                                  ))
                                : prices.map((p) => (
                                      <TickerChip key={p.id} p={p} />
                                  ))}
                        </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                        <span className="text-xs text-muted-foreground hidden sm:inline">{`Updated ${fmtRelTime(new Date(now).toISOString())}`}</span>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={onRefresh}
                            data-testid="header-refresh-button"
                            aria-label="Refresh data"
                            className="hover:bg-[hsl(var(--muted))]"
                        >
                            <RefreshCw className="w-4 h-4" />
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onOpenSettings}
                            data-testid="header-open-settings-button"
                            className="gap-2"
                        >
                            <Settings className="w-4 h-4" />
                            <span className="hidden sm:inline">Settings</span>
                        </Button>
                    </div>
                </div>
            </div>
        </header>
    );
}

function TickerChip({ p }) {
    const change = p.change_24h_pct;
    const positive = (change ?? 0) >= 0;
    const color = change === undefined || change === null
        ? "text-muted-foreground"
        : positive ? "text-[hsl(142_62%_70%)]" : "text-[hsl(0_72%_72%)]";
    return (
        <div
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-border bg-card hover:border-[hsl(222_12%_28%)] transition-colors"
            data-testid={`ticker-${p.symbol?.toLowerCase?.()}`}
            title={`${p.symbol} • ${fmtNum(p.price_usd, 6)}`}
        >
            <span className="text-xs font-medium text-muted-foreground">{p.symbol}</span>
            <span className="text-sm mono">{p.price_usd ? `$${fmtNum(p.price_usd, p.price_usd > 100 ? 0 : 4)}` : "—"}</span>
            <span className={`text-xs mono ${color}`}>{fmtPct(change)}</span>
        </div>
    );
}
