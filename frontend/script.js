const byId = (id) => document.getElementById(id);

function getBaseUrl() {
    return byId("apiBaseUrl").value.trim().replace(/\/$/, "");
}

function showOutput(id, data) {
    byId(id).textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

async function callApi(path, options = {}) {
    const response = await fetch(`${getBaseUrl()}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.error || data.message || `Request failed (${response.status})`);
    }
    return data;
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
    } catch (error) {
        showOutput("healthOutput", `Could not load material types: ${error.message}`);
    }
}

async function checkHealth() {
    try {
        const data = await callApi("/health");
        showOutput("healthOutput", data);
    } catch (error) {
        showOutput("healthOutput", `Health check failed: ${error.message}`);
    }
}

async function datasetRecommendation() {
    try {
        const data = await callApi("/recommend");
        showOutput("datasetOutput", data);
    } catch (error) {
        showOutput("datasetOutput", `Recommendation failed: ${error.message}`);
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
                cost_efficiency_index: Number(byId("costEfficiencyIndex").value),
                co2_impact_index: Number(byId("co2ImpactIndex").value),
                material_suitability_score: Number(byId("materialSuitabilityScore").value)
            }
        ]
    };

    try {
        const data = await callApi("/recommend", {
            method: "POST",
            body: JSON.stringify(payload)
        });
        showOutput("customOutput", data);
    } catch (error) {
        showOutput("customOutput", `Custom recommendation failed: ${error.message}`);
    }
}

byId("healthBtn").addEventListener("click", checkHealth);
byId("datasetRecommendBtn").addEventListener("click", datasetRecommendation);
byId("recommendForm").addEventListener("submit", customRecommendation);
byId("apiBaseUrl").addEventListener("change", loadMaterialTypes);

loadMaterialTypes();
