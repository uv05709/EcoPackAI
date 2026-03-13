const byId = (id) => document.getElementById(id);

function getBaseUrl() {
    return byId("apiBaseUrl").value.trim().replace(/\/$/, "");
}

function formatNumber(value, digits = 2) {
    return Number(value).toFixed(digits);
}

function renderMaterialCard(containerId, material, title = "Recommended Material") {
    const target = byId(containerId);
    if (!material) {
        target.innerHTML = `<p class="muted">No material available.</p>`;
        return;
    }

    target.innerHTML = `
        <h4>${title}: ${material.material_name}</h4>
        <p><strong>Type:</strong> ${material.material_type}</p>
        <div class="metrics">
            <div class="metric">
                <span class="metric-label">Eco Score</span>
                <span class="metric-value">${formatNumber(material.eco_score, 3)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Predicted Cost</span>
                <span class="metric-value">${formatNumber(material.predicted_cost, 2)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Predicted CO2</span>
                <span class="metric-value">${formatNumber(material.predicted_co2, 2)}</span>
            </div>
        </div>
    `;
}

function renderTopTable(bodyId, rows) {
    const body = byId(bodyId);
    if (!rows || rows.length === 0) {
        body.innerHTML = `<tr><td colspan="6" class="empty">No ranked materials.</td></tr>`;
        return;
    }

    body.innerHTML = rows
        .map(
            (row, index) => `
            <tr>
                <td>${index + 1}</td>
                <td>${row.material_name}</td>
                <td>${row.material_type}</td>
                <td>${formatNumber(row.eco_score, 3)}</td>
                <td>${formatNumber(row.predicted_cost, 2)}</td>
                <td>${formatNumber(row.predicted_co2, 2)}</td>
            </tr>`
        )
        .join("");
}

async function callApi(path, options = {}) {
    const response = await fetch(`${getBaseUrl()}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.error || data.message || `Request failed (${response.status})`);
    }
    return data;
}

function setStatus(message, ok = false) {
    const status = byId("healthStatus");
    status.textContent = message;
    status.style.color = ok ? "#1d6a45" : "#8d2b2b";
}

async function loadMaterialTypes() {
    try {
        const data = await callApi("/metadata/material-types");
        const select = byId("materialType");
        select.innerHTML = "";
        data.material_types.forEach((type) => {
            const option = document.createElement("option");
            option.value = type;
            option.textContent = type;
            select.appendChild(option);
        });
        setStatus(`Status: connected (${data.count} material types loaded)`, true);
    } catch (error) {
        setStatus(`Status: failed to load material types (${error.message})`, false);
    }
}

async function checkHealth() {
    try {
        const health = await callApi("/health");
        setStatus(`Status: backend healthy, dataset rows: ${health.dataset_rows}`, true);
    } catch (error) {
        setStatus(`Status: backend unhealthy (${error.message})`, false);
    }
}

async function datasetRecommendation() {
    try {
        const data = await callApi("/recommend");
        renderMaterialCard("datasetBestCard", data.best_material, "Best Dataset Material");
        renderTopTable("datasetTopBody", data.top_5 || []);
    } catch (error) {
        byId("datasetBestCard").innerHTML = `<p class="muted">Dataset recommendation failed: ${error.message}</p>`;
        renderTopTable("datasetTopBody", []);
    }
}

async function customRecommendation(event) {
    event.preventDefault();

    const payload = {
        materials: [
            {
                material_name: byId("materialName").value.trim(),
                material_type: byId("materialType").value,
                strength_rating: Number(byId("strengthRating").value),
                weight_capacity: Number(byId("weightCapacity").value),
                biodegradability_score: Number(byId("biodegradabilityScore").value),
                recyclability_percentage: Number(byId("recyclabilityPercentage").value),
            },
        ],
    };

    try {
        const data = await callApi("/recommend", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        renderMaterialCard("customBestCard", data.best_material, "Best Custom Material");
    } catch (error) {
        byId("customBestCard").innerHTML = `<p class="muted">Custom recommendation failed: ${error.message}</p>`;
    }
}

byId("healthBtn").addEventListener("click", checkHealth);
byId("datasetRecommendBtn").addEventListener("click", datasetRecommendation);
byId("recommendForm").addEventListener("submit", customRecommendation);
byId("apiBaseUrl").addEventListener("change", loadMaterialTypes);

loadMaterialTypes();
