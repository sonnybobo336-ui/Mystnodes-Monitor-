import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({
    baseURL: API,
    timeout: 30000,
});

export const fmtUSD = (v, opts = {}) => {
    if (v === null || v === undefined || isNaN(v)) return "—";
    const n = Number(v);
    return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: opts.max ?? 2, ...opts });
};

export const fmtNum = (v, max = 4) => {
    if (v === null || v === undefined || isNaN(v)) return "—";
    return Number(v).toLocaleString("en-US", { maximumFractionDigits: max });
};

export const fmtPct = (v, max = 2) => {
    if (v === null || v === undefined || isNaN(v)) return "—";
    const n = Number(v);
    const sign = n > 0 ? "+" : "";
    return `${sign}${n.toFixed(max)}%`;
};

export const fmtAddr = (a, head = 6, tail = 4) => {
    if (!a) return "—";
    return `${a.slice(0, head)}…${a.slice(-tail)}`;
};

export const fmtRelTime = (iso) => {
    if (!iso) return "—";
    const ts = new Date(iso).getTime();
    if (Number.isNaN(ts)) return "—";
    const diffSec = Math.round((Date.now() - ts) / 1000);
    if (diffSec < 60) return `${diffSec}s ago`;
    if (diffSec < 3600) return `${Math.round(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.round(diffSec / 3600)}h ago`;
    return `${Math.round(diffSec / 86400)}d ago`;
};

export const fmtCountdown = (iso) => {
    if (!iso) return "—";
    const ts = new Date(iso).getTime();
    if (Number.isNaN(ts)) return "—";
    let s = Math.max(0, Math.round((ts - Date.now()) / 1000));
    const d = Math.floor(s / 86400); s -= d * 86400;
    const h = Math.floor(s / 3600); s -= h * 3600;
    const m = Math.floor(s / 60);
    if (d > 0) return `${d}d ${h}h ${m}m`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
};
