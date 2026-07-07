import { useState, useRef } from "react";
import styles from "./DataUpload.module.css";
import Header from "../components/Header";
import Nav from "../components/Nav";
import api from "../api/Client";
import { Upload, FileCheck, Info, X, Check } from "lucide-react";

function fmtSize(b: number): string {
  if (b < 1024) return b + " B";
  if (b < 1048576) return (b / 1024).toFixed(1) + " KB";
  return (b / 1048576).toFixed(2) + " MB";
}

const schema = [
  { name: "full_name", desc: "Customer full name", tag: "required" },
  { name: "email", desc: "Unique email address", tag: "required" },
  { name: "country", desc: "Country of residence", tag: "required" },
  { name: "total_spent", desc: "Lifetime spend", tag: "required" },
  { name: "last_purchase_date", desc: "YYYY-MM-DD", tag: "required" },
  { name: "review_score", desc: "Star rating 1–5", tag: "required" },
  { name: "review_text", desc: "Free-text review", tag: "optional" },
];

const DataUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [banner, setBanner] = useState("");
  const [bannerOk, setBannerOk] = useState(true);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const showBanner = (msg: string, ok: boolean) => {
    setBanner(msg);
    setBannerOk(ok);
    if (ok) setTimeout(() => setBanner(""), 5000);
  };

  const takeFile = (f: File | undefined) => {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".csv")) {
      showBanner('Only .csv files are accepted. "' + f.name + '" was rejected.', false);
      return;
    }
    if (f.size > 5 * 1024 * 1024) {
      showBanner(f.name + " is " + fmtSize(f.size) + " — over the 5MB limit.", false);
      return;
    }
    setFile(f);
    setBanner("");
  };

  const doUpload = async () => {
    if (!file) {
      showBanner("Please choose a CSV file first.", false);
      return;
    }
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await api.post("/utils/upload/customers", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      showBanner('Success — "' + file.name + '" uploaded. ' + (res.data.message || ""), true);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err: any) {
      showBanner(err.response?.data?.detail || "Upload failed. Please try again.", false);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Nav />
      <Header title="Upload" subtitle="Import customers from a CSV file." />
      <main className={styles.main}>

        {banner && (
          <div className={`${styles.banner} ${bannerOk ? styles.bannerOk : styles.bannerErr}`}>
            {bannerOk && <Check size={18} strokeWidth={2.4} />}
            <span className={styles.bannerText}>{banner}</span>
            <button className={styles.bannerClose} onClick={() => setBanner("")}><X size={16} /></button>
          </div>
        )}

        <div className={styles.grid}>
          {/* Uploader card */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Upload customer CSV</div>
            <div className={styles.cardSub}>Drop your file below or browse to select.</div>

            <label
              className={`${styles.dropzone} ${dragging ? styles.dropzoneActive : ""} ${file ? styles.dropzoneReady : ""}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={(e) => { e.preventDefault(); setDragging(false); }}
              onDrop={(e) => { e.preventDefault(); setDragging(false); takeFile(e.dataTransfer.files[0]); }}
            >
              <input ref={inputRef} type="file" accept=".csv" onChange={(e) => takeFile(e.target.files?.[0])} style={{ display: "none" }} />
              {!file ? (
                <>
                  <div className={`${styles.dzIcon} ${styles.dzIconAccent}`}><Upload size={28} /></div>
                  <div className={styles.dzTitle}>Drag &amp; drop your CSV here</div>
                  <div className={styles.dzHint}>or <span className={styles.dzLink}>browse files</span> · max 5MB</div>
                </>
              ) : (
                <>
                  <div className={`${styles.dzIcon} ${styles.dzIconGreen}`}><FileCheck size={28} /></div>
                  <div className={styles.dzFileName}>{file.name}</div>
                  <div className={styles.dzHint}>{fmtSize(file.size)} · ready to upload</div>
                </>
              )}
            </label>

            <div className={styles.btnRow}>
              <button className={styles.uploadBtn} onClick={doUpload} disabled={uploading}>
                <Upload size={16} />{uploading ? "Uploading..." : "Upload file"}
              </button>
              {file && (
                <button className={styles.clearBtn} onClick={() => { setFile(null); if (inputRef.current) inputRef.current.value = ""; }}>
                  Clear
                </button>
              )}
            </div>
            <div className={styles.footerNote}>
              <Info size={14} />Maximum file size is 5MB. Only .csv files are accepted.
            </div>
          </div>

          {/* Schema card */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Required schema</div>
            <div className={styles.cardSub}>Your CSV header row must contain these columns.</div>
            <div className={styles.schemaList}>
              {schema.map((f) => (
                <div key={f.name} className={styles.schemaRow}>
                  <code className={styles.schemaCode}>{f.name}</code>
                  <span className={styles.schemaDesc}>{f.desc}</span>
                  <span className={f.tag === "required" ? styles.tagRequired : styles.tagOptional}>{f.tag}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DataUpload;