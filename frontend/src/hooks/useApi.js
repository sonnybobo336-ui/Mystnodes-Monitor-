import { useEffect, useRef, useState, useCallback } from "react";
import { api } from "@/lib/api";

export function useApi(path, opts = {}) {
    const { intervalMs = 0, method = "get", body = null, enabled = true } = opts;
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(enabled);
    const aliveRef = useRef(true);

    const fetcher = useCallback(async () => {
        if (!enabled) return;
        try {
            const res = method === "post" ? await api.post(path, body || {}) : await api.get(path);
            if (!aliveRef.current) return;
            setData(res.data);
            setError(null);
        } catch (e) {
            if (!aliveRef.current) return;
            setError(e?.response?.data || { message: e?.message || "Request failed" });
        } finally {
            if (aliveRef.current) setLoading(false);
        }
    }, [path, method, JSON.stringify(body), enabled]);

    useEffect(() => {
        aliveRef.current = true;
        if (!enabled) return () => { aliveRef.current = false; };
        fetcher();
        let t;
        if (intervalMs > 0) t = setInterval(fetcher, intervalMs);
        return () => { aliveRef.current = false; if (t) clearInterval(t); };
    }, [fetcher, intervalMs, enabled]);

    return { data, error, loading, refetch: fetcher };
}
