
# 🕵️ Digital Exhaust: Reddit Metadata Forensics

> *"Privacy isn't just about **what** you say. It's about **when** you say it."*

## 📖 About The Project

**Digital Exhaust** is a research tool designed to demonstrate how public metadata can be used to fingerprint anonymous users. By analyzing the **timestamps** (`created_utc`) of a user's activity on Reddit, this tool allows researchers to infer highly personal attributes without ever reading the content of the posts.

### Key Capabilities:

* **🌍 Timezone Inference:** Predicts a user's location based on activity "lulls" (sleep cycles).
* **🛌 Sleep Cycle Analysis:** Visualizes circadian rhythms to identify sleep deprivation or irregular shifts.
* **💼 Employment Estimator:** Distinguishes between students, freelancers, and 9-to-5 employees based on weekday vs. weekend activity ratios.

---

## 🏗️ Architecture

This project uses a **Hybrid Architecture** to balance performance with analytical power.

1. **Ingestion Engine (Go):** A high-concurrency scraper using the "Worker Pool" pattern. It bypasses bot detection and streams raw timestamp data into storage.
2. **Analysis Brain (Python):** A forensic script that ingests the raw timestamps, applies the "Sleep Gap" algorithm, and generates visual evidence (Heatmaps/Bar Charts).

---

## ⚡ Prerequisities

* **Go** (Golang) 1.20+
* **Python** 3.8+
* **Python Libraries:** `pandas`, `matplotlib`, `seaborn`

```bash
pip install pandas matplotlib seaborn

```

---

## 🚀 Usage

### Step 1: Harvest Data (Go)

The Go engine fetches user data and normalizes it into a JSON dataset.

1. Open `.env.example` and set your target username:
```env
user=yourUser

```


2. Run the scraper:
```bash
go run project/data-processor/cmd

```


3. **Output:** A file named `raw_data.json` (or `dataset.jsonl`) will be generated.

### Step 2: Analyze Forensics (Python)

The Python script digests the raw data to find patterns.

1. Run the analyzer:
```bash
project/data-processor/analyzer.py

```
### Alternatively you can 
Run the zsh file:
```bash
.project/run.zsh

```

2. **Output:** Check the `processed-data/` folder for the report and images.

---

## 📊 Visual Output Examples

The tool generates a "Forensic Dashboard" containing:

| Metric | Visualization | Purpose |
| --- | --- | --- |
| **Sleep Pattern** | `sleep_heatmap.png` | Identifies the 6-8 hour "Valley of Silence" (Sleep). |
| **Activity Peak** | `hourly_activity_bar.png` | Shows the specific hour of day the user is most active. |
| **Work/Life** | `weekend_ratio_pie.png` | Compares M-F activity vs Sat-Sun to guess job type. |

---

## ⚠️ Ethical Disclaimer

This tool is intended for **educational and research purposes only**.

* It utilizes only **publicly available data** provided by Reddit.
* It does **not** bypass authentication or access private subreddits.
* **Do not use this tool to harass or doxx individuals.**

---

## 🤝 Contribution

Contributions are welcome! If you have a better algorithm for detecting "shift work" patterns, feel free to open a PR.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request