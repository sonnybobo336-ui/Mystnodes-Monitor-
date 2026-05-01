import { useEffect, useState } from "react";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api } from "@/lib/api";
import { useApi } from "@/hooks/useApi";
import { CheckCircle2, XCircle, Save, Beaker } from "lucide-react";
import { toast } from "sonner";

export function SettingsSheet({ open, onOpenChange, onSaved }) {
    const { data, refetch } = useApi(`/settings?_=${open ? Date.now() : 0}`, { enabled: open });
    const [form, setForm] = useState({
        mystnodes_email: "",
        mystnodes_password: "",
        tailscale_api_key: "",
        tailscale_tailnet: "-",
        auto_withdrawal_days: 5,
        auto_withdrawal_threshold_myst: 5,
    });
    const [saving, setSaving] = useState(false);
    const [tests, setTests] = useState({ myst: null, ts: null });
    const [busy, setBusy] = useState({ myst: false, ts: false });

    useEffect(() => {
        if (data) {
            setForm((f) => ({
                ...f,
                mystnodes_email: data.mystnodes_email || "",
                tailscale_tailnet: data.tailscale_tailnet || "-",
                auto_withdrawal_days: data.auto_withdrawal_days ?? 5,
                auto_withdrawal_threshold_myst: data.auto_withdrawal_threshold_myst ?? 5,
            }));
        }
    }, [data]);

    const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

    const testMyst = async () => {
        setBusy({ ...busy, myst: true });
        try {
            const res = await api.post("/settings/test/mystnodes", {
                email: form.mystnodes_email,
                password: form.mystnodes_password,
            });
            setTests((t) => ({ ...t, myst: res.data }));
            if (res.data.ok) toast.success("Mystnodes credentials valid");
            else toast.error(`Mystnodes test failed`);
        } catch (e) {
            toast.error("Mystnodes test failed");
            setTests((t) => ({ ...t, myst: { ok: false, error: e?.message || "failed" } }));
        } finally {
            setBusy({ ...busy, myst: false });
        }
    };
    const testTs = async () => {
        setBusy({ ...busy, ts: true });
        try {
            const res = await api.post("/settings/test/tailscale", {
                api_key: form.tailscale_api_key,
                tailnet: form.tailscale_tailnet || "-",
            });
            setTests((t) => ({ ...t, ts: res.data }));
            if (res.data.ok) toast.success(`Tailscale OK · ${res.data.count} device(s)`);
            else toast.error(`Tailscale test failed`);
        } catch (e) {
            toast.error("Tailscale test failed");
            setTests((t) => ({ ...t, ts: { ok: false, error: e?.message || "failed" } }));
        } finally {
            setBusy({ ...busy, ts: false });
        }
    };

    const save = async () => {
        setSaving(true);
        try {
            const payload = {
                mystnodes_email: form.mystnodes_email || null,
                mystnodes_password: form.mystnodes_password || null,
                tailscale_api_key: form.tailscale_api_key || null,
                tailscale_tailnet: form.tailscale_tailnet || "-",
                auto_withdrawal_days: Number(form.auto_withdrawal_days) || 5,
                auto_withdrawal_threshold_myst: Number(form.auto_withdrawal_threshold_myst) || 5,
            };
            await api.post("/settings/save", payload);
            await refetch();
            toast.success("Settings saved");
            onSaved?.();
        } catch {
            toast.error("Failed to save settings");
        } finally {
            setSaving(false);
        }
    };

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent
                side="right"
                className="bg-card border-border w-full sm:max-w-md overflow-auto"
                data-testid="settings-drawer"
            >
                <SheetHeader>
                    <SheetTitle>Settings</SheetTitle>
                    <SheetDescription>Configure account connections and automation.</SheetDescription>
                </SheetHeader>
                <Tabs defaultValue="accounts" className="mt-4">
                    <TabsList className="grid grid-cols-2 bg-[hsl(var(--secondary))]">
                        <TabsTrigger value="accounts">Accounts</TabsTrigger>
                        <TabsTrigger value="automation">Automation</TabsTrigger>
                    </TabsList>

                    <TabsContent value="accounts" className="space-y-6 mt-4">
                        <section className="space-y-3">
                            <h3 className="text-sm font-medium tracking-wide">Mystnodes account</h3>
                            <div className="text-xs text-muted-foreground -mt-1">Required for node metrics & earnings.</div>
                            <div className="space-y-2">
                                <Label htmlFor="myst-email">Email</Label>
                                <Input id="myst-email" data-testid="settings-mystnodes-email" type="email" value={form.mystnodes_email} onChange={update("mystnodes_email")} placeholder="you@example.com" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="myst-pw">Password</Label>
                                <Input id="myst-pw" data-testid="settings-mystnodes-password" type="password" value={form.mystnodes_password} onChange={update("mystnodes_password")} placeholder="••••••••" />
                            </div>
                            <div className="flex items-center gap-2">
                                <Button size="sm" variant="outline" className="gap-2" onClick={testMyst} disabled={busy.myst} data-testid="settings-test-mystnodes-button">
                                    <Beaker className="w-4 h-4" /> {busy.myst ? "Testing…" : "Test connection"}
                                </Button>
                                {tests.myst && (
                                    <span className={`text-xs inline-flex items-center gap-1 ${tests.myst.ok ? "text-[hsl(142_62%_70%)]" : "text-[hsl(0_72%_72%)]"}`}>
                                        {tests.myst.ok ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                                        {tests.myst.ok ? "Valid" : (tests.myst.error || "Failed").slice(0, 60)}
                                    </span>
                                )}
                            </div>
                        </section>
                        <section className="space-y-3">
                            <h3 className="text-sm font-medium tracking-wide">Tailscale</h3>
                            <div className="text-xs text-muted-foreground -mt-1">Optional. Maps Mysterium nodes to host devices.</div>
                            <div className="space-y-2">
                                <Label htmlFor="ts-key">API key</Label>
                                <Input id="ts-key" data-testid="settings-tailscale-key" type="password" value={form.tailscale_api_key} onChange={update("tailscale_api_key")} placeholder="tskey-api-…" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="ts-net">Tailnet</Label>
                                <Input id="ts-net" data-testid="settings-tailscale-tailnet" value={form.tailscale_tailnet} onChange={update("tailscale_tailnet")} placeholder="-" />
                            </div>
                            <div className="flex items-center gap-2">
                                <Button size="sm" variant="outline" className="gap-2" onClick={testTs} disabled={busy.ts} data-testid="settings-test-tailscale-button">
                                    <Beaker className="w-4 h-4" /> {busy.ts ? "Testing…" : "Test connection"}
                                </Button>
                                {tests.ts && (
                                    <span className={`text-xs inline-flex items-center gap-1 ${tests.ts.ok ? "text-[hsl(142_62%_70%)]" : "text-[hsl(0_72%_72%)]"}`}>
                                        {tests.ts.ok ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                                        {tests.ts.ok ? `${tests.ts.count} device(s)` : (tests.ts.error || "Failed").slice(0, 60)}
                                    </span>
                                )}
                            </div>
                        </section>
                    </TabsContent>

                    <TabsContent value="automation" className="space-y-6 mt-4">
                        <Alert className="bg-[hsl(200_50%_14%)] border-[hsl(200_50%_22%)] text-[hsl(200_78%_72%)]">
                            <AlertTitle className="text-sm">Read-only API limitation</AlertTitle>
                            <AlertDescription className="text-xs">
                                The Mystnodes public API does not expose programmatic withdrawals.
                                The scheduler will run a check on the configured cycle and notify you when your unsettled balance is ready.
                                Final confirmation is done on mystnodes.com.
                            </AlertDescription>
                        </Alert>
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-2">
                                <Label htmlFor="days">Cycle days</Label>
                                <Input id="days" type="number" min={1} max={60} value={form.auto_withdrawal_days} onChange={update("auto_withdrawal_days")} data-testid="settings-cycle-days" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="thr">Threshold (MYST)</Label>
                                <Input id="thr" type="number" step="0.1" min={0} value={form.auto_withdrawal_threshold_myst} onChange={update("auto_withdrawal_threshold_myst")} data-testid="settings-threshold" />
                            </div>
                        </div>
                    </TabsContent>
                </Tabs>

                <div className="sticky bottom-0 left-0 right-0 mt-6 pt-4 border-t border-border bg-card">
                    <Button onClick={save} disabled={saving} className="w-full gap-2" data-testid="settings-save-button">
                        <Save className="w-4 h-4" /> {saving ? "Saving…" : "Save changes"}
                    </Button>
                </div>
            </SheetContent>
        </Sheet>
    );
}
