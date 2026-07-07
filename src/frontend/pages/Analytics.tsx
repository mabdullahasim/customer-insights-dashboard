import { useState, useEffect, useMemo, useCallback } from "react";
import styles from "./Analytics.module.css";
import Header from "../components/Header";
import Nav from "../components/Nav";
import { useTheme } from "../components/useTheme";
import api from "../api/Client";
import { Bar } from "react-chartjs-2";
import {Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip,} from "chart.js";
import type { ChartOptions, Plugin } from "chart.js";
import { Filter, Smile, RefreshCw, Check } from "lucide-react";
import {
  type CustomerFeature, type CountryStat, type ReviewDist,
  toNum, formatMoney, formatMoneyFull, hexToRgba,
  initials, churnBand, churnPrediction, confidenceLabel,
} from "../utils/Helpers";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

const PER_PAGE = 8;

const Analytics = () => {
  const { theme } = useTheme();

  const [byCountry, setByCountry] = useState<CountryStat[]>([]);
  const [reviewDist, setReviewDist] = useState<ReviewDist[]>([]);
  const [customers, setCustomers] = useState<CustomerFeature[]>([]);
  const [loading, setLoading] = useState(true);

  /* Filters */
  const [fCountry, setFCountry] = useState("all");
  const [fBand, setFBand] = useState("all");
  const [fReview, setFReview] = useState(1);

  /* Table sort + pagination */
  const [sortKey, setSortKey] = useState("total_spent");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(0);

  /* Toast */
  const [toast, setToast] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [cRes, rRes, fRes] = await Promise.all([
          api.get("/analytics/by-country"),
          api.get("/analytics/review_score_distribution"),
          api.get("/analytics/customer-features"),
        ]);
        setByCountry(cRes.data);
        setReviewDist(rRes.data);
        setCustomers(fRes.data);
      } catch (err) {
        console.error("Analytics fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  /* Derived: filtered + sorted customers */
  const filtered = useMemo(() => {
    return customers.filter((c) => {
      if (fCountry !== "all" && c.country !== fCountry) return false;
      if (fBand !== "all" && churnBand(toNum(c.churn_risk)) !== fBand) return false;
      if ((c.review_score ?? 0) < fReview) return false;
      return true;
    });
  }, [customers, fCountry, fBand, fReview]);

  const sorted = useMemo(() => {
    const dir = sortDir === "asc" ? 1 : -1;
    return [...filtered].sort((a: any, b: any) => {
      let x = a[sortKey], y = b[sortKey];
      if (x == null) x = sortKey === "full_name" ? "" : -Infinity;
      if (y == null) y = sortKey === "full_name" ? "" : -Infinity;
      if (typeof x === "string" && typeof y === "string") return x.localeCompare(y) * dir;
      return (toNum(x) - toNum(y)) * dir;
    });
  }, [filtered, sortKey, sortDir]);

  const pageCount = Math.max(1, Math.ceil(sorted.length / PER_PAGE));
  const safePage = Math.min(page, pageCount - 1);
  const pageRows = sorted.slice(safePage * PER_PAGE, safePage * PER_PAGE + PER_PAGE);

  const toggleSort = useCallback((key: string) => {
    setSortKey((prev) => {
      if (prev === key) {
        setSortDir((d) => (d === "desc" ? "asc" : "desc"));
        return prev;
      }
      setSortDir("desc");
      return key;
    });
    setPage(0);
  }, []);

  const resetFilters = () => { setFCountry("all"); setFBand("all"); setFReview(1); setPage(0); };

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3200);
  };

  const runSentiment = async () => {
    try {
      await api.post("/analytics/run-sentiment");
      showToast("Sentiment analysis completed on " + filtered.length + " customers.");
    } catch { showToast("Sentiment analysis failed."); }
  };

  const runChurn = async () => {
    try {
      await api.post("/analytics/run-churn");
      showToast("Churn scoring completed for " + filtered.length + " customers.");
    } catch { showToast("Churn scoring failed."); }
  };

  /* Chart: CSS vars */
  const cssVars = useMemo(() => {
    const css = getComputedStyle(document.documentElement);
    return {
      border: css.getPropertyValue("--border").trim(),
      muted: css.getPropertyValue("--muted").trim(),
      card: css.getPropertyValue("--card").trim(),
      heading: css.getPropertyValue("--heading").trim(),
      positive: css.getPropertyValue("--positive").trim(),
      warning: css.getPropertyValue("--warning").trim(),
      danger: css.getPropertyValue("--danger").trim(),
    };
  }, [theme]);

  /* Review distribution chart */
  const reviewChartData = useMemo(() => ({
    labels: reviewDist.map((r) => r.review_score + "★"),
    datasets: [{
      data: reviewDist.map((r) => r.count),
      backgroundColor: ["#f87171", "#fb923c", "#fbbf24", "#a3e635", "#4ade80"],
      borderRadius: 7,
      barPercentage: 0.6,
    }],
  }), [reviewDist]);

  /* Churn histogram */
  const churnBuckets = useMemo(() => {
    const buckets = Array.from({ length: 10 }, (_, i) => ({
      label: i * 10 + "-" + (i * 10 + 10) + "%",
      lo: i / 10,
      count: 0,
    }));
    customers.forEach((c) => {
      const idx = Math.min(9, Math.floor(toNum(c.churn_risk) * 10));
      buckets[idx].count++;
    });
    return buckets;
  }, [customers]);

  const churnChartData = useMemo(() => ({
    labels: churnBuckets.map((b) => b.label),
    datasets: [{
      data: churnBuckets.map((b) => b.count),
      backgroundColor: churnBuckets.map((b) =>
        b.lo >= 0.66 ? cssVars.danger : b.lo >= 0.33 ? cssVars.warning : cssVars.positive
      ),
      borderRadius: 6,
      barPercentage: 0.82,
      categoryPercentage: 0.9,
    }],
  }), [churnBuckets, cssVars]);

  const barOptions = useCallback((labelCb: (c: any) => string): ChartOptions<"bar"> => ({
    responsive: true, maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: cssVars.card, titleColor: cssVars.heading,
        bodyColor: cssVars.muted, borderColor: cssVars.border,
        borderWidth: 1, padding: 10, cornerRadius: 9,
        callbacks: { label: labelCb },
      },
    },
    scales: {
      x: { grid: { display: false }, border: { color: cssVars.border }, ticks: { color: cssVars.muted, font: { family: "Poppins", size: 11 } } },
      y: { grid: { color: cssVars.border, drawTicks: false }, border: { display: false }, ticks: { color: cssVars.muted, font: { family: "Poppins", size: 11 } } },
    },
  }), [cssVars]);

  /* Churn band counts */
  const lowCount = customers.filter((c) => churnBand(toNum(c.churn_risk)) === "low").length;
  const medCount = customers.filter((c) => churnBand(toNum(c.churn_risk)) === "medium").length;
  const highCount = customers.filter((c) => churnBand(toNum(c.churn_risk)) === "high").length;

  /* Country options for filter */
  const countryOpts = useMemo(() =>
    [...new Set(customers.map((c) => c.country).filter(Boolean))].sort() as string[]
  , [customers]);

  /* Max revenue for bar widths */
  const maxRev = byCountry.length > 0 ? toNum(byCountry[0].revenue) : 1;

  /* Band button definitions */
  const bandDefs: [string, string][] = [["all", "All"], ["low", "Low"], ["medium", "Med"], ["high", "High"]];
  const bandColor: Record<string, string> = { all: "var(--accent)", low: "var(--positive)", medium: "var(--warning)", high: "var(--danger)" };

  /* Column definitions for customer table */
  const colDefs: [string, string, string][] = [
    ["full_name", "Customer", "left"], ["total_spent", "Total spent", "right"],
    ["recency_days", "Recency", "right"], ["review_score", "Review", "right"],
    ["sentiment_score", "Sentiment", "right"], ["churn_risk", "Churn risk", "left"],
    ["churn_band", "Band", "left"], ["churn_prediction", "Prediction", "left"],
    ["confidence", "Confidence", "left"], ["country", "Country", "left"],
  ];

  if (loading) {
    return (
      <div className={styles.container}><Nav /><Header title="Analytics" subtitle="Detailed breakdowns across revenue, reviews and churn." />
        <div className={styles.loading}>Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <Nav />
      <Header title="Analytics" subtitle="Detailed breakdowns across revenue, reviews and churn." />
      <main className={styles.main}>

        {/* ── Filters bar ── */}
        <div className={styles.filterBar}>
          <div className={styles.filterLabel}><Filter size={17} />Filters</div>

          <div className={styles.filterGroup}>
            <label className={styles.filterCaption}>COUNTRY</label>
            <select className={styles.select} value={fCountry} onChange={(e) => { setFCountry(e.target.value); setPage(0); }}>
              <option value="all">All countries</option>
              {countryOpts.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div className={styles.filterGroup}>
            <label className={styles.filterCaption}>CHURN RISK BAND</label>
            <div className={styles.bandRow}>
              {bandDefs.map(([val, label]) => (
                <button key={val}
                  className={`${styles.bandBtn} ${fBand === val ? styles.bandBtnActive : ""}`}
                  style={fBand === val ? { background: bandColor[val], color: "#fff", borderColor: "transparent" } : {}}
                  onClick={() => { setFBand(val); setPage(0); }}
                >{label}</button>
              ))}
            </div>
          </div>

          <div className={styles.filterGroup}>
            <label className={styles.filterCaption}>MIN REVIEW SCORE — {fReview}★</label>
            <input type="range" min={1} max={5} step={1} value={fReview}
              onChange={(e) => { setFReview(+e.target.value); setPage(0); }}
              className={styles.rangeInput} />
          </div>

          <div className={styles.filterRight}>
            <span className={styles.matchCount}>{filtered.length} of {customers.length} customers</span>
            <button className={styles.resetBtn} onClick={resetFilters}>Reset</button>
          </div>
        </div>

        {/* ── Country table + Review dist row ── */}
        <div className={styles.twoCol}>
          {/* Country table */}
          <div className={styles.card} style={{ padding: 24 }}>
            <div className={styles.cardTitle}>Revenue by country</div>
            <div className={styles.cardSub}>Revenue, customers and avg review per market</div>
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th className={styles.th}>COUNTRY</th>
                    <th className={`${styles.th} ${styles.thRight}`}>REVENUE</th>
                    <th className={`${styles.th} ${styles.thRight}`}>CUST.</th>
                    <th className={`${styles.th} ${styles.thRight}`}>AVG REVIEW</th>
                    <th className={`${styles.th} ${styles.thRight}`}>ARPC</th>
                  </tr>
                </thead>
                <tbody>
                  {byCountry
                    .filter((c) => fCountry === "all" || c.country === fCountry)
                    .map((c) => (
                    <tr key={c.country} className={styles.tr}>
                      <td className={styles.td}>
                        <div className={styles.countryCell}>
                          <span className={styles.miniBar}>
                            <span className={styles.miniBarFill} style={{ width: `${(toNum(c.revenue) / maxRev) * 100}%` }} />
                          </span>
                          <span className={styles.countryName}>{c.country}</span>
                        </div>
                      </td>
                      <td className={`${styles.td} ${styles.tdRight} ${styles.tdBold}`}>{formatMoney(toNum(c.revenue))}</td>
                      <td className={`${styles.td} ${styles.tdRight}`}>{c.customer_count}</td>
                      <td className={`${styles.td} ${styles.tdRight}`}>{c.avg_review_score != null ? c.avg_review_score.toFixed(1) : "—"}★</td>
                      <td className={`${styles.td} ${styles.tdRight}`}>{formatMoneyFull(toNum(c.avg_revenue_per_customer))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Review dist chart */}
          <div className={styles.card} style={{ padding: 24 }}>
            <div className={styles.cardTitle}>Review score distribution</div>
            <div className={styles.cardSub}>Count &amp; share per star rating</div>
            <div className={styles.chartBox} style={{ height: 230 }}>
              <Bar key={`rev-${theme}`} data={reviewChartData}
                options={barOptions((c: any) => "  " + c.parsed.y + " customers · " + (reviewDist[c.dataIndex]?.percentage ?? 0) + "%")} />
            </div>
            <div className={styles.legendRow}>
              {reviewDist.map((r) => (
                <div key={r.review_score} className={styles.legendCell}>
                  <div className={styles.legendPct}>{r.percentage}%</div>
                  <div className={styles.legendLabel}>{r.review_score}★</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Churn breakdown ── */}
        <div className={styles.card} style={{ padding: 24 }}>
          <div className={styles.churnHeader}>
            <div>
              <div className={styles.cardTitle}>Churn risk breakdown</div>
              <div className={styles.cardSub}>Distribution of predicted churn probability across customers</div>
            </div>
            <div className={styles.churnPills}>
              <span className={styles.pillLow}>Low {lowCount}</span>
              <span className={styles.pillMed}>Medium {medCount}</span>
              <span className={styles.pillHigh}>High {highCount}</span>
            </div>
          </div>
          <div className={styles.chartBox} style={{ height: 240 }}>
            <Bar key={`churn-${theme}`} data={churnChartData}
              options={barOptions((c: any) => "  " + c.parsed.y + " customers")} />
          </div>
        </div>

        {/* ── Customer features table ── */}
        <div className={styles.card} style={{ padding: 24 }}>
          <div className={styles.tableToolbar}>
            <div>
              <div className={styles.cardTitle}>Customer features</div>
              <div className={styles.cardSub}>Click any column header to sort · {filtered.length} matching customers</div>
            </div>
            <div className={styles.toolbarBtns}>
              <button className={styles.outlineBtn} onClick={runSentiment}>
                <Smile size={15} />Run sentiment
              </button>
              <button className={styles.accentBtn} onClick={runChurn}>
                <RefreshCw size={15} />Run churn scoring
              </button>
            </div>
          </div>

          {toast && (
            <div className={styles.toast}><Check size={16} strokeWidth={2.4} />{toast}</div>
          )}

          <div className={styles.tableWrap}>
            <table className={styles.tableWide}>
              <thead>
                <tr>
                  {colDefs.map(([key, label, align]) => (
                    <th key={key}
                      className={`${styles.thSort} ${align === "right" ? styles.thRight : ""}`}
                      onClick={() => toggleSort(key)}>
                      <span className={styles.thInner}>
                        {label}
                        {sortKey === key && <span className={styles.arrow}>{sortDir === "asc" ? "▲" : "▼"}</span>}
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {pageRows.map((c) => {
                  const band = churnBand(toNum(c.churn_risk));
                  const pred = churnPrediction(toNum(c.churn_risk));
                  const conf = confidenceLabel(toNum(c.churn_risk));
                  const sent = toNum(c.sentiment_score);
                  return (
                    <tr key={c.id} className={styles.tr}>
                      <td className={styles.td}>
                        <div className={styles.customerCell}>
                          <span className={styles.avatar}>{initials(c.full_name)}</span>
                          <span className={styles.custName}>{c.full_name}</span>
                        </div>
                      </td>
                      <td className={`${styles.td} ${styles.tdRight} ${styles.tdBold}`}>{formatMoneyFull(toNum(c.total_spent))}</td>
                      <td className={`${styles.td} ${styles.tdRight}`}>{c.recency_days ?? "—"}d</td>
                      <td className={`${styles.td} ${styles.tdRight}`}>{c.review_score ?? "—"}★</td>
                      <td className={`${styles.td} ${styles.tdRight}`}>
                        <span className={sent > 0.2 ? styles.sentPositive : sent < -0.2 ? styles.sentNegative : styles.sentNeutral}>
                          {sent >= 0 ? "+" : ""}{sent.toFixed(2)}
                        </span>
                      </td>
                      <td className={styles.td}>
                        <div className={styles.churnBarCell}>
                          <span className={styles.churnTrack}>
                            <span className={styles.churnFill} style={{
                              width: `${toNum(c.churn_risk) * 100}%`,
                              background: band === "high" ? "var(--danger)" : band === "medium" ? "var(--warning)" : "var(--positive)",
                            }} />
                          </span>
                          <span>{Math.round(toNum(c.churn_risk) * 100)}%</span>
                        </div>
                      </td>
                      <td className={styles.td}><span className={`${styles.pill} ${styles["pill_" + band]}`}>{band.charAt(0).toUpperCase() + band.slice(1)}</span></td>
                      <td className={styles.td}>{pred}</td>
                      <td className={styles.td}><span className={`${styles.confPill} ${styles["conf_" + conf]}`}>{conf}</span></td>
                      <td className={styles.td}>{c.country ?? "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className={styles.pagination}>
            <span className={styles.pageInfo}>Showing {sorted.length ? safePage * PER_PAGE + 1 : 0}–{Math.min(sorted.length, safePage * PER_PAGE + PER_PAGE)} of {filtered.length}</span>
            <div className={styles.pageBtns}>
              <button className={styles.pageBtn} disabled={safePage === 0} onClick={() => setPage((p) => p - 1)}>Prev</button>
              <button className={styles.pageBtn} disabled={safePage >= pageCount - 1} onClick={() => setPage((p) => p + 1)}>Next</button>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
};

export default Analytics;