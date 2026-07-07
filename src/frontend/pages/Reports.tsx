import { useState, useEffect } from "react";
import styles from "./Reports.module.css";
import Header from "../components/Header";
import Nav from "../components/Nav";
import api from "../api/Client";
import { DollarSign, AlertTriangle, Smile, Globe, Download, FileText, Check } from "lucide-react";
import { toNum, csvDownload, churnBand, churnPrediction, confidenceLabel } from "../utils/Helpers";
import type { CountryStat, CustomerFeature } from "../utils/Helpers";

const Reports = () => {
  const [countries, setCountries] = useState<CountryStat[]>([]);
  const [customers, setCustomers] = useState<CustomerFeature[]>([]);
  const [toast, setToast] = useState("");

  useEffect(() => {
    Promise.all([
      api.get("/analytics/by-country"),
      api.get("/analytics/customer-features"),
    ]).then(([cRes, fRes]) => {
      setCountries(cRes.data);
      setCustomers(fRes.data);
    }).catch((err) => console.error("Reports fetch error:", err));
  }, []);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3500);
  };

  const dlRevenue = () => {
    csvDownload("revenue_summary.csv",
      ["country", "revenue", "customer_count", "avg_revenue_per_customer", "avg_review_score"],
      countries.map((c) => [c.country, toNum(c.revenue), c.customer_count, toNum(c.avg_revenue_per_customer), c.avg_review_score])
    );
    showToast("revenue_summary.csv downloaded (" + countries.length + " rows).");
  };

  const dlChurn = () => {
    csvDownload("churn_report.csv",
      ["id", "full_name", "country", "churn_risk", "churn_band", "churn_prediction", "confidence", "recency_days"],
      customers.map((c) => [c.id, c.full_name, c.country, toNum(c.churn_risk), churnBand(toNum(c.churn_risk)), churnPrediction(toNum(c.churn_risk)), confidenceLabel(toNum(c.churn_risk)), c.recency_days])
    );
    showToast("churn_report.csv downloaded (" + customers.length + " rows).");
  };

  const dlSentiment = () => {
    csvDownload("sentiment_report.csv",
      ["id", "full_name", "review_score", "sentiment_score"],
      customers.map((c) => [c.id, c.full_name, c.review_score, toNum(c.sentiment_score)])
    );
    showToast("sentiment_report.csv downloaded (" + customers.length + " rows).");
  };

  const dlCountry = () => {
    csvDownload("country_breakdown.csv",
      ["country", "revenue", "customer_count", "avg_review_score", "avg_revenue_per_customer"],
      countries.map((c) => [c.country, toNum(c.revenue), c.customer_count, c.avg_review_score, toNum(c.avg_revenue_per_customer)])
    );
    showToast("country_breakdown.csv downloaded (" + countries.length + " rows).");
  };

  const reports = [
    { title: "Revenue summary", desc: "Aggregated revenue, customer counts and average revenue per customer, broken down by country.", icon: DollarSign, iconClass: styles.iconPositive, rows: countries.length, action: dlRevenue },
    { title: "Churn report", desc: "Per-customer churn risk score, predicted outcome, confidence label and recency for the entire base.", icon: AlertTriangle, iconClass: styles.iconDanger, rows: customers.length, action: dlChurn },
    { title: "Sentiment report", desc: "Review text, star rating and computed sentiment score for every customer review on record.", icon: Smile, iconClass: styles.iconAccent, rows: customers.length, action: dlSentiment },
    { title: "Country breakdown", desc: "Full geographic breakdown of revenue, customers and review performance across all markets.", icon: Globe, iconClass: styles.iconWarning, rows: countries.length, action: dlCountry },
  ];

  return (
    <div className={styles.container}>
      <Nav />
      <Header title="Reports" subtitle="Export your customer data as ready-to-share CSV files." />
      <main className={styles.main}>
        {toast && (
          <div className={styles.toast}><Check size={18} strokeWidth={2.4} />{toast}</div>
        )}

        <div className={styles.grid}>
          {reports.map((r) => (
            <div key={r.title} className={styles.card}>
              <div className={styles.cardBody}>
                <div className={`${styles.iconTile} ${r.iconClass}`}>
                  <r.icon size={24} />
                </div>
                <div className={styles.cardText}>
                  <div className={styles.cardTitle}>{r.title}</div>
                  <div className={styles.cardDesc}>{r.desc}</div>
                </div>
              </div>
              <div className={styles.cardFooter}>
                <div className={styles.meta}>
                  <FileText size={14} />{r.rows} rows · CSV
                </div>
                <button className={styles.dlBtn} onClick={r.action}>
                  <Download size={16} />Download CSV
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};

export default Reports;