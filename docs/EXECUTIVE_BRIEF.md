# Executive Brief – Conut AI Chief of Operations Agent  
**Max 2 pages | Export to PDF for submission**

---

## Problem Framing

Conut’s operational data (sales, attendance, branches, menu mix) is underused for day-to-day decisions. The goal is an **AI Chief of Operations Agent** that turns this data into clear, actionable outputs for combos, demand, expansion, staffing, and beverage growth, with **OpenClaw** able to query the system in practice.

---

## Top Findings

1. **Combo optimization** – Frequently bought-together pairs are identified from line-item sales; top pairs and combo suggestions are exposed via API for promotions and bundling.  
2. **Demand by branch** – Simple per-branch forecasts (e.g. average of recent months in scaled units) support inventory and supply chain planning.  
3. **Expansion** – Existing branches show consistent scaled performance; expansion is feasible with candidate criteria (traffic, demographics, delivery overlap).  
4. **Staffing** – Recommended employees per shift per branch are derived from historical attendance and demand; recommendations are available via API.  
5. **Coffee and milkshake** – Top products and growth strategies (bundling, promotions, cross-sell) are data-derived and exposed for strategy prompts.

---

## Recommended Actions

- Run the pipeline regularly (e.g. weekly) to refresh artifacts.  
- Use the API from OpenClaw for ad-hoc queries (demand, staffing, combos, strategy).  
- Treat all numeric outputs as **scaled/relative**; use for comparison and trends, not absolute currency.  
- Consider adding more sophisticated forecasting (e.g. time-series models) and A/B tests for combo and beverage strategies.

---

## Expected Impact and Risks

- **Impact**: Faster, consistent answers to operational questions; one place for demand, staffing, combos, and strategy; OpenClaw-enabled access for non-technical users.  
- **Risks**: Scaled data limits absolute planning; model simplicity may need tuning as data grows; API and OpenClaw must be available and secured in production.

---

*Conut AI Engineering Hackathon | AUB*
