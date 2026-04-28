const reportMonthInput = document.getElementById("reportMonth");
const vehicleForm = document.getElementById("vehicleForm");
const voucherForm = document.getElementById("voucherForm");
const vehiclesTableBody = document.getElementById("vehiclesTableBody");
const vouchersTableBody = document.getElementById("vouchersTableBody");
const vehicleSelect = document.getElementById("vehicleSelect");
const fuelTypeSelect = document.getElementById("fuelTypeSelect");
const totalVouchers = document.getElementById("totalVouchers");
const totalLiters = document.getElementById("totalLiters");
const totalVehicles = document.getElementById("totalVehicles");
const refreshBtn = document.getElementById("refreshBtn");

let vehicles = [];

function currentMonthValue() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

async function api(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!response.ok) {
        let detail = "Error de servidor";
        try {
            const body = await response.json();
            detail = body.detail || detail;
        } catch (err) {
            detail = "No se pudo procesar la respuesta";
        }
        throw new Error(detail);
    }
    return response.json();
}

function setVehicleRows(items) {
    vehiclesTableBody.innerHTML = "";
    vehicleSelect.innerHTML = '<option value="">Seleccionar vehiculo</option>';

    items.forEach((vehicle) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${vehicle.code}</td>
            <td>${vehicle.plate}</td>
            <td>${vehicle.brand} ${vehicle.model}</td>
            <td>${vehicle.fuel_type}</td>
        `;
        vehiclesTableBody.appendChild(tr);

        if (vehicle.active) {
            const option = document.createElement("option");
            option.value = String(vehicle.id);
            option.textContent = `${vehicle.code} - ${vehicle.plate}`;
            option.dataset.fuelType = vehicle.fuel_type;
            vehicleSelect.appendChild(option);
        }
    });

    totalVehicles.textContent = String(items.length);
}

function setVoucherRows(items) {
    vouchersTableBody.innerHTML = "";
    items.forEach((voucher) => {
        const vehicle = vehicles.find((v) => v.id === voucher.vehicle_id);
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${voucher.serial_number}</td>
            <td>${voucher.issue_date}</td>
            <td>${voucher.employee_name}</td>
            <td>${voucher.area}</td>
            <td>${voucher.liters.toFixed(2)} L</td>
            <td>${voucher.fuel_type}</td>
            <td>${vehicle ? `${vehicle.code} / ${vehicle.plate}` : voucher.vehicle_id}</td>
            <td><a class="link-btn" href="/print/${voucher.id}" target="_blank">Imprimir x2</a></td>
        `;
        vouchersTableBody.appendChild(tr);
    });
}

async function loadVehicles() {
    vehicles = await api("/api/vehicles");
    setVehicleRows(vehicles);
}

async function loadReport() {
    const month = reportMonthInput.value;
    const report = await api(`/api/reports/monthly?month=${month}`);
    totalVouchers.textContent = String(report.total_vouchers);
    totalLiters.textContent = `${Number(report.total_liters).toFixed(2)} L`;
    setVoucherRows(report.vouchers);
}

vehicleSelect.addEventListener("change", () => {
    const selected = vehicleSelect.options[vehicleSelect.selectedIndex];
    if (selected && selected.dataset.fuelType) {
        fuelTypeSelect.value = selected.dataset.fuelType;
    }
});

vehicleForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = Object.fromEntries(new FormData(vehicleForm).entries());
    try {
        await api("/api/vehicles", {
            method: "POST",
            body: JSON.stringify(formData),
        });
        vehicleForm.reset();
        await loadVehicles();
    } catch (error) {
        alert(error.message);
    }
});

voucherForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(voucherForm).entries());
    payload.vehicle_id = Number(payload.vehicle_id);
    payload.liters = Number(payload.liters);

    try {
        const created = await api("/api/vouchers", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        voucherForm.reset();
        voucherForm.issue_date.value = new Date().toISOString().split("T")[0];
        await loadReport();
        window.open(`/print/${created.id}`, "_blank");
    } catch (error) {
        alert(error.message);
    }
});

refreshBtn.addEventListener("click", async () => {
    try {
        await loadReport();
    } catch (error) {
        alert(error.message);
    }
});

(async function init() {
    reportMonthInput.value = currentMonthValue();
    voucherForm.issue_date.value = new Date().toISOString().split("T")[0];
    try {
        await loadVehicles();
        await loadReport();
    } catch (error) {
        alert(error.message);
    }
})();
