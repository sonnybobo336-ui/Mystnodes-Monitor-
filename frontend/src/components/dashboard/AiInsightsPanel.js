import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Sparkles, RefreshCw, AlertTriangle, ArrowDownRight } from "lucide-react";
import { api, fmtUSD } from "@/lib/api";
import { useApi } from "@/hooks/useApi";
import { toast } from "sonner";

export function AiInsightsPanel({ refreshKey }) {
    const { data: latest, loading, refetch } = useApi(`/ai/insights/latest?_=${refreshKey}`);
    const [generating, setGenerating] = useState(false);
    const insights = latest?.insights || null;

    const generate = async () => {
        setGenerating(true);
        try {
            const res = await api.post("/ai/insights");
            await refetch();
            toast.success("Insights refreshed");
            return res.data;
        } catch (e) {
            toast.error("Failed to generate insights");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <Card
            className="card-elev rounded-xl bg-card border border-border h-full flex flex-col"
            data-testid="ai-insights-panel"
        >
            <CardHeader className="pb-2 flex flex-row items-start justify-between gap-3">
                <div>
                    <CardTitle className="text-sm font-medium tracking-wide flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-[hsl(168_62%_60%)]" />
                        AI Insights
                    </CardTitle>
                    <div className="text-[11px] text-muted-foreground mt-1">Powered by Claude Sonnet 4.5</div>
                </div>
                <Button
                    size="sm"
                    variant="outline"
                    onClick={generate}
                    disabled={generating}
                    data-testid="ai-insights-refresh-button"
                    className="gap-2"
                >
                    <RefreshCw className={`w-3.5 h-3.5 ${generating ? "animate-spin" : ""}`} />
                    {generating ? "Generating…" : "Refresh"}
                </Button>
            </CardHeader>
            <CardContent className="flex-1">
                {loading && !insights ? (
                    <div className="space-y-3">
                        {Array.from({ length: 4 }).map((_, i) => (
                            <Skeleton key={i} className="h-4 w-full bg-[hsl(var(--muted))]" />
                        ))}
                    </div>
                ) : !insights ? (
                    <EmptyInsights onClick={generate} disabled={generating} />
                ) : (
                    <div className="space-y-4 text-sm">
                        {insights.summary && (
                            <p className="text-muted-foreground leading-relaxed">{insights.summary}</p>
                        )}
                        {typeof insights.revenue_loss_estimate_usd === "number" && (
                            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[hsl(38_60%_22%)] bg-[hsl(38_60%_14%)] text-[hsl(38_92%_70%)]">
                                <ArrowDownRight className="w-3.5 h-3.5" />
                                <span className="text-xs">Estimated revenue loss</span>
                                <span className="text-xs mono">{fmtUSD(insights.revenue_loss_estimate_usd)}</span>
                            </div>
                        )}
                        {Array.isArray(insights.underperformers) && insights.underperformers.length > 0 && (
                            <div>
                                <div className="text-xs font-medium tracking-wide text-foreground mb-2">Underperformers</div>
                                <ul className="space-y-2">
                                    {insights.underperformers.slice(0, 4).map((u, i) => (
                                        <li key={i} className="flex items-start gap-2">
                                            <AlertTriangle className="w-3.5 h-3.5 text-[hsl(38_92%_70%)] mt-0.5 shrink-0" />
                                            <div>
                                                <div className="text-xs mono text-muted-foreground truncate max-w-[260px]" title={u.id}>{u.id}</div>
                                                <div className="text-sm text-foreground">{u.reason}</div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        {Array.isArray(insights.recommendations) && insights.recommendations.length > 0 && (
                            <div>
                                <div className="text-xs font-medium tracking-wide text-foreground mb-2">Recommendations</div>
                                <ul className="space-y-2 list-disc list-inside marker:text-[hsl(168_62%_60%)]">
                                    {insights.recommendations.slice(0, 6).map((r, i) => (
                                        <li key={i} className="text-sm leading-relaxed">{r}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

function EmptyInsights({ onClick, disabled }) {
    return (
        <div
            className="h-full flex flex-col items-center justify-center text-center py-10 px-4"
            data-testid="panel-empty-state"
        >
            <Sparkles className="w-8 h-8 text-[hsl(168_62%_50%)] mb-3" />
            <div className="text-sm font-medium">Generate insights</div>
            <p className="text-xs text-muted-foreground mt-1 max-w-[280px]">
                Spot underperforming nodes, estimate revenue loss, and get rebalancing recommendations.
            </p>
            <Button onClick={onClick} disabled={disabled} className="mt-4 gap-2" size="sm">
                <Sparkles className="w-4 h-4" />
                Run analysis
            </Button>
        </div>
    );
}
