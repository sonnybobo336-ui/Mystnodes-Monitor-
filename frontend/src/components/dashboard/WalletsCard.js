import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/useApi";
import { fmtAddr, fmtNum } from "@/lib/api";
import { Wallet, Copy, ExternalLink } from "lucide-react";
import { toast } from "sonner";

export function WalletsCard({ refreshKey }) {
    const { data, loading } = useApi(`/wallets?_=${refreshKey}`, { intervalMs: 120_000 });
    const balances = data?.balances || [];

    const copyAddr = (a) => {
        try {
            navigator.clipboard.writeText(a);
            toast.success("Address copied");
        } catch {
            toast.error("Copy failed");
        }
    };

    return (
        <Card
            className="card-elev rounded-xl bg-card border border-border h-full"
            data-testid="wallets-panel"
        >
            <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium tracking-wide flex items-center gap-2">
                    <Wallet className="w-4 h-4" /> Wallets
                </CardTitle>
                <div className="text-[11px] text-muted-foreground mt-1">
                    Read-only balances on Ethereum mainnet · Polygon (POL native + MYST ERC-20)
                </div>
            </CardHeader>
            <CardContent className="space-y-3">
                {loading ? (
                    Array.from({ length: 2 }).map((_, i) => (
                        <Skeleton key={i} className="h-24 w-full bg-[hsl(var(--muted))]" />
                    ))
                ) : balances.length === 0 ? (
                    <div className="text-sm text-muted-foreground py-4">No wallet addresses configured.</div>
                ) : (
                    balances.map((b) => (
                        <div
                            key={b.address}
                            className="rounded-lg border border-border bg-[hsl(222_18%_8%)] p-3"
                        >
                            <div className="flex items-center gap-2 justify-between">
                                <div className="flex items-center gap-2 min-w-0">
                                    <span className="text-xs font-mono mono truncate" title={b.address} data-testid="wallet-address">
                                        {fmtAddr(b.address, 10, 8)}
                                    </span>
                                    <Button
                                        size="icon"
                                        variant="ghost"
                                        className="h-6 w-6"
                                        onClick={() => copyAddr(b.address)}
                                        data-testid="wallet-copy-button"
                                        aria-label="Copy address"
                                    >
                                        <Copy className="w-3 h-3" />
                                    </Button>
                                </div>
                                <a
                                    href={`https://polygonscan.com/address/${b.address}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="text-xs text-muted-foreground hover:text-foreground inline-flex items-center gap-1"
                                    data-testid="wallet-explorer-link"
                                >
                                    Polygonscan <ExternalLink className="w-3 h-3" />
                                </a>
                            </div>
                            <div className="grid grid-cols-3 gap-3 mt-3">
                                <BalanceCell label="ETH" value={b.eth} suffix="ETH" />
                                <BalanceCell label="POL" value={b.pol} suffix="POL" />
                                <BalanceCell label="MYST" value={b.myst} suffix="MYST" highlight />
                            </div>
                        </div>
                    ))
                )}
            </CardContent>
        </Card>
    );
}

function BalanceCell({ label, value, suffix, highlight }) {
    return (
        <div className={`rounded-md border border-border px-3 py-2 ${highlight ? "bg-[hsl(168_40%_10%)]" : "bg-[hsl(222_14%_11%)]"}`}>
            <div className="text-[10px] tracking-widest text-muted-foreground">{label}</div>
            <div className="mono text-sm mt-1">
                {value === null || value === undefined ? "—" : fmtNum(value, 6)}
                <span className="text-[10px] text-muted-foreground ml-1">{suffix}</span>
            </div>
        </div>
    );
}
