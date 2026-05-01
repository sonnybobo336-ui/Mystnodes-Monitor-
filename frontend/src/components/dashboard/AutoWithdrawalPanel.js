import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { useApi } from "@/hooks/useApi";
import { useCountdown } from "@/hooks/useCountdown";
import { api, fmtNum, fmtUSD, fmtRelTime } from "@/lib/api";
import { Clock, Play, ExternalLink, ScrollText } from "lucide-react";
import { toast } from "sonner";

export function AutoWithdrawalPanel({ refreshKey }) {
    const { data, loading, refetch } = useApi(`/withdrawal/state?_=${refreshKey}`, { intervalMs: 30_000 });
    const countdown = useCountdown(data?.next_run_at);
    const [running, setRunning] = useState(false);

    const runNow = async () => {
        setRunning(true);
        try {
            const res = await api.post("/withdrawal/run");
            await refetch();
            const note = res.data?.result;
            if (note?.triggered) toast.success(`Threshold met. Visit mystnodes.com to confirm.`);
            else toast.info(`Below threshold. ${fmtNum(note?.unsettled_myst, 4)} MYST unsettled.`);
        } catch {
            toast.error("Failed to run withdrawal check");
        } finally {
            setRunning(false);
        }
    };

    return (
        <Card
            className="card-elev rounded-xl bg-card border border-border h-full flex flex-col"
            data-testid="auto-withdrawal-panel"
        >
            <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium tracking-wide flex items-center gap-2">
                    <Clock className="w-4 h-4" /> Auto-Withdrawal
                </CardTitle>
                <div className="text-[11px] text-muted-foreground mt-1">
                    Runs every {data?.interval_days ?? 5} days. Mystnodes API is read-only — settlement is confirmed by you on mystnodes.com.
                </div>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col gap-4">
                <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg border border-border bg-[hsl(222_14%_11%)] p-3">
                        <div className="text-[10px] tracking-widest text-muted-foreground">NEXT RUN IN</div>
                        {loading ? (
                            <Skeleton className="h-6 w-24 bg-[hsl(var(--muted))] mt-1" />
                        ) : (
                            <div className="mono text-xl mt-1" data-testid="auto-withdrawal-countdown">{countdown}</div>
                        )}
                        <div className="text-[11px] text-muted-foreground mono mt-1">{data?.next_run_at?.replace("T", " ").slice(0, 16) || "—"}</div>
                    </div>
                    <div className="rounded-lg border border-border bg-[hsl(222_14%_11%)] p-3">
                        <div className="text-[10px] tracking-widest text-muted-foreground">THRESHOLD</div>
                        <div className="mono text-xl mt-1">{fmtNum(data?.threshold_myst ?? 5, 2)} MYST</div>
                        <div className="text-[11px] text-muted-foreground mono mt-1">Last run {fmtRelTime(data?.last_run_at)}</div>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <AlertDialog>
                        <AlertDialogTrigger asChild>
                            <Button size="sm" className="gap-2" disabled={running} data-testid="auto-withdrawal-run-now-button">
                                <Play className="w-4 h-4" /> {running ? "Running…" : "Run check now"}
                            </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent className="bg-card border-border">
                            <AlertDialogHeader>
                                <AlertDialogTitle>Run withdrawal check now?</AlertDialogTitle>
                                <AlertDialogDescription>
                                    This computes your unsettled MYST and creates a notification. The actual withdrawal must be confirmed on mystnodes.com.
                                </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction onClick={runNow}>Run now</AlertDialogAction>
                            </AlertDialogFooter>
                        </AlertDialogContent>
                    </AlertDialog>
                    <a
                        href="https://mystnodes.com"
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-md border border-border bg-[hsl(var(--secondary))] hover:bg-[hsl(222_14%_18%)]"
                    >
                        Open mystnodes.com <ExternalLink className="w-3 h-3" />
                    </a>
                    <LogDialog />
                </div>
                <RecentLog items={data?.recent || []} />
            </CardContent>
        </Card>
    );
}

function RecentLog({ items }) {
    if (!items.length) return (
        <div className="text-xs text-muted-foreground border-t border-border pt-3">
            No withdrawal events yet. The first scheduled run will appear here.
        </div>
    );
    return (
        <div className="border-t border-border pt-3">
            <div className="text-xs font-medium tracking-wide text-foreground mb-2">Recent</div>
            <ul className="space-y-2">
                {items.slice(0, 3).map((e) => (
                    <li key={e.id} className="flex items-center gap-2 text-xs">
                        <span className={`pill ${e.triggered ? "pill-healthy" : "pill-muted"}`}><span className="dot" /> {e.triggered ? "Triggered" : "Below"}</span>
                        <span className="mono">{fmtNum(e.unsettled_myst, 4)} MYST</span>
                        <span className="text-muted-foreground">· {fmtUSD(e.unsettled_usd)}</span>
                        <span className="text-muted-foreground ml-auto">{fmtRelTime(e.created_at)}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}

function LogDialog() {
    const [open, setOpen] = useState(false);
    const { data, loading } = useApi(`/withdrawal/log?limit=100`, { enabled: open });
    const items = data?.items || [];
    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button size="sm" variant="outline" className="gap-2" data-testid="auto-withdrawal-open-log-button">
                    <ScrollText className="w-4 h-4" /> Log
                </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-border max-w-2xl">
                <DialogHeader>
                    <DialogTitle>Withdrawal Log</DialogTitle>
                </DialogHeader>
                <div className="max-h-[60vh] overflow-auto">
                    {loading ? (
                        <div className="space-y-2">
                            {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-8 w-full bg-[hsl(var(--muted))]" />)}
                        </div>
                    ) : items.length === 0 ? (
                        <div className="text-sm text-muted-foreground py-6">No withdrawal events yet.</div>
                    ) : (
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="text-left text-[11px] text-muted-foreground border-b border-border">
                                    <th className="py-2">When</th>
                                    <th>Status</th>
                                    <th className="text-right">Unsettled MYST</th>
                                    <th className="text-right">USD</th>
                                    <th>Message</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items.map((e) => (
                                    <tr key={e.id} className="border-b border-border">
                                        <td className="py-2 text-muted-foreground mono">{e.created_at?.replace("T", " ").slice(0, 19)}</td>
                                        <td><span className={`pill ${e.triggered ? "pill-healthy" : "pill-muted"}`}><span className="dot" />{e.triggered ? "Triggered" : "Below"}</span></td>
                                        <td className="text-right mono">{fmtNum(e.unsettled_myst, 4)}</td>
                                        <td className="text-right mono">{fmtUSD(e.unsettled_usd)}</td>
                                        <td className="text-xs text-muted-foreground max-w-[260px]">{e.message}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
