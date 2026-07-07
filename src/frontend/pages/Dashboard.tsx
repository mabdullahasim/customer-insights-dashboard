import { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import styles from "./Dashboard.module.css";
import Header from "../components/Header";
import Nav from "../components/Nav";
import { useTheme } from "../components/useTheme";
import api from "../api/Client";
import { toNum, formatMoney, hexToRgba } from "../utils/Helpers";
import type { Summary, MonthlyPoint, CountryStat } from "../utils/Helpers";
import { Line } from "react-chartjs-2";
import {
Chart as ChartJS,
CategoryScale,
LinearScale,
PointElement,
LineElement,
Filler,
Tooltip,
} from "chart.js";
import type { ChartData, ChartOptions, Plugin } from "chart.js";
import {Users, DollarSign, Banknote, Clock, Star, Smile, AlertTriangle, ArrowUpRight, } from "lucide-react";

/* ── Register Chart.js modules ── */
ChartJS.register(CategoryScale,LinearScale,
PointElement,
LineElement,
Filler,
Tooltip
);

/* ── Component ── */
const Dashboard = () => {
 const { theme } = useTheme();

const [summary, setSummary] = useState<Summary | null>(null);
const [monthly, setMonthly] = useState<MonthlyPoint[]>([]);
const [countries, setCountries] = useState<CountryStat[]>([]);
const [loading, setLoading] = useState(true);

/* Fetch all three endpoints on mount */
useEffect(() => {
async function fetchDashboard() {
    try {
    const [sumRes, monthRes, countryRes] = await Promise.all([
        api.get("/analytics/summary"),
        api.get("/analytics/monthly-revenue"),
        api.get("/analytics/by-country"),
    ]);
    setSummary(sumRes.data);
    setMonthly(monthRes.data);
    setCountries(countryRes.data);
    } catch (err) {
    console.error("Dashboard fetch error:", err);
    } finally {
    setLoading(false);
    }
}
fetchDashboard();
}, []);

/* Read live CSS vars so chart colors match the active theme */
const cssVars = useMemo(() => {
const css = getComputedStyle(document.documentElement);
return {
    accent: css.getPropertyValue("--accent").trim(),
    heading: css.getPropertyValue("--heading").trim(),
    muted: css.getPropertyValue("--muted").trim(),
    border: css.getPropertyValue("--border").trim(),
    card: css.getPropertyValue("--card").trim(),
};
}, [theme]);

/* Plugin: paints a vertical gradient fill under the revenue line */
const gradientPlugin: Plugin<"line"> = useMemo(
() => ({
    id: "revenueGradient",
    beforeDatasetsDraw(chart) {
    const ds = chart.data.datasets[0];
    if (!ds || !chart.chartArea) return;
    const {
        ctx,
        chartArea: { top, bottom },
    } = chart;
    const gradient = ctx.createLinearGradient(0, top, 0, bottom);
    gradient.addColorStop(0, hexToRgba(cssVars.accent, 0.32));
    gradient.addColorStop(1, hexToRgba(cssVars.accent, 0));
    ds.backgroundColor = gradient;
    },
}),
[cssVars.accent]
);

/* Chart datasets */
const chartData: ChartData<"line"> = useMemo(
() => ({
    labels: monthly.map((m) => m.month),
    datasets: [
    {
        label: "Revenue",
        data: monthly.map((m) => toNum(m.revenue)),
        yAxisID: "y",
        borderColor: cssVars.accent,
        backgroundColor: "transparent",
        fill: true,
        tension: 0.38,
        borderWidth: 2.5,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: cssVars.accent,
    },
    {
        label: "Customers",
        data: monthly.map((m) => m.customer_count),
        yAxisID: "y1",
        borderColor: "#38bdf8",
        backgroundColor: "#38bdf8",
        tension: 0.38,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 5,
    },
    {
        label: "Avg review",
        data: monthly.map((m) => m.avg_review_score ?? 0),
        yAxisID: "y2",
        borderColor: "#f59e0b",
        backgroundColor: "#f59e0b",
        borderDash: [5, 4],
        tension: 0.38,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 5,
    },
    ],
}),
[monthly, cssVars.accent]
);

/* Chart options — axes, tooltip, grid all themed from CSS vars */
const chartOptions: ChartOptions<"line"> = useMemo(
() => ({
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index" as const, intersect: false },
    plugins: {
    legend: { display: false },
    tooltip: {
        backgroundColor: cssVars.card,
        titleColor: cssVars.heading,
        bodyColor: cssVars.muted,
        borderColor: cssVars.border,
        borderWidth: 1,
        padding: 12,
        cornerRadius: 10,
        boxPadding: 5,
        usePointStyle: true,
        callbacks: {
        label(ctx) {
            if (ctx.dataset.label === "Revenue")
            return "  Revenue: $" + (ctx.parsed?.y ?? 0).toLocaleString();
            if (ctx.dataset.label === "Customers")
            return "  Customers: " + (ctx.parsed?.y ?? 0);
            return "  Avg review: " + (ctx.parsed?.y ?? 0);
        },
        },
    },
    },
    scales: {
    x: {
        grid: { display: false },
        ticks: {
        color: cssVars.muted,
        font: { family: "Poppins", size: 11 },
        },
        border: { color: cssVars.border },
    },
    y: {
        grid: { color: cssVars.border, drawTicks: false },
        border: { display: false },
        ticks: {
        color: cssVars.muted,
        font: { family: "Poppins", size: 11 },
        callback(v) {
            return "$" + Number(v) / 1000 + "k";
        },
        },
    },
    y1: {
        position: "right" as const,
        grid: { display: false },
        border: { display: false },
        ticks: {
        color: cssVars.muted,
        font: { family: "Poppins", size: 11 },
        },
    },
    y2: { display: false, min: 0, max: 5 },
    },
}),
[cssVars]
);

/* ── Loading state ── */
if (loading) {
return (
    <div className={styles.container}>
    <Nav />
    <Header title="Dashboard" subtitle="Overview of your customer base and revenue health." />
    <div className={styles.loading}>Loading dashboard...</div>
    </div>
);
}

/* ── Derived values ── */
const top3 = countries.slice(0, 3);
const maxCountryRevenue =
top3.length > 0 ? toNum(top3[0].revenue) : 1;

/* ── Render ── */
return (
<div className={styles.container}>
    <Nav />
    <Header title="Dashboard" subtitle="Overview of your customer base and revenue health." />

    <main className={styles.main}>
    {/* ━━ Row 1: Summary cards ━━ */}
    {summary && (
        <div className={styles.cardsGrid}>
        {/* Total customers */}
        <div className={styles.card}>
            <div className={styles.cardTop}>
            <span className={styles.cardLabel}>Total customers</span>
            <div
                className={`${styles.cardIcon} ${styles.cardIconAccent}`}
            >
                <Users size={19} />
            </div>
            </div>
            <div className={styles.cardValue}>
            {summary.total_customers}
            </div>
            <div className={styles.captionPositive}>
            <ArrowUpRight size={13} strokeWidth={2.5} />
            {summary.recent_customers_30d} new in last 30 days
            </div>
        </div>

        {/* Total revenue */}
        <div className={styles.card}>
            <div className={styles.cardTop}>
            <span className={styles.cardLabel}>Total revenue</span>
            <div
                className={`${styles.cardIcon} ${styles.cardIconPositive}`}
            >
                <DollarSign size={19} />
            </div>
            </div>
            <div className={styles.cardValue}>
            {formatMoney(toNum(summary.total_revenue))}
            </div>
            <div className={styles.cardCaption}>
            Across all customers &amp; regions
            </div>
        </div>

        {/* Avg revenue / customer */}
        <div className={styles.card}>
            <div className={styles.cardTop}>
            <span className={styles.cardLabel}>
                Avg revenue / customer
            </span>
            <div
                className={`${styles.cardIcon} ${styles.cardIconAccent}`}
            >
                <Banknote size={19} />
            </div>
            </div>
            <div className={styles.cardValue}>
            {formatMoney(toNum(summary.avg_revenue_per_customer))}
            </div>
            <div className={styles.cardCaption}>
            Lifetime value per customer
            </div>
        </div>

        {/* Recent customers */}
        <div className={styles.card}>
            <div className={styles.cardTop}>
            <span className={styles.cardLabel}>Recent customers</span>
            <div
                className={`${styles.cardIcon} ${styles.cardIconAccent}`}
            >
                <Clock size={19} />
            </div>
            </div>
            <div className={styles.cardValue}>
            {summary.recent_customers_30d}
            </div>
            <div className={styles.cardCaption}>
            Active in the last 30 days
            </div>
        </div>
        </div>
    )}

    {/* ━━ Row 2: Chart + stat column ━━ */}
    <div className={styles.middleRow}>
        {/* Revenue trend chart */}
        <div className={styles.card} style={{ padding: 24 }}>
        <div className={styles.chartHeader}>
            <div>
            <div className={styles.chartTitle}>
                Monthly revenue trend
            </div>
            <div className={styles.chartSubtitle}>
                Revenue, customer count &amp; avg review score by month
            </div>
            </div>
            <div className={styles.legendRow}>
            <span className={styles.legendItem}>
                <span
                className={styles.legendDot}
                style={{ background: cssVars.accent }}
                />
                Revenue
            </span>
            <span className={styles.legendItem}>
                <span
                className={styles.legendDot}
                style={{ background: "#38bdf8" }}
                />
                Customers
            </span>
            <span className={styles.legendItem}>
                <span
                className={styles.legendDot}
                style={{ background: "#f59e0b" }}
                />
                Avg review
            </span>
            </div>
        </div>
        <div className={styles.chartContainer}>
            {monthly.length > 0 && (
            <Line
                key={`rev-${theme}`}
                data={chartData}
                options={chartOptions}
                plugins={[gradientPlugin]}
            />
            )}
        </div>
        </div>

        {/* Stat cards */}
        <div className={styles.statColumn}>
        {/* Avg review score */}
        {summary && (
            <div className={styles.statCard}>
            <div className={styles.statHeader}>
                <div
                className={`${styles.cardIcon} ${styles.cardIconWarning}`}
                >
                <Star size={19} />
                </div>
                <span className={styles.cardLabel}>
                Avg review score
                </span>
            </div>
            <div className={styles.statValueRow}>
                <span className={styles.statBigValue}>
                {summary.average_review_score != null
                    ? summary.average_review_score.toFixed(2)
                    : "—"}
                </span>
                <span className={styles.statUnit}>/ 5.0</span>
            </div>
            <div className={styles.progressTrack}>
                <div
                className={`${styles.progressFill} ${styles.progressFillWarning}`}
                style={{
                    width: `${((summary.average_review_score ?? 0) / 5) * 100}%`,
                }}
                />
            </div>
            </div>
        )}

        {/* Avg sentiment score */}
        {summary && (
            <div className={styles.statCard}>
            <div className={styles.statHeader}>
                <div
                className={`${styles.cardIcon} ${styles.cardIconPositive}`}
                >
                <Smile size={19} />
                </div>
                <span className={styles.cardLabel}>
                Avg sentiment score
                </span>
            </div>
            <div className={styles.statValueRow}>
                <span className={styles.statBigValue}>
                {summary.avg_sentiment_score != null
                    ? (summary.avg_sentiment_score >= 0 ? "+" : "") +
                    summary.avg_sentiment_score.toFixed(2)
                    : "—"}
                </span>
                <span className={styles.statUnit}>/ +1.0</span>
            </div>
            <div className={styles.progressTrack}>
                <div
                className={`${styles.progressFill} ${
                    (summary.avg_sentiment_score ?? 0) > 0.2
                    ? styles.progressFillPositive
                    : (summary.avg_sentiment_score ?? 0) < -0.2
                    ? styles.progressFillDanger
                    : styles.progressFillWarning
                }`}
                style={{
                    width: `${(((summary.avg_sentiment_score ?? 0) + 1) / 2) * 100}%`,
                }}
                />
            </div>
            </div>
        )}

        {/* High churn risk */}
        {summary && (
            <div className={styles.statCard}>
            <div className={styles.statHeader}>
                <div
                className={`${styles.cardIcon} ${styles.cardIconDanger}`}
                >
                <AlertTriangle size={19} />
                </div>
                <span className={styles.cardLabel}>High churn risk</span>
            </div>
            <div className={styles.statValueRow}>
                <span className={styles.statBigValue}>
                {summary.high_churn_risk_count}
                </span>
                <span className={styles.statUnit}>customers</span>
            </div>
            <Link to="/analytics" className={styles.churnLink}>
                Review at risk →
            </Link>
            </div>
        )}
        </div>
    </div>

    {/* ━━ Row 3: Top countries by revenue ━━ */}
    {top3.length > 0 && (
        <div className={styles.card} style={{ padding: 24 }}>
        <div className={styles.countriesTitle}>
            Top countries by revenue
        </div>
        <div className={styles.countriesGrid}>
            {top3.map((c, i) => (
            <div key={c.country} className={styles.countryTile}>
                <div className={styles.countryHeader}>
                <span className={styles.countryName}>
                    <span className={styles.countryRank}>{i + 1}</span>
                    {c.country}
                </span>
                <span className={styles.countryCount}>
                    {c.customer_count} cust.
                </span>
                </div>
                <div className={styles.countryRevenue}>
                {formatMoney(toNum(c.revenue))}
                </div>
                <div className={styles.countryBar}>
                <div
                    className={styles.countryBarFill}
                    style={{
                    width: `${(toNum(c.revenue) / maxCountryRevenue) * 100}%`,
                    }}
                />
                </div>
            </div>
            ))}
        </div>
        </div>
    )}
    </main>
</div>
);
};

export default Dashboard;