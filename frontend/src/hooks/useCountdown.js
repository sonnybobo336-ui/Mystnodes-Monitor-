import { useEffect, useState } from "react";
import { fmtCountdown } from "@/lib/api";

export function useCountdown(targetIso) {
    const [text, setText] = useState(fmtCountdown(targetIso));
    useEffect(() => {
        setText(fmtCountdown(targetIso));
        const t = setInterval(() => setText(fmtCountdown(targetIso)), 1000 * 30);
        return () => clearInterval(t);
    }, [targetIso]);
    return text;
}
