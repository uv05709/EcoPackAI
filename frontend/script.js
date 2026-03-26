const byId = id => document.getElementById(id);
let latestTopRanked = [];

function getBaseUrl() { return byId("apiBaseUrl").value.trim().replace(/\/$/, ""); }
function formatNumber(value, digits = 2) { return Number(value).toFixed(digits); }

function renderMaterialCard(containerId, material, title = "Recommended Material") {
    const target = byId(containerId);
    if (!material) { target.innerHTML = `<p class="muted">No material available.</p>`; return; }
    target.innerHTML = `
        <h4>${title}: ${material.material_name}</h4>
        <p><strong>Type:</strong> ${material.material_type}</p>
        <div class="metrics">
            <div class="metric"><span class="metric-label">Eco Score</span><span class="metric-value">${formatNumber(material.eco_score,3)}</span></div>
            <div class="metric"><span class="metric-label">Predicted Cost</span><span class="metric-value">${formatNumber(material.predicted_cost,2)}</span></div>
            <div class="metric"><span class="metric-label">Predicted CO2</span><span class="metric-value">${formatNumber(material.predicted_co2,2)}</span></div>
        </div>
    `;
}

function renderTopTable(bodyId, rows) {
    latestTopRanked = rows || [];
    const body = byId(bodyId);
    if (!rows || rows.length === 0) { body.innerHTML = `<tr><td colspan="6" class="empty">No ranked materials.</td></tr>`; return; }

    body.innerHTML = rows.map((row,index)=>`
        <tr>
            <td>${index+1}</td>
            <td>${row.material_name}</td>
            <td>${row.material_type}</td>
            <td>${formatNumber(row.eco_score,3)}</td>
            <td>${formatNumber(row.predicted_cost,2)}</td>
            <td>${formatNumber(row.predicted_co2,2)}</td>
        </tr>`).join("");
}

async function callApi(path, options={}) {
    const response = await fetch(`${getBaseUrl()}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
    const data = await response.json().catch(()=>({}));
    if(!response.ok) throw new Error(data.error || data.message || `Request failed (${response.status})`);
    return data;
}

function setStatus(message, ok=false) {
    const status = byId("healthStatus");
    status.textContent = message;
    status.style.color = ok ? "#1d6a45" : "#8d2b2b";
}

function showLoading(containerId) { byId(containerId).innerHTML = '<div class="spinner"></div>'; }

function setDashboardStatus(message, ok=false) {
    const status = byId("dashboardStatus");
    status.textContent = message;
    status.style.color = ok ? "#1d6a45" : "#8d2b2b";
}

function renderChart(targetId, data, layout) {
    const target = byId(targetId);
    if (!window.Plotly) {
        target.innerHTML = "<p class=\"muted\">Plotly not loaded.</p>";
        return;
    }
    Plotly.react(target, data, layout, { displayModeBar: false, responsive: true });
}

function renderDashboard(summary) {
    byId("kpiCo2Reduction").textContent = `${summary.savings.co2_reduction_pct}%`;
    byId("kpiCostSavings").textContent = `${summary.savings.cost_savings_pct}%`;
    byId("kpiEcoScore").textContent = summary.top_summary.avg_eco_score;

    const labels = summary.usage_trends.labels;
    const usageData = [{
        x: labels,
        y: summary.usage_trends.counts,
        type: "bar",
        marker: { color: "#6aa27a" }
    }];
    const costData = [{
        x: labels,
        y: summary.usage_trends.avg_cost,
        type: "bar",
        marker: { color: "#a5612a" }
    }];
    const co2Data = [{
        x: labels,
        y: summary.usage_trends.avg_co2,
        type: "bar",
        marker: { color: "#3a6b55" }
    }];

    const baseLayout = {
        margin: { t: 20, l: 40, r: 10, b: 60 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        xaxis: { tickangle: -30, automargin: true },
        yaxis: { gridcolor: "#e3efe3" }
    };

    renderChart("usageChart", usageData, { ...baseLayout, yaxis: { ...baseLayout.yaxis, title: "Count" } });
    renderChart("costChart", costData, { ...baseLayout, yaxis: { ...baseLayout.yaxis, title: "Avg Cost" } });
    renderChart("co2Chart", co2Data, { ...baseLayout, yaxis: { ...baseLayout.yaxis, title: "Avg CO2" } });
}

async function loadDashboard() {
    setDashboardStatus("Dashboard: loading...", true);
    const top_n = Number(byId("topN").value) || 5;
    const filter_type = byId("filterMaterialType").value || null;
    const query = `/analytics/summary?top_n=${top_n}${filter_type ? "&material_type=" + encodeURIComponent(filter_type) : ""}`;
    try {
        const summary = await callApi(query);
        renderDashboard(summary);
        setDashboardStatus(`Dashboard: updated (Top ${summary.top_summary.top_n})`, true);
    } catch (error) {
        setDashboardStatus(`Dashboard: failed (${error.message})`, false);
    }
}

function downloadReport(format) {
    const top_n = Number(byId("topN").value) || 5;
    const filter_type = byId("filterMaterialType").value || null;
    const query = `/reports/sustainability?format=${format}&top_n=${top_n}${filter_type ? "&material_type=" + encodeURIComponent(filter_type) : ""}`;
    const link = document.createElement("a");
    link.href = `${getBaseUrl()}${query}`;
    link.target = "_blank";
    link.click();
}

async function loadMaterialTypes() {
    try {
        const data = await callApi("/metadata/material-types");
        const select = byId("materialType");
        select.innerHTML = "";
        data.material_types.forEach(type=>{
            const option = document.createElement("option");
            option.value = type;
            option.textContent = type;
            select.appendChild(option);
        });
        setStatus(`Status: connected (${data.count} material types loaded)`, true);
    } catch(error) {
        setStatus(`Status: failed to load material types (${error.message})`, false);
    }
}

async function loadFilterMaterialTypes() {
    try {
        const data = await callApi("/metadata/material-types");
        const select = byId("filterMaterialType");
        select.innerHTML = '<option value="">All Types</option>';
        data.material_types.forEach(type=>{
            const option = document.createElement("option");
            option.value = type;
            option.textContent = type;
            select.appendChild(option);
        });
    } catch(err) { console.warn("Failed to load filter types",err); }
}

async function checkHealth() {
    try {
        const health = await callApi("/health");
        setStatus(`Status: backend healthy, dataset rows: ${health.dataset_rows}`, true);
    } catch(error) { setStatus(`Status: backend unhealthy (${error.message})`, false); }
}

async function datasetRecommendation() {
    showLoading("datasetBestCard");
    renderTopTable("datasetTopBody", []);
    try {
        const top_n = Number(byId("topN").value) || 5;
        const filter_type = byId("filterMaterialType").value || null;
        const query = `/recommend?top_n=${top_n}${filter_type ? "&material_type=" + filter_type : ""}`;
        const data = await callApi(query);
        renderMaterialCard("datasetBestCard", data.best_material, "Best Dataset Material");
        renderTopTable("datasetTopBody", data.top_ranked || []);
    } catch(error) {
        byId("datasetBestCard").innerHTML = `<p class="muted">Dataset recommendation failed: ${error.message}</p>`;
        renderTopTable("datasetTopBody", []);
    }
}

async function customRecommendation(event) {
    event.preventDefault();
    const payload = {
        top_n: Number(byId("topN").value) || null,
        filter_type: byId("filterMaterialType").value || null,
        materials:[{
            material_name: byId("materialName").value.trim(),
            material_type: byId("materialType").value,
            strength_rating: Number(byId("strengthRating").value),
            weight_capacity: Number(byId("weightCapacity").value),
            biodegradability_score: Number(byId("biodegradabilityScore").value),
            recyclability_percentage: Number(byId("recyclabilityPercentage").value),
        }]
    };
    showLoading("customBestCard");
    try {
        const data = await callApi("/recommend",{ method:"POST", body:JSON.stringify(payload) });
        renderMaterialCard("customBestCard", data.best_material, "Best Custom Material");
    } catch(error) {
        byId("customBestCard").innerHTML = `<p class="muted">Custom recommendation failed: ${error.message}</p>`;
    }
}

byId("healthBtn").addEventListener("click", checkHealth);
byId("datasetRecommendBtn").addEventListener("click", datasetRecommendation);
byId("recommendForm").addEventListener("submit", customRecommendation);
byId("apiBaseUrl").addEventListener("change", loadMaterialTypes);
byId("refreshDashboardBtn").addEventListener("click", loadDashboard);
byId("exportPdfBtn").addEventListener("click", ()=>downloadReport("pdf"));
byId("exportExcelBtn").addEventListener("click", ()=>downloadReport("excel"));
byId("downloadCsvBtn").addEventListener("click", ()=>{
    if(!latestTopRanked.length) return alert("No data to export");
    const csvContent = [["#", "Material Name","Type","Eco Score","Predicted Cost","Predicted CO2"], ...latestTopRanked.map((row,i)=>[i+1,row.material_name,row.material_type,row.eco_score,row.predicted_cost,row.predicted_co2])]
        .map(e=>e.join(",")).join("\n");
    const blob = new Blob([csvContent],{type:"text/csv"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "top_materials.csv";
    a.click();
    URL.revokeObjectURL(url);
});

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
    } catch (err) {
        // ignore and fall back
    }

    input.value = "http://127.0.0.1:5000";
}

initBaseUrl().then(()=>{
    loadMaterialTypes();
    loadFilterMaterialTypes();
    loadDashboard();
});
