import { useState } from "react";
import { Header } from "@/components/dashboard/Header";
import { KpiRow } from "@/components/dashboard/KpiRow";
import { EarningsChart } from "@/components/dashboard/EarningsChart";
import { AiInsightsPanel } from "@/components/dashboard/AiInsightsPanel";
import { NodesTable } from "@/components/dashboard/NodesTable";
import { WalletsCard } from "@/components/dashboard/WalletsCard";
import { AutoWithdrawalPanel } from "@/components/dashboard/AutoWithdrawalPanel";
import { SettingsSheet } from "@/components/dashboard/SettingsSheet";

export default function DashboardPage() {
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);
    const bumpRefresh = () => setRefreshKey((k) => k + 1);

    return (
        <div className="min-h-screen bg-background text-foreground">
            <Header
                onOpenSettings={() => setSettingsOpen(true)}
                onRefresh={bumpRefresh}
                refreshKey={refreshKey}
            />
            <main className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-16">
                <div className="grid grid-cols-12 gap-4 lg:gap-6">
                    <div className="col-span-12">
                        <KpiRow refreshKey={refreshKey} />
                    </div>
                    <div className="col-span-12 lg:col-span-8">
                        <EarningsChart refreshKey={refreshKey} />
                    </div>
                    <div className="col-span-12 lg:col-span-4">
                        <AiInsightsPanel refreshKey={refreshKey} />
                    </div>
                    <div className="col-span-12">
                        <NodesTable refreshKey={refreshKey} onOpenSettings={() => setSettingsOpen(true)} />
                    </div>
                    <div className="col-span-12 lg:col-span-7">
                        <WalletsCard refreshKey={refreshKey} />
                    </div>
                    <div className="col-span-12 lg:col-span-5">
                        <AutoWithdrawalPanel refreshKey={refreshKey} />
                    </div>
                </div>
            </main>
            <SettingsSheet
                open={settingsOpen}
                onOpenChange={setSettingsOpen}
                onSaved={bumpRefresh}
            />
        </div>
    );
}
