const byId = (id) => document.getElementById(id);
let latestTopRanked = [];

function getBaseUrl() {
    const raw = byId("apiBaseUrl").value.trim().replace(/\/$/, "");
    if (window.location.protocol === "https:" && raw.startsWith("http://")) {
        return raw.replace("http://", "https://");
    }
    return raw;
}

function formatNumber(value, digits = 2) {
    const num = Number(value);
    if (Number.isNaN(num)) return "--";
    return num.toFixed(digits);
}

function formatCurrency(value) {
    const num = Number(value);
    if (Number.isNaN(num)) return "--";
    return `INR ${num.toFixed(2)}`;
}

function formatCo2(value) {
    const num = Number(value);
    if (Number.isNaN(num)) return "--";
    return `${num.toFixed(2)} kg`;
}

function formatPercent(value, digits = 1) {
    const num = Number(value);
    if (Number.isNaN(num)) return "--";
    return `${num.toFixed(digits)}%`;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getScoreClass(score) {
    const num = Number(score);
    if (num >= 8) return "score-high";
    if (num >= 5) return "score-medium";
    return "score-low";
}

function getEcoSummary(score) {
    const num = Number(score);
    if (num >= 8) return "Excellent sustainability potential";
    if (num >= 5) return "Balanced eco-performance";
    return "Needs improvement in sustainability";
}

function getCostSummary(cost) {
    const num = Number(cost);
    if (num <= 10) return "Low predicted cost";
    if (num <= 25) return "Moderate predicted cost";
    return "Higher predicted cost";
}

function getCo2Summary(co2) {
    const num = Number(co2);
    if (num <= 5) return "Lower estimated carbon footprint";
    if (num <= 15) return "Moderate carbon footprint";
    return "Higher estimated carbon footprint";
}

function updateStatusElement(elementId, message, state = "neutral") {
    const el = byId(elementId);
    el.className = "status-pill";

    if (state === "success") {
        el.classList.add("status-success");
    } else if (state === "danger") {
        el.classList.add("status-danger");
    } else {
        el.classList.add("status-neutral");
    }

    el.innerHTML = `
        <i class="bi bi-circle-fill"></i>
        <span>${escapeHtml(message)}</span>
    `;
}

function renderLoading(containerId, message = "Loading...") {
    byId(containerId).innerHTML = `
        <div class="spinner-wrap">
            <span class="spinner"></span>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
}

function renderEmptyCard(containerId, iconClass, title, text) {
    byId(containerId).innerHTML = `
        <div class="empty-state-inner">
            <i class="${escapeHtml(iconClass)}"></i>
            <h4>${escapeHtml(title)}</h4>
            <p>${escapeHtml(text)}</p>
        </div>
    `;
}

function renderBadgeList(badges = []) {
    if (!Array.isArray(badges) || badges.length === 0) return "";
    return `
        <div class="inline-badges mt-2">
            ${badges
                .map((badge) => `<span class="compare-badge">${escapeHtml(badge)}</span>`)
                .join("")}
        </div>
    `;
}

function renderRelativeComparisonList(explanation) {
    const entries = explanation?.relative_comparison || [];
    if (!entries.length) {
        return `<li>No strong deltas were detected against nearby alternatives.</li>`;
    }
    return entries.map((line) => `<li>${escapeHtml(line)}</li>`).join("");
}

function renderMaterialCard(containerId, material, title = "Recommended Material") {
    const target = byId(containerId);

    if (!material) {
        renderEmptyCard(
            containerId,
            "bi bi-info-circle",
            "No material available",
            "The system did not return a material for this request."
        );
        return;
    }

    const explanation = material.explanation || {};
    const whySelected =
        explanation.why_selected ||
        "This material was selected based on its overall sustainability and cost profile.";

    target.innerHTML = `
        <div class="result-header">
            <div class="result-title">
                <div class="inline-badges">
                    <span class="rank-badge">
                        <i class="bi bi-trophy-fill"></i>
                        ${escapeHtml(title)}
                    </span>
                    <span class="type-badge">
                        <i class="bi bi-tag-fill"></i>
                        ${escapeHtml(material.material_type)}
                    </span>
                    <span class="type-badge">
                        <i class="bi bi-list-ol"></i>
                        Rank #${escapeHtml(material.rank || 1)}
                    </span>
                </div>
                <h3>${escapeHtml(material.material_name)}</h3>
                <p>AI-ranked material based on sustainability, durability, cost, and CO2 prediction.</p>
                ${renderBadgeList(material.badges)}
            </div>

            <div>
                <span class="score-badge">
                    <i class="bi bi-stars"></i>
                    Final Score: ${formatNumber(material.final_ranking_score ?? material.eco_score, 3)}
                </span>
            </div>
        </div>

        <div class="result-grid">
            <div class="metric-box">
                <div class="metric-top">
                    <span class="metric-label">Predicted Cost</span>
                    <i class="bi bi-cash-coin"></i>
                </div>
                <span class="metric-value">${formatCurrency(material.predicted_cost)}</span>
                <span class="metric-note">${getCostSummary(material.predicted_cost)}</span>
            </div>

            <div class="metric-box">
                <div class="metric-top">
                    <span class="metric-label">Predicted CO2</span>
                    <i class="bi bi-cloud-haze2-fill"></i>
                </div>
                <span class="metric-value">${formatCo2(material.predicted_co2)}</span>
                <span class="metric-note">${getCo2Summary(material.predicted_co2)}</span>
            </div>

            <div class="metric-box">
                <div class="metric-top">
                    <span class="metric-label">Durability Score</span>
                    <i class="bi bi-shield-check"></i>
                </div>
                <span class="metric-value">${formatNumber(material.durability_score, 2)}</span>
                <span class="metric-note">Strength and suitability benchmark</span>
            </div>

            <div class="metric-box">
                <div class="metric-top">
                    <span class="metric-label">Biodegradability</span>
                    <i class="bi bi-tree-fill"></i>
                </div>
                <span class="metric-value">${formatNumber(material.biodegradability_score, 2)}</span>
                <span class="metric-note">Higher is better for natural breakdown</span>
            </div>

            <div class="metric-box">
                <div class="metric-top">
                    <span class="metric-label">Recyclability</span>
                    <i class="bi bi-recycle"></i>
                </div>
                <span class="metric-value">${formatPercent(material.recyclability_percentage, 1)}</span>
                <span class="metric-note">Potential for circular reuse</span>
            </div>

            <div class="metric-box">
                <div class="metric-top">
                    <span class="metric-label">Eco Score</span>
                    <i class="bi bi-leaf-fill"></i>
                </div>
                <span class="metric-value">${formatNumber(material.eco_score, 3)}</span>
                <span class="metric-note">${getEcoSummary(material.eco_score)}</span>
            </div>
        </div>

        <div class="recommendation-note mt-3">
            <strong>Why this was selected</strong>
            <p class="mt-2 mb-2">${escapeHtml(whySelected)}</p>
            <ul class="mb-0 recommendation-points">
                ${renderRelativeComparisonList(explanation)}
            </ul>
        </div>
    `;
}

function renderTopComparison(comparisonPayload) {
    const target = byId("topComparisonCards");
    const materials = comparisonPayload?.materials || [];

    if (!materials.length) {
        target.innerHTML = `
            <div class="empty-state-inner">
                <i class="bi bi-columns-gap"></i>
                <h4>Comparison not available</h4>
                <p>Top 3 comparison will appear after recommendation is generated.</p>
            </div>
        `;
        return;
    }

    const cards = materials
        .map((material) => {
            const isWinner = Number(material.rank) === 1;
            return `
                <article class="comparison-card ${isWinner ? "comparison-winner" : ""}">
                    <div class="comparison-head">
                        <span class="comparison-rank">Rank #${escapeHtml(material.rank)}</span>
                        <span class="score-pill ${getScoreClass(material.eco_score)}">${formatNumber(material.eco_score, 3)}</span>
                    </div>
                    <h4>${escapeHtml(material.material_name)}</h4>
                    <p class="comparison-type">${escapeHtml(material.material_type)}</p>
                    ${renderBadgeList(material.badges)}
                    <div class="comparison-metrics">
                        <div><span>Predicted Cost</span><strong>${formatCurrency(material.predicted_cost)}</strong></div>
                        <div><span>Predicted CO2</span><strong>${formatCo2(material.predicted_co2)}</strong></div>
                        <div><span>Recyclability</span><strong>${formatPercent(material.recyclability_percentage, 1)}</strong></div>
                        <div><span>Biodegradability</span><strong>${formatNumber(material.biodegradability_score, 2)}</strong></div>
                        <div><span>Durability</span><strong>${formatNumber(material.durability_score, 2)}</strong></div>
                        <div><span>Final Score</span><strong>${formatNumber(material.final_ranking_score ?? material.eco_score, 3)}</strong></div>
                    </div>
                </article>
            `;
        })
        .join("");

    const winnerReason = comparisonPayload?.why_rank_1_wins
        ? `<div class="comparison-summary">${escapeHtml(comparisonPayload.why_rank_1_wins)}</div>`
        : "";

    target.innerHTML = `${winnerReason}<div class="comparison-cards-grid">${cards}</div>`;
}

function renderTopTable(bodyId, rows) {
    latestTopRanked = rows || [];
    const body = byId(bodyId);

    if (!rows || rows.length === 0) {
        body.innerHTML = `<tr><td colspan="6" class="empty-row">No ranked materials found.</td></tr>`;
        return;
    }

    body.innerHTML = rows
        .map((row, index) => {
            const scoreClass = getScoreClass(row.eco_score);
            return `
                <tr>
                    <td class="rank-cell">#${index + 1}</td>
                    <td class="material-name">${escapeHtml(row.material_name)}</td>
                    <td><span class="table-type-badge">${escapeHtml(row.material_type)}</span></td>
                    <td><span class="score-pill ${scoreClass}">${formatNumber(row.eco_score, 3)}</span></td>
                    <td>${formatCurrency(row.predicted_cost)}</td>
                    <td>${formatCo2(row.predicted_co2)}</td>
                </tr>
            `;
        })
        .join("");
}

async function callApi(path, options = {}) {
    const response = await fetch(`${getBaseUrl()}${path}`, {
        headers: {
            "Content-Type": "application/json"
        },
        ...options
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || data.message || `Request failed (${response.status})`);
    }

    return data;
}

function buildCommonLayout(yTitle) {
    return {
        margin: { t: 14, l: 48, r: 18, b: 65 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: {
            tickangle: -25,
            automargin: true,
            showgrid: false,
            zeroline: false
        },
        yaxis: {
            title: yTitle,
            gridcolor: "#e7efe9",
            zeroline: false
        },
        font: {
            family: "Poppins, sans-serif",
            color: "#355644"
        }
    };
}

function renderChart(targetId, data, layout) {
    const target = byId(targetId);

    if (!window.Plotly) {
        target.innerHTML = `<p class="text-muted">Plotly not loaded.</p>`;
        return;
    }

    Plotly.react(target, data, layout, {
        displayModeBar: false,
        responsive: true
    });
}

function renderDashboardInsights(insights = []) {
    const target = byId("dashboardInsights");

    if (!Array.isArray(insights) || insights.length === 0) {
        target.innerHTML = `
            <div class="col-12">
                <div class="insight-card">
                    <span class="insight-badge">Action Insight</span>
                    <h5>No actionable insights available</h5>
                    <p>Try changing Top N or material filter and refresh dashboard.</p>
                </div>
            </div>
        `;
        return;
    }

    target.innerHTML = insights
        .slice(0, 5)
        .map((item) => {
            const isNumericValue = typeof item.value === "number" && item.title.toLowerCase().includes("cost");
            const value = isNumericValue ? formatCurrency(item.value) : String(item.value || "--");
            return `
                <div class="col-md-6 col-lg-4">
                    <div class="insight-card">
                        <span class="insight-badge">${escapeHtml(item.badge || "Action Insight")}</span>
                        <h5>${escapeHtml(item.title || "Insight")}</h5>
                        <div class="insight-value">${escapeHtml(value)}</div>
                        <p>${escapeHtml(item.insight || "")}</p>
                        <div class="insight-action"><strong>Recommended action:</strong> ${escapeHtml(item.action || "Review this option.")}</div>
                    </div>
                </div>
            `;
        })
        .join("");
}

function renderDashboard(summary) {
    byId("kpiCo2Reduction").textContent = `${summary.savings.co2_reduction_pct}%`;
    byId("kpiCostSavings").textContent = `${summary.savings.cost_savings_pct}%`;
    byId("kpiEcoScore").textContent = summary.top_summary.avg_eco_score;
    renderDashboardInsights(summary.actionable_insights || []);

    const labels = summary.usage_trends.labels || [];

    const usageData = [
        {
            x: labels,
            y: summary.usage_trends.counts || [],
            type: "bar",
            marker: { color: "#5e966f" },
            hovertemplate: "%{x}<br>Count: %{y}<extra></extra>"
        }
    ];

    const costData = [
        {
            x: labels,
            y: summary.usage_trends.avg_cost || [],
            type: "bar",
            marker: { color: "#ba7a43" },
            hovertemplate: "%{x}<br>Avg Cost: %{y}<extra></extra>"
        }
    ];

    const co2Data = [
        {
            x: labels,
            y: summary.usage_trends.avg_co2 || [],
            type: "bar",
            marker: { color: "#2f6b52" },
            hovertemplate: "%{x}<br>Avg CO2: %{y}<extra></extra>"
        }
    ];

    renderChart("usageChart", usageData, buildCommonLayout("Count"));
    renderChart("costChart", costData, buildCommonLayout("Avg Cost"));
    renderChart("co2Chart", co2Data, buildCommonLayout("Avg CO2"));
}

async function loadDashboard() {
    updateStatusElement("dashboardStatus", "Dashboard: loading...", "neutral");

    const topN = Number(byId("topN").value) || 5;
    const filterType = byId("filterMaterialType").value || null;
    const query = `/analytics/summary?top_n=${topN}${filterType ? "&material_type=" + encodeURIComponent(filterType) : ""}`;

    try {
        const summary = await callApi(query);
        renderDashboard(summary);
        updateStatusElement("dashboardStatus", `Dashboard: updated (Top ${summary.top_summary.top_n})`, "success");
    } catch (error) {
        updateStatusElement("dashboardStatus", `Dashboard: failed (${error.message})`, "danger");
    }
}

function getFilenameFromDisposition(disposition, fallbackName) {
    if (!disposition) return fallbackName;
    const match = disposition.match(/filename="?([^"]+)"?/i);
    if (!match || !match[1]) return fallbackName;
    return match[1];
}

async function downloadReport(format) {
    const topN = Number(byId("topN").value) || 5;
    const filterType = byId("filterMaterialType").value || null;
    const query = `/reports/sustainability?format=${format}&top_n=${topN}${filterType ? "&material_type=" + encodeURIComponent(filterType) : ""}`;

    const fallbackName = format === "pdf"
        ? "EcoPackAI_Sustainability_Report.pdf"
        : "EcoPackAI_Sustainability_Report.xlsx";

    try {
        updateStatusElement("dashboardStatus", `Dashboard: preparing ${format.toUpperCase()} report...`, "neutral");
        const response = await fetch(`${getBaseUrl()}${query}`, { method: "GET" });
        if (!response.ok) {
            let errorMessage = `Download failed (${response.status})`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.message || errorMessage;
            } catch (error) {
                // keep fallback message
            }
            throw new Error(errorMessage);
        }

        const blob = await response.blob();
        const filename = getFilenameFromDisposition(
            response.headers.get("Content-Disposition"),
            fallbackName
        );

        const objectUrl = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = objectUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(objectUrl);

        updateStatusElement("dashboardStatus", `Dashboard: ${format.toUpperCase()} report downloaded`, "success");
    } catch (error) {
        updateStatusElement("dashboardStatus", `Dashboard: ${error.message}`, "danger");
    }
}

async function loadMaterialTypes() {
    try {
        const data = await callApi("/metadata/material-types");

        const materialTypeSelect = byId("materialType");
        materialTypeSelect.innerHTML = "";

        data.material_types.forEach((type) => {
            const option = document.createElement("option");
            option.value = type;
            option.textContent = type;
            materialTypeSelect.appendChild(option);
        });

        updateStatusElement("healthStatus", `Status: connected (${data.count} material types loaded)`, "success");
    } catch (error) {
        updateStatusElement("healthStatus", `Status: failed to load material types (${error.message})`, "danger");
    }
}

async function loadFilterMaterialTypes() {
    try {
        const data = await callApi("/metadata/material-types");

        const select = byId("filterMaterialType");
        select.innerHTML = `<option value="">All Types</option>`;

        data.material_types.forEach((type) => {
            const option = document.createElement("option");
            option.value = type;
            option.textContent = type;
            select.appendChild(option);
        });
    } catch (error) {
        console.warn("Failed to load filter types", error);
    }
}

async function checkHealth() {
    try {
        const health = await callApi("/health");
        updateStatusElement(
            "healthStatus",
            `Status: backend healthy, dataset rows: ${health.dataset_rows}`,
            "success"
        );
    } catch (error) {
        updateStatusElement(
            "healthStatus",
            `Status: backend unhealthy (${error.message})`,
            "danger"
        );
    }
}

async function datasetRecommendation() {
    renderLoading("datasetBestCard", "Generating best dataset material...");
    renderTopTable("datasetTopBody", []);
    renderTopComparison(null);

    try {
        const topN = Number(byId("topN").value) || 5;
        const filterType = byId("filterMaterialType").value || null;

        const query = `/recommend?top_n=${topN}${filterType ? "&material_type=" + encodeURIComponent(filterType) : ""}`;
        const data = await callApi(query);

        const rankedRows = data.top_ranked || data.ranked_materials || [];
        renderMaterialCard("datasetBestCard", data.best_material, "Best Dataset Material");
        renderTopComparison(data.top_3_comparison);
        renderTopTable("datasetTopBody", rankedRows);
    } catch (error) {
        renderEmptyCard(
            "datasetBestCard",
            "bi bi-exclamation-circle",
            "Dataset recommendation failed",
            error.message
        );
        renderTopComparison(null);
        renderTopTable("datasetTopBody", []);
    }
}

async function customRecommendation(event) {
    event.preventDefault();

    const payload = {
        top_n: Number(byId("topN").value) || null,
        material_type: byId("filterMaterialType").value || null,
        materials: [
            {
                material_name: byId("materialName").value.trim(),
                material_type: byId("materialType").value,
                strength_rating: Number(byId("strengthRating").value),
                weight_capacity: Number(byId("weightCapacity").value),
                biodegradability_score: Number(byId("biodegradabilityScore").value),
                recyclability_percentage: Number(byId("recyclabilityPercentage").value)
            }
        ]
    };

    renderLoading("customBestCard", "Scoring custom material...");

    try {
        const data = await callApi("/recommend", {
            method: "POST",
            body: JSON.stringify(payload)
        });

        renderMaterialCard("customBestCard", data.best_material, "Best Custom Material");
    } catch (error) {
        renderEmptyCard(
            "customBestCard",
            "bi bi-x-octagon",
            "Custom recommendation failed",
            error.message
        );
    }
}

function exportCsv() {
    if (!latestTopRanked.length) {
        alert("No data to export");
        return;
    }

    const csvRows = [
        [
            "#",
            "Material Name",
            "Type",
            "Eco Score",
            "Final Ranking Score",
            "Predicted Cost",
            "Predicted CO2",
            "Durability Score",
            "Biodegradability Score",
            "Recyclability Percentage"
        ],
        ...latestTopRanked.map((row, index) => [
            index + 1,
            row.material_name,
            row.material_type,
            row.eco_score,
            row.final_ranking_score ?? row.eco_score,
            row.predicted_cost,
            row.predicted_co2,
            row.durability_score,
            row.biodegradability_score,
            row.recyclability_percentage
        ])
    ];

    const csvContent = csvRows
        .map((row) =>
            row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")
        )
        .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "EcoPackAI_Top_Materials.csv";
    link.click();

    URL.revokeObjectURL(url);
}

async function initBaseUrl() {
    const input = byId("apiBaseUrl");

    if (input.value) return;

    const origin = window.location.origin;

    if (!origin || origin === "null") {
        input.value = "http://127.0.0.1:5000";
        return;
    }

    try {
        const response = await fetch(`${origin}/health`, { method: "GET" });
        if (response.ok) {
            input.value = origin;
            return;
        }
    } catch (error) {
        // ignore
    }

    input.value = origin;
}

function attachEvents() {
    byId("healthBtn").addEventListener("click", checkHealth);
    byId("datasetRecommendBtn").addEventListener("click", datasetRecommendation);
    byId("heroRecommendBtn").addEventListener("click", datasetRecommendation);
    byId("recommendForm").addEventListener("submit", customRecommendation);

    byId("apiBaseUrl").addEventListener("change", async () => {
        await loadMaterialTypes();
        await loadFilterMaterialTypes();
        await loadDashboard();
    });

    byId("refreshDashboardBtn").addEventListener("click", loadDashboard);
    byId("exportPdfBtn").addEventListener("click", () => downloadReport("pdf"));
    byId("exportExcelBtn").addEventListener("click", () => downloadReport("excel"));
    byId("downloadCsvBtn").addEventListener("click", exportCsv);
    byId("topN").addEventListener("change", loadDashboard);
    byId("filterMaterialType").addEventListener("change", loadDashboard);
}

async function init() {
    attachEvents();
    await initBaseUrl();
    await loadMaterialTypes();
    await loadFilterMaterialTypes();
    await loadDashboard();
}

init();
