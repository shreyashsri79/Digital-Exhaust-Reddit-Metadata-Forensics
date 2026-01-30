import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import datetime


INPUT_FILE = "../raw-data/output.json"
OUTPUT_DIR = "../processed-data"

class ForensicAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.timezone_offset = 0
        self.estimated_timezone = "Unknown"
        
        
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"📁 Created output directory: {OUTPUT_DIR}")

    def run_suite(self):
        print("--- 🕵️ Starting Forensic Analysis ---")
        self.load_data()
        self.process_timestamps()
        
        # 1. logical Analysis
        self.estimate_timezone()
        
        # 2. Visual Analysis
        self.plot_hourly_bar()      # Bar Graph
        self.plot_weekly_pie()      # Pie Chart
        self.plot_heatmap()         # Heatmap
        
        # 3. Text Report
        self.generate_report()
        print(f"--- ✅ Analysis Complete. Check {OUTPUT_DIR}/ ---")

    def load_data(self):
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            self.df = pd.DataFrame(data["timestamps"], columns=["unix_time"])
        except Exception as e:
            print(f"❌ Error: {e}")
            exit()

    def process_timestamps(self):

        self.df['datetime'] = pd.to_datetime(self.df['unix_time'], unit='s')
        self.df['hour'] = self.df['datetime'].dt.hour
        self.df['day_of_week'] = self.df['datetime'].dt.dayofweek # 0=Mon, 6=Sun
        self.df['is_weekend'] = self.df['day_of_week'] >= 5

    def estimate_timezone(self):
        """
        Logic: The deepest 6-hour lull in activity usually centers around 4 AM local time.
        """
        # Count activity per hour
        hourly_counts = self.df['hour'].value_counts().reindex(range(24), fill_value=0)
        
        # Find the 6-hour window with LEAST activity
        min_activity = float('inf')
        sleep_center_utc = 0
        
        for i in range(24):
            # Sum activity for a 6-hour window (handling wrap-around for midnight)
            window_sum = 0
            for j in range(6):
                window_sum += hourly_counts[(i + j) % 24]
            
            if window_sum < min_activity:
                min_activity = window_sum
                # The "center" of this window is i + 3
                sleep_center_utc = (i + 3) % 24

        # HEURISTIC: Humans typically are deepest asleep around 04:00 Local Time.
        # So, Local Time = UTC + Offset => 4 = SleepCenterUTC + Offset
        # Offset = 4 - SleepCenterUTC
        offset = 4 - sleep_center_utc
        
        # Normalize offset to +/- 12 range
        if offset < -12: offset += 24
        elif offset > 12: offset -= 24
        
        self.timezone_offset = offset
        self.estimated_timezone = f"UTC {offset:+d}:00"
        print(f"🧠 Estimated Sleep Center (UTC): {sleep_center_utc}:00")
        print(f"🌍 Estimated Timezone: {self.estimated_timezone}")

    def plot_hourly_bar(self):
        """Generates a Bar Chart of Peak Activity Hours."""
        plt.figure(figsize=(10, 6))
        
        # Group by hour
        hourly_data = self.df['hour'].value_counts().sort_index()
        
        # Plot
        colors = plt.cm.viridis(np.linspace(0, 1, 24))
        bars = plt.bar(hourly_data.index, hourly_data.values, color=colors)
        
        plt.title(f"Activity Distribution (Peak Analysis) - Est. {self.estimated_timezone}")
        plt.xlabel("Hour of Day (UTC)")
        plt.ylabel("Activity Count")
        plt.xticks(range(24))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        path = f"{OUTPUT_DIR}/1_hourly_activity_bar.png"
        plt.savefig(path)
        plt.close()

    def plot_weekly_pie(self):
        """Generates a Pie Chart of Weekday vs. Weekend Activity."""
        plt.figure(figsize=(8, 8))
        
        counts = self.df['is_weekend'].value_counts()
        # Rename True/False to Weekend/Weekday
        labels = [('Weekend' if x else 'Weekday') for x in counts.index]
        
        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff'])
        plt.title("Work-Life Balance Indicator (Weekday vs Weekend)")
        
        path = f"{OUTPUT_DIR}/2_weekend_ratio_pie.png"
        plt.savefig(path)
        plt.close()

    def plot_heatmap(self):
        """Generates the main Sleep Cycle Heatmap."""
        plt.figure(figsize=(12, 6))
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.df['day_name'] = self.df['datetime'].dt.day_name()
        
        heatmap_data = self.df.pivot_table(
            index='day_name', 
            columns='hour', 
            aggfunc='size', 
            fill_value=0
        ).reindex(days).reindex(columns=range(24), fill_value=0)

        sns.heatmap(heatmap_data, cmap="magma", linewidths=.5)
        plt.title("Circadian Rhythm Fingerprint")
        
        path = f"{OUTPUT_DIR}/3_sleep_heatmap.png"
        plt.savefig(path)
        plt.close()

    def generate_report(self):
        """Writes a summary text file."""
        total_posts = len(self.df)
        first_seen = self.df['datetime'].min()
        last_seen = self.df['datetime'].max()
        
        report = f"""
FORENSIC ANALYSIS REPORT
========================
Subject Data Points: {total_posts}
Date Range: {first_seen} to {last_seen}

INFERENCE RESULTS
-----------------
Estimated Timezone: {self.estimated_timezone} (Confidence: Medium)
Calculated Offset: {self.timezone_offset} hours from UTC
Likely Region: {self.get_region_guess(self.timezone_offset)}

BEHAVIORAL STATS
----------------
Most Active Hour (UTC): {self.df['hour'].mode()[0]}:00
Activity Ratio: {self.df['is_weekend'].mean()*100:.1f}% Weekend / {(1-self.df['is_weekend'].mean())*100:.1f}% Weekday
        """
        
        with open(f"{OUTPUT_DIR}/report.txt", "w") as f:
            f.write(report)

    def get_region_guess(self, offset):
# Expanded lookup for common timezones (UTC offsets)
        regions = {
    -12: "Baker Island / Howland Island",
    -11: "American Samoa",
    -10: "Hawaii (HST)",
    -9.5: "Marquesas Islands",
    -9: "Alaska",
    -8: "US West Coast (Los Angeles, Vancouver)",
    -7: "US Mountain Time (Denver, Phoenix*)",
    -6: "US Central Time (Chicago, Mexico City)",
    -5: "US East Coast (New York, Toronto)",
    -4: "Atlantic Time (Canada) / Caribbean",
    -3.5: "Newfoundland",
    -3: "Brazil / Argentina / Uruguay",
    -2: "South Georgia & Sandwich Islands",
    -1: "Azores / Cape Verde",
     0: "UK / Ireland / Portugal / West Africa",
     1: "Central Europe (Germany, France, Italy)",
     2: "Eastern Europe / South Africa",
     3: "Moscow / East Africa",
     3.5: "Iran",
     4: "Gulf States (UAE, Oman)",
     4.5: "Afghanistan",
     5: "Pakistan / West Asia",
     5.5: "India (IST)",
     5.75: "Nepal",
     6: "Bangladesh / Bhutan",
     6.5: "Myanmar",
     7: "Thailand / Vietnam / Indonesia (WIB)",
     8: "China / Singapore / Western Australia",
     8.75: "Western Australia (Eucla)",
     9: "Japan / Korea",
     9.5: "Central Australia (ACST)",
     10: "Eastern Australia / Papua New Guinea",
     10.5: "Lord Howe Island",
     11: "Solomon Islands",
     12: "New Zealand / Fiji",
     12.75: "Chatham Islands",
     13: "New Zealand (Summer)",
     14: "Line Islands (Kiribati)"
}

        # Rounding for simple integer matching
        return regions.get(round(offset), "Unknown Region")

# --- EXECUTION ---
if __name__ == "__main__":
    analyzer = ForensicAnalyzer(INPUT_FILE)
    analyzer.run_suite()