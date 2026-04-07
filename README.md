# 🏨 Hotel Financial KPI Dataset – PoC README

## 📌 Project Context
**Title:** Del Dashboard al Insight Financiero con IA: Análisis y Comentarios Automáticos del Reporting Package Hotelero

This dataset has been synthetically generated to support a Proof of Concept (PoC) focused on transforming hotel dashboards into automated financial insights using AI.

The goal is to simulate a realistic hotel reporting environment where key performance indicators (KPIs) can be analyzed and translated into natural language commentary.

---

## 🎯 Scope of the PoC

This PoC focuses exclusively on the **core hotel revenue KPIs**, which are the industry standard for performance analysis:

- Occupancy Rate
- ADR (Average Daily Rate)
- RevPAR (Revenue per Available Room)

Additionally, the dataset includes **Month-over-Month (MoM) variation metrics**, enabling the generation of automated insights.

---

## 📊 Dataset Overview

- **Granularity:** Monthly
- **Time Range:** January 2023 – December 2024
- **Entities:** 3 hotels
- **Type:** Synthetic (simulated but realistic distributions)

Each row represents the performance of one hotel in a given month.

---

## 🧾 Data Dictionary

### 🔹 Identifiers
- `hotel_name`: Name of the hotel
- `month`: Reporting period (YYYY-MM)

---

### 🔹 Core KPIs

#### 1. Occupancy Rate (`occupancy_rate`)
- Definition: Percentage of available rooms that were sold
- Formula:
  Occupancy = Rooms Sold / Rooms Available

---

#### 2. ADR – Average Daily Rate (`ADR`)
- Definition: Average revenue earned per sold room
- Formula:
  ADR = Revenue Rooms / Rooms Sold

---

#### 3. RevPAR – Revenue per Available Room (`RevPAR`)
- Definition: Revenue generated per available room
- Formula:
  RevPAR = Revenue Rooms / Rooms Available
  OR
  RevPAR = ADR × Occupancy

---

### 🔹 Supporting Operational Metrics

- `rooms_available`: Total available rooms per period
- `rooms_sold`: Total rooms sold
- `revenue_rooms`: Revenue from room sales

---

### 🔹 Financial Metrics (contextual, not core for PoC)

- `revenue_FnB`: Food & Beverage revenue
- `total_revenue`: Total hotel revenue
- `operating_costs`: Operational expenses
- `GOP`: Gross Operating Profit

---

### 🔹 Derived Metrics (Critical for AI Insights)

#### Month-over-Month Change (%)

- `RevPAR_mom_change_%`
- `ADR_mom_change_%`
- `occupancy_rate_mom_change_%`

Definition:
Percentage change compared to the previous month for the same hotel.

---

## 🤖 AI Use Case

The dataset is designed to support the development of an AI layer capable of:

### 1. Trend Detection
- Identify increases, decreases, or stability in KPIs

### 2. Driver Analysis
- Explain *why* a KPI changed
  - Demand-driven (Occupancy)
  - Price-driven (ADR)

### 3. Automated Commentary Generation

Example outputs:

- "RevPAR increased 8% compared to last month, driven by higher occupancy while ADR remained stable."
- "ADR declined despite stable occupancy, suggesting pricing pressure."
- "Performance improvement was driven primarily by demand growth."

---

## 🧠 Analytical Logic for the PoC

The PoC can implement rule-based or AI-based logic such as:

- If RevPAR ↑ and ADR ↑ → Pricing-driven growth
- If RevPAR ↑ and Occupancy ↑ → Demand-driven growth
- If ADR ↓ and Occupancy ↑ → Volume strategy
- If RevPAR ↓ → Performance decline

---

## ⚠️ Limitations

- Synthetic data (not real hotel data)
- No competitor benchmarking (e.g., RevPAR Index)
- No segmentation (e.g., leisure vs business)
- No daily granularity

---

## 🚀 Future Enhancements

To extend the PoC:

- Add Budget vs Actuals
- Include seasonality flags
- Incorporate external demand drivers (events, holidays)
- Add competitor benchmarking KPIs
- Train ML/NLP models for commentary generation

---

## ✅ Summary

This dataset provides a minimal but robust foundation to:

- Build a KPI dashboard
- Detect performance changes
- Generate automated financial insights

It is intentionally scoped to the **three core KPIs** to ensure clarity, focus, and feasibility for a PoC.
