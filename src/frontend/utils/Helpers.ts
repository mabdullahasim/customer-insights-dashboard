/* ── Backend response types ── */

export interface Summary {
    total_customers: number;
    total_revenue: string | number;
    avg_revenue_per_customer: string | number;
    average_review_score: number | null;
    avg_sentiment_score: number | null;
    high_churn_risk_count: number;
    top_countries_by_revenue: string[];
    recent_customers_30d: number;
  }
  
  export interface MonthlyPoint {
    month: string;
    revenue: string | number;
    customer_count: number;
    avg_review_score: number | null;
  }
  
  export interface CountryStat {
    country: string;
    revenue: string | number;
    customer_count: number;
    avg_review_score: number | null;
    avg_revenue_per_customer: string | number;
  }
  
  export interface CustomerFeature {
    id: number;
    full_name: string;
    total_spent: string | number;
    recency_days: number | null;
    review_score: number | null;
    sentiment_score: number | null;
    segment: string | null;
    churn_risk: number | null;
    country: string | null;
  }
  
  export interface ReviewDist {
    review_score: number;
    count: number;
    percentage: number;
  }
  
  /* ── Helpers ── */
  
  export function toNum(val: string | number | null | undefined): number {
    if (val == null) return 0;
    return typeof val === "string" ? parseFloat(val) || 0 : val;
  }
  
  export function formatMoney(n: number): string {
    if (n >= 1_000_000) return "$" + (n / 1_000_000).toFixed(2) + "M";
    if (n >= 1_000) return "$" + (n / 1_000).toFixed(1) + "K";
    return "$" + Math.round(n).toLocaleString();
  }
  
  export function formatMoneyFull(n: number): string {
    return "$" + Math.round(n).toLocaleString();
  }
  
  export function hexToRgba(hex: string, alpha: number): string {
    hex = hex.replace("#", "");
    if (hex.length === 3) hex = hex.split("").map((c) => c + c).join("");
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r},${g},${b},${alpha})`;
  }
  
  export function initials(name: string): string {
    return name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
  }
  
  export function churnBand(risk: number | null): "low" | "medium" | "high" {
    if (risk == null) return "low";
    if (risk > 0.66) return "high";
    if (risk > 0.33) return "medium";
    return "low";
  }
  
  export function churnPrediction(risk: number | null): string {
    return (risk ?? 0) > 0.5 ? "Will churn" : "Will stay";
  }
  
  export function confidenceLabel(risk: number | null): "High" | "Medium" | "Low" {
    const r = risk ?? 0;
    if (r > 0.75 || r < 0.25) return "High";
    if (r > 0.6 || r < 0.4) return "Medium";
    return "Low";
  }
  
  export function csvDownload(filename: string, header: string[], rows: (string | number | null)[][]) {
    const esc = (v: string | number | null) => {
      const s = String(v ?? "");
      return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
    };
    const csv = [header.join(","), ...rows.map((r) => r.map(esc).join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }