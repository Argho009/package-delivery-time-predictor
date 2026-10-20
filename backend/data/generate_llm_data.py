"""
backend/data/generate_llm_data.py — Generate Domain Instruction Dataset for LLM Fine-Tuning
Converts 184,000+ Indian logistics shipment records into ChatML instruction-tuning pairs
for training domain-specific models (Llama 3.2 3B / Qwen 2.5 3B).
"""

import os
import sys
import json
import random
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "processed", "unified_delivery.csv")
OUTPUT_JSONL = os.path.join(BASE_DIR, "processed", "deliverai_llm_instructions.jsonl")

# Label mappings
TRAFFIC_LEVELS = {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"}
PACKAGE_TYPES  = {0: "Small (<2 kg)", 1: "Medium (2-10 kg)", 2: "Heavy (10-25 kg)", 3: "Oversized (>25 kg)", 4: "Perishable", 5: "Hazardous"}
PRIORITIES     = {0: "Standard", 1: "Express", 2: "Overnight"}
SHIPPING_MODES = {0: "Road Freight", 1: "Air Express", 2: "Rail Freight", 3: "Sea Cargo"}

SYSTEM_PROMPT = (
    "You are 'DeliverAI Copilot', an expert AI Logistics & Supply Chain Operations Assistant "
    "dedicated to inland India freight, package delivery forecasting, and fleet optimization. "
    "Provide accurate, actionable, and professionally formatted operational responses."
)


def generate_qa_sample(row: pd.Series, sample_type: int) -> dict:
    origin = str(row.get("origin_city", "Origin")).strip()
    dest = str(row.get("destination_city", "Destination")).strip()
    dist = round(float(row.get("distance_km", 0.0)), 1)
    traffic_min = round(float(row.get("traffic_duration_min", 0.0)), 0)
    traffic_lvl = TRAFFIC_LEVELS.get(int(row.get("traffic_level_enc", 1)), "Moderate")
    weight = round(float(row.get("package_weight_kg", 5.0)), 1)
    pkg_type = PACKAGE_TYPES.get(int(row.get("package_type_enc", 1)), "Medium")
    priority = PRIORITIES.get(int(row.get("priority_enc", 0)), "Standard")
    mode = SHIPPING_MODES.get(int(row.get("shipping_mode_enc", 0)), "Road Freight")
    actual_hours = round(float(row.get("actual_time_hours", 0.0)), 2)

    hours_int = int(actual_hours)
    mins_int = int(round((actual_hours - hours_int) * 60))
    time_str = f"{hours_int}h {mins_int}m" if actual_hours > 0 else "N/A"

    # Type 1: Transit Duration & Root Cause Breakdown
    if sample_type == 1:
        user_msg = (
            f"Analyze the shipment transit time from {origin} to {dest}.\n"
            f"• Distance: {dist} km\n"
            f"• Cargo: {weight} kg ({pkg_type})\n"
            f"• Mode: {mode} | Priority: {priority}\n"
            f"• Traffic: {traffic_lvl} ({int(traffic_min)} min baseline drive)\n\n"
            f"What is the estimated delivery time, and what operational factors influence this route?"
        )
        assistant_msg = (
            f"### Transit Estimation: {origin} to {dest}\n\n"
            f"• **Estimated Transit Time:** **{time_str}** ({actual_hours} hours)\n"
            f"• **Route Distance:** {dist} km via Indian National Highway corridors\n"
            f"• **Transit Mode:** {mode}\n\n"
            f"**Operational Delay Analysis:**\n"
            f"1. **Highway Cruising Velocity:** Commercial freight vehicles operate at an average speed of 40–55 km/h on this corridor due to terrain and toll plazas.\n"
            f"2. **Traffic Density:** {traffic_lvl} congestion adds approximately {int(traffic_min * 0.15)} minutes in urban transit bottlenecks around {origin} and {dest}.\n"
            f"3. **Cargo Handling:** Transporting {weight} kg ({pkg_type}) under {priority} priority involves standard hub loading and manifest verification."
        )

    # Type 2: Multi-Modal Speed & Cost Comparison
    elif sample_type == 2:
        air_hours = max(round(dist / 420.0 + 3.0, 1), 2.0)
        rail_hours = max(round(dist / 65.0 + 3.5, 1), 4.0)
        user_msg = (
            f"We need to dispatch {weight} kg of cargo from {origin} to {dest} ({dist} km). "
            f"How does current {mode} compare against Air Express and Rail Cargo?"
        )
        assistant_msg = (
            f"### Multi-Modal Transit Comparison ({origin} ➔ {dest} • {dist} km)\n\n"
            f"| Transit Mode | Estimated Transit | Cost Profile | Best Use Case |\n"
            f"| :--- | :--- | :--- | :--- |\n"
            f"| **Road Freight (Current)** | **{time_str}** | Economy (₹3–5/kg) | High volume, door-to-door delivery |\n"
            f"| **Air Express (✈️)** | **~{air_hours}h** | Premium (₹35–60/kg) | High-value, critical perishable freight |\n"
            f"| **Rail Cargo (🚆)** | **~{rail_hours}h** | Balanced (₹2–4/kg) | Bulk cargo, immune to highway jams |\n\n"
            f"**Recommendation:** "
            + (f"For {dist} km, Air Express can reduce delivery time by ~{max(round(actual_hours - air_hours, 1), 0.0)} hours if urgent." if dist > 400 else "For this short distance, Road Freight remains the most cost-effective and rapid option.")
        )

    # Type 3: Driver Dispatch Briefing & Waybill Notes
    elif sample_type == 3:
        user_msg = (
            f"Generate an official fleet driver dispatch briefing for shipment from {origin} to {dest}. "
            f"Cargo: {weight} kg {pkg_type}, Mode: {mode}."
        )
        assistant_msg = (
            f"### Fleet Dispatch Waybill Briefing\n\n"
            f"**Origin Terminal:** {origin} Hub\n"
            f"**Destination Receiving Hub:** {dest} Logistics Center\n"
            f"**Total Highway Distance:** {dist} km\n"
            f"**Target Arrival SLA:** Within **{time_str}**\n"
            f"**Cargo Specification:** {weight} kg ({pkg_type})\n\n"
            f"**Mandatory Fleet Directives:**\n"
            f"1. **Safety Rest Breaks:** Compulsory 30-minute rest stop after every 4 hours of continuous transit.\n"
            f"2. **FASTag Automated Tolls:** Ensure vehicle balance is topped up to avoid manual toll gate delays.\n"
            f"3. **Urban Entry Regulations:** Coordinate final approach into {dest} to avoid restricted daytime commercial no-entry hours.\n"
            f"4. **Emergency Contact:** Report any breakdown or traffic stoppage immediately via the in-cab GPS terminal."
        )

    # Type 4: Delay Mitigation Strategy
    else:
        user_msg = (
            f"A shipment from {origin} to {dest} is reporting {traffic_lvl} traffic with a {dist} km route. "
            f"What proactive steps can dispatch take to prevent SLA breach?"
        )
        assistant_msg = (
            f"### SLA Delay Mitigation Strategy: {origin} ➔ {dest}\n\n"
            f"• **Current Risk Level:** {traffic_lvl} congestion detected on corridor.\n"
            f"• **Baseline Transit:** {time_str}\n\n"
            f"**Action Plan:**\n"
            f"1. **Bypass Urban Centers:** Reroute commercial trucks via Outer Ring Road or Peripheral Expressways to avoid morning/evening metro rush hours.\n"
            f"2. **Assign Relief Drivers:** For routes exceeding 500 km ({dist} km), deploying twin-driver crews eliminates mandatory nighttime rest stoppages.\n"
            f"3. **Automated Customer Notification:** Proactively issue an updated delivery ETA window ({hours_int}h {mins_int}m ± 30m) to manage recipient expectations."
        )

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg}
        ]
    }


def main():
    print("=" * 65)
    print("  DeliverAI — Domain Instruction Dataset Generator for LLM")
    print("=" * 65)

    if not os.path.exists(CSV_PATH):
        print(f"Error: Processed CSV not found at {CSV_PATH}")
        sys.exit(1)

    print(f"[1/3] Loading logistics records from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    total_records = len(df)
    print(f"      Total available shipment records: {total_records:,}")

    # Sample representative subset for instruction tuning (e.g. 5,000 diverse Q&A pairs)
    sample_size = min(5000, total_records)
    print(f"[2/3] Synthesizing {sample_size:,} instruction-tuning pairs across 4 logistics domains...")
    
    sampled_df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
    samples = []

    for idx, row in sampled_df.iterrows():
        sample_type = (idx % 4) + 1
        qa = generate_qa_sample(row, sample_type)
        samples.append(qa)

    print(f"[3/3] Writing JSONL instruction dataset to: {OUTPUT_JSONL}")
    os.makedirs(os.path.dirname(OUTPUT_JSONL), exist_ok=True)
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"\n[✓] Successfully generated {len(samples):,} instruction training pairs!")
    print(f"    File: {OUTPUT_JSONL} ({os.path.getsize(OUTPUT_JSONL) / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    main()
