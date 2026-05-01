import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useApi } from "@/hooks/useApi";
import { fmtNum, fmtUSD } from "@/lib/api";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function EarningsChart({ refreshKey }) {
    const [days, setDays] = useState("30");
    const [currency, setCurrency] = useState("USD");
    const { data, loading, error } = useApi(`/earnings/timeseries?days=${days}&_=${refreshKey}`);
    const points = useMemo(
        () => (data?.points || []).map((p) => ({
            ...p,
            value: currency === "USD" ? p.earnings_usd : p.earnings_myst,
        })),
        [data, currency]
    );

    const total = useMemo(() => points.reduce((s, p) => s + (Number(p.value) || 0), 0), [points]);

    return (
        <Card
            className="card-elev rounded-xl bg-card border border-border h-full"
            data-testid="earnings-chart-panel"
        >
            <CardHeader className="pb-2 flex flex-row items-start justify-between gap-3">
                <div>
                    <CardTitle className="text-sm font-medium tracking-wide">Earnings Trend</CardTitle>
                    <div className="text-xs text-muted-foreground mono mt-1">
                        Total {days}d: {currency === "USD" ? fmtUSD(total) : `${fmtNum(total, 4)} MYST`}
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Tabs value={days} onValueChange={setDays} data-testid="earnings-chart-timeframe-tabs">
                        <TabsList className="bg-[hsl(var(--secondary))]">
                            <TabsTrigger value="7" className="text-xs">7d</TabsTrigger>
                            <TabsTrigger value="30" className="text-xs">30d</TabsTrigger>
                            <TabsTrigger value="90" className="text-xs">90d</TabsTrigger>
                        </TabsList>
                    </Tabs>
                    <Tabs value={currency} onValueChange={setCurrency} data-testid="earnings-chart-currency-toggle">
                        <TabsList className="bg-[hsl(var(--secondary))]">
                            <TabsTrigger value="USD" className="text-xs">USD</TabsTrigger>
                            <TabsTrigger value="MYST" className="text-xs">MYST</TabsTrigger>
                        </TabsList>
                    </Tabs>
                </div>
            </CardHeader>
            <CardContent className="pt-0">
                {loading ? (
                    <Skeleton className="h-[260px] w-full bg-[hsl(var(--muted))]" />
                ) : error ? (
                    <div className="h-[260px] flex items-center justify-center text-sm text-muted-foreground">Failed to load chart.</div>
                ) : (
                    <div className="h-[260px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={points} margin={{ top: 10, right: 12, left: -10, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="earningsFill" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="hsl(168 62% 44%)" stopOpacity={0.45} />
                                        <stop offset="100%" stopColor="hsl(168 62% 44%)" stopOpacity={0.04} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid stroke="hsl(222 12% 18%)" strokeDasharray="3 3" />
                                <XAxis dataKey="date" stroke="hsl(215 14% 60%)" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis stroke="hsl(215 14% 60%)" fontSize={10} tickLine={false} axisLine={false} width={48} />
                                <Tooltip
                                    contentStyle={{
                                        background: "hsl(222 18% 9%)",
                                        border: "1px solid hsl(222 12% 22%)",
                                        borderRadius: 12,
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 12,
                                    }}
                                    labelStyle={{ color: "hsl(215 14% 70%)" }}
                                    formatter={(v) => [currency === "USD" ? fmtUSD(v) : `${fmtNum(v, 4)} MYST`, currency]}
                                />
                                <Area type="monotone" dataKey="value" stroke="hsl(168 62% 44%)" fill="url(#earningsFill)" strokeWidth={2} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
