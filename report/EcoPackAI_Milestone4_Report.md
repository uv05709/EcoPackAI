# EcoPackAI Milestone 4 Report

## 1. Overview
EcoPackAI is an AI framework that predicts packaging cost and CO2 impact, then ranks materials with an eco score to recommend sustainable options. Milestone 4 focuses on business intelligence insights, report exports, and deployment readiness.

## 2. BI Dashboard Highlights
- CO2 reduction percentage calculated against baseline averages.
- Cost savings percentage for top-ranked materials.
- Material usage trends and average cost/CO2 by material type.
- Interactive charts rendered in the frontend dashboard.

## 3. Sustainability Reporting
- PDF report export for quick sharing and stakeholder review.
- Excel report export for analysts and operational teams.
- Reports include baseline metrics, top-N averages, and ranked materials.

## 4. Deployment Readiness
- `Procfile` for Heroku (`gunicorn backend.app:app`).
- `render.yaml` for Render deploy flow.
- Environment variable support for PostgreSQL credentials.

## 5. Results Summary
- Dataset baseline averages vs top-ranked materials highlight measurable savings.
- Dashboard provides rapid insight into material tradeoffs.
- Exportable reports enable audit and compliance workflows.

## 6. Next Steps
- Add automated tests for analytics endpoints.
- Introduce scheduled model retraining and versioned reports.
- Expand dashboard with time-based trends when real production logs are available.
