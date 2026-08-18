const reportMonthInput = document.getElementById("reportMonth");
const invoiceMonthInput = document.getElementById("invoiceMonth");
const vehicleForm = document.getElementById("vehicleForm");
const voucherForm = document.getElementById("voucherForm");
const invoiceForm = document.getElementById("invoiceForm");
const invoiceSubmitBtn = document.getElementById("invoiceSubmitBtn");
const invoiceCancelEditBtn = document.getElementById("invoiceCancelEditBtn");
const vehiclesTableBody = document.getElementById("vehiclesTableBody");
const vouchersTableBody = document.getElementById("vouchersTableBody");
const invoicesTableBody = document.getElementById("invoicesTableBody");
const vehicleSelect = document.getElementById("vehicleSelect");
const fuelTypeSelect = document.getElementById("fuelTypeSelect");
const totalVouchers = document.getElementById("totalVouchers");
const invoiceLiters = document.getElementById("invoiceLiters");
const totalVehicles = document.getElementById("totalVehicles");
const invoiceSummary = document.getElementById("invoiceSummary");
const refreshBtn = document.getElementById("refreshBtn");
const exportBtn = document.getElementById("exportBtn");
const voucherSearchInput = document.getElementById("voucherSearchInput");
const reportPrevPageBtn = document.getElementById("reportPrevPageBtn");
const reportNextPageBtn = document.getElementById("reportNextPageBtn");
const reportPageInfo = document.getElementById("reportPageInfo");
const invoicePrevPageBtn = document.getElementById("invoicePrevPageBtn");
const invoiceNextPageBtn = document.getElementById("invoiceNextPageBtn");
const invoicePageInfo = document.getElementById("invoicePageInfo");
const stationSummary = document.getElementById("stationSummary");
const stationChart = document.getElementById("stationChart");
const stationsTableBody = document.getElementById("stationsTableBody");

let vehicles = [];
let editingInvoiceId = null;
let reportPage = 1;
let reportTotalPages = 1;
let reportSearch = "";
const REPORT_PAGE_SIZE = 10;
let invoicePage = 1;
let invoiceTotalPages = 1;
const INVOICE_PAGE_SIZE = 10;
let currentInvoiceItems = [];

function setStationRows(report) {
    stationsTableBody.innerHTML = "";
    stationChart.innerHTML = "";

    if (!report.stations.length) {
        stationSummary.textContent = "Sin datos para el mes seleccionado.";
        stationChart.innerHTML = '<div class="station-empty">No hay cargas registradas para este mes.</div>';
        stationsTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:24px;color:#64748b;">No hay estaciones con vales en este mes.</td></tr>';
        return;
    }

    const stationCount = report.stations.length;
    stationSummary.textContent = `Estaciones: ${stationCount} | Vales: ${report.total_vouchers} | Litros: ${Number(report.total_liters).toFixed(2)} L`;

    report.stations.forEach((station) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${station.station}</td>
            <td>${station.total_vouchers}</td>
            <td>${Number(station.total_liters).toFixed(2)} L</td>
            <td>${Number(station.avg_liters_per_voucher).toFixed(2)} L</td>
            <td>${Number(station.share_percent).toFixed(2)}%</td>
        `;
        stationsTableBody.appendChild(tr);

        const row = document.createElement("div");
        row.className = "station-bar-row";
        row.innerHTML = `
            <div class="station-bar-label" title="${station.station}">${station.station}</div>
            <div class="station-bar-track">
                <div class="station-bar-fill" style="width:${Math.max(2, Number(station.share_percent))}%"></div>
            </div>
            <div class="station-bar-value">${Number(station.share_percent).toFixed(2)}%</div>
        `;
        stationChart.appendChild(row);
    });
}

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
    if (response.status === 204) return null;
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
            <td style="text-align:center"><button type="button" class="table-action danger icon-btn" data-action="delete-vehicle" data-id="${vehicle.id}" title="Eliminar" style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg></button></td>
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
    if (!items.length) {
        vouchersTableBody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:24px;color:#64748b;">No hay vales para este mes.</td></tr>';
        return;
    }

    items.forEach((voucher) => {
        const vehicle = vehicles.find((v) => v.id === voucher.vehicle_id);
        const quantityLabel = voucher.liters && voucher.liters > 0
            ? `${voucher.liters.toFixed(2)} L`
            : "A completar en estacion";
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${voucher.serial_number}</td>
            <td>${voucher.issue_date}</td>
            <td>${voucher.employee_name}</td>
            <td>${voucher.area}</td>
            <td>${quantityLabel}</td>
            <td>${voucher.fuel_type}</td>
            <td>${vehicle ? `${vehicle.code} / ${vehicle.plate}` : voucher.vehicle_id}</td>
            <td style="text-align:center">
                <button type="button" class="table-action icon-btn" data-action="print-station" data-id="${voucher.id}" title="Imprimir copia estacion" style="margin:0;background:#15803d;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg></button>
                <button type="button" class="table-action icon-btn" data-action="print-internal" data-id="${voucher.id}" title="Imprimir control interno" style="margin:0;background:#334155;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg></button>
                <button type="button" class="table-action icon-btn" data-action="download-internal" data-id="${voucher.id}" title="Descargar PDF control interno" style="margin:0;background:#1d4ed8;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></button>
                <button type="button" class="table-action danger icon-btn" data-action="delete-voucher" data-id="${voucher.id}" title="Eliminar" style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg></button>
            </td>
        `;
        vouchersTableBody.appendChild(tr);
    });
}

function setInvoiceRows(summary) {
    invoicesTableBody.innerHTML = "";
    currentInvoiceItems = summary.invoices;
    invoicePage = summary.page;
    invoiceTotalPages = summary.total_pages;

    summary.invoices.forEach((invoice) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${invoice.month}</td>
            <td>${invoice.station}</td>
            <td>${invoice.invoice_number}</td>
            <td>${invoice.total_vouchers}</td>
            <td>${Number(invoice.total_liters).toFixed(2)} L</td>
            <td>${Number(invoice.total_amount).toFixed(2)}</td>
            <td>
                <button type="button" class="table-action" data-action="edit" data-id="${invoice.id}">Editar</button>
                <button type="button" class="table-action danger" data-action="delete" data-id="${invoice.id}">Eliminar</button>
            </td>
        `;
        invoicesTableBody.appendChild(tr);
    });

    invoiceSummary.textContent = `Facturas: ${summary.total_invoices} | Vales facturados: ${summary.total_vouchers} | Litros facturados: ${Number(summary.total_liters).toFixed(2)} L | Monto: ${Number(summary.total_amount).toFixed(2)}`;
    invoiceLiters.textContent = `${Number(summary.total_liters).toFixed(2)} L`;
    invoicePageInfo.textContent = `Pagina ${invoicePage} de ${invoiceTotalPages}`;
    invoicePrevPageBtn.disabled = !summary.has_prev;
    invoiceNextPageBtn.disabled = !summary.has_next;
}

function resetInvoiceForm() {
    editingInvoiceId = null;
    invoiceForm.reset();
    invoiceMonthInput.value = reportMonthInput.value;
    invoiceSubmitBtn.textContent = "Guardar factura mensual";
    invoiceCancelEditBtn.style.display = "none";
}

function showToast(message, tone = "info") {
    const existing = document.getElementById("appToast");
    if (existing) {
        existing.remove();
    }

    const toast = document.createElement("div");
    toast.id = "appToast";
    toast.textContent = message;
    toast.style.position = "fixed";
    toast.style.right = "16px";
    toast.style.bottom = "16px";
    toast.style.zIndex = "9999";
    toast.style.padding = "12px 14px";
    toast.style.borderRadius = "999px";
    toast.style.color = "#fff";
    toast.style.fontWeight = "700";
    toast.style.boxShadow = "0 10px 24px rgba(0,0,0,0.2)";
    toast.style.background = tone === "success" ? "#15803d" : tone === "danger" ? "#b91c1c" : "#334155";
    document.body.appendChild(toast);
    window.setTimeout(() => toast.remove(), 2600);
}

function populateInvoiceForm(invoice) {
    editingInvoiceId = invoice.id;
    invoiceForm.month.value = invoice.month;
    invoiceForm.station.value = invoice.station;
    invoiceForm.invoice_number.value = invoice.invoice_number;
    invoiceForm.total_vouchers.value = invoice.total_vouchers;
    invoiceForm.total_liters.value = invoice.total_liters;
    invoiceForm.total_amount.value = invoice.total_amount;
    invoiceForm.notes.value = invoice.notes || "";
    invoiceSubmitBtn.textContent = "Actualizar factura mensual";
    invoiceCancelEditBtn.style.display = "block";
}

async function loadVehicles() {
    vehicles = await api("/api/vehicles");
    setVehicleRows(vehicles);
}

async function loadReport() {
    const month = reportMonthInput.value;
    const query = new URLSearchParams({
        month,
        page: String(reportPage),
        page_size: String(REPORT_PAGE_SIZE),
    });
    if (reportSearch) {
        query.set("search", reportSearch);
    }
    const report = await api(`/api/reports/monthly?${query.toString()}`);
    reportPage = report.page;
    reportTotalPages = report.total_pages;
    totalVouchers.textContent = String(report.total_vouchers);
    setVoucherRows(report.vouchers);
    reportPageInfo.textContent = `Pagina ${reportPage} de ${reportTotalPages}`;
    reportPrevPageBtn.disabled = !report.has_prev;
    reportNextPageBtn.disabled = !report.has_next;
}

async function loadInvoices() {
    const month = reportMonthInput.value;
    const summary = await api(`/api/monthly-invoices?month=${month}&page=${invoicePage}&page_size=${INVOICE_PAGE_SIZE}`);
    setInvoiceRows(summary);
}

async function loadStationBreakdown() {
    const month = reportMonthInput.value;
    const report = await api(`/api/reports/stations?month=${month}`);
    setStationRows(report);
}

const litersInput = document.getElementById("litersInput");
const litersCompletarCheck = document.getElementById("litersCompletarCheck");

litersCompletarCheck.addEventListener("change", () => {
    if (litersCompletarCheck.checked) {
        litersInput.value = "";
        litersInput.disabled = true;
        litersInput.placeholder = "A completar en estacion";
    } else {
        litersInput.disabled = false;
        litersInput.placeholder = "Cantidad de litros";
    }
});

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
        showToast("Vehiculo guardado", "success");
    } catch (error) {
        alert(error.message);
    }
});

voucherForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(voucherForm).entries());
    payload.vehicle_id = Number(payload.vehicle_id);
    if (litersCompletarCheck.checked || !payload.liters) {
        payload.liters = 0;
    } else {
        payload.liters = Number(payload.liters);
    }

    try {
        const created = await api("/api/vouchers", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        voucherForm.reset();
        litersCompletarCheck.checked = false;
        litersInput.disabled = false;
        litersInput.placeholder = "Cantidad de litros";
        voucherForm.issue_date.value = new Date().toISOString().split("T")[0];
        reportPage = 1;
        await loadReport();
        showToast("Vale emitido correctamente", "success");
        window.open(`/print/${created.id}`, "_blank");
    } catch (error) {
        alert(error.message);
    }
});

invoiceForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(invoiceForm).entries());
    payload.total_vouchers = Number(payload.total_vouchers);
    payload.total_liters = Number(payload.total_liters);
    payload.total_amount = Number(payload.total_amount);

    try {
        const isEditing = Boolean(editingInvoiceId);
        await api(editingInvoiceId ? `/api/monthly-invoices/${editingInvoiceId}` : "/api/monthly-invoices", {
            method: editingInvoiceId ? "PUT" : "POST",
            body: JSON.stringify(payload),
        });
        if (!isEditing) {
            invoicePage = 1;
        }
        resetInvoiceForm();
        await loadInvoices();
        showToast("Factura mensual guardada", "success");
    } catch (error) {
        alert(error.message);
    }
});

invoiceCancelEditBtn.addEventListener("click", () => {
    resetInvoiceForm();
});

vehiclesTableBody.addEventListener("click", async (event) => {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const action = target.dataset.action;
    const id = Number(target.dataset.id);
    if (action !== "delete-vehicle" || !id) return;
    const confirmed = window.confirm("Se eliminara el vehiculo seleccionado. Continuar?");
    if (!confirmed) return;
    try {
        await api(`/api/vehicles/${id}`, { method: "DELETE" });
        await loadVehicles();
    } catch (error) {
        alert(error.message);
    }
});

vouchersTableBody.addEventListener("click", async (event) => {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const action = target.dataset.action;
    const id = Number(target.dataset.id);
    if (!id) return;

    if (action === "print-station") {
        window.open(`/print/${id}`, "_blank");
        return;
    }

    if (action === "print-internal") {
        window.open(`/print/${id}?mode=internal`, "_blank");
        return;
    }

    if (action === "download-internal") {
        window.open(`/print/${id}?mode=internal&format=pdf&download=true`, "_blank");
        return;
    }

    if (action !== "delete-voucher") return;
    const confirmed = window.confirm("Se eliminara el vale seleccionado. Continuar?");
    if (!confirmed) return;
    try {
        await api(`/api/vouchers/${id}`, { method: "DELETE" });
        await loadReport();
        if (reportPage > reportTotalPages) {
            reportPage = reportTotalPages;
            await loadReport();
        }
        showToast("Vale eliminado", "danger");
    } catch (error) {
        alert(error.message);
    }
});

invoicesTableBody.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
        return;
    }

    const action = target.dataset.action;
    const id = Number(target.dataset.id);
    if (!action || !id) {
        return;
    }

    if (action === "edit") {
        const invoice = currentInvoiceItems.find((item) => item.id === id);
        if (!invoice) {
            alert("No se encontro la factura seleccionada");
            return;
        }
        populateInvoiceForm(invoice);
    }

    if (action === "delete") {
        const confirmed = window.confirm("Se eliminara la factura mensual seleccionada. Continuar?");
        if (!confirmed) {
            return;
        }
        try {
            await api(`/api/monthly-invoices/${id}`, { method: "DELETE" });
            if (editingInvoiceId === id) {
                resetInvoiceForm();
            }
            await loadInvoices();
            if (invoicePage > invoiceTotalPages) {
                invoicePage = invoiceTotalPages;
                await loadInvoices();
            }
            showToast("Factura eliminada", "danger");
        } catch (error) {
            alert(error.message);
        }
    }
});

reportMonthInput.addEventListener("change", async () => {
    if (!editingInvoiceId) {
        invoiceMonthInput.value = reportMonthInput.value;
    }
    reportPage = 1;
    invoicePage = 1;
    try {
        await loadReport();
        await loadInvoices();
        await loadStationBreakdown();
    } catch (error) {
        alert(error.message);
    }
});

refreshBtn.addEventListener("click", async () => {
    try {
        await loadReport();
        await loadInvoices();
        await loadStationBreakdown();
    } catch (error) {
        alert(error.message);
    }
});

voucherSearchInput.addEventListener("input", async (event) => {
    reportSearch = event.target.value.trim();
    reportPage = 1;
    try {
        await loadReport();
    } catch (error) {
        alert(error.message);
    }
});

exportBtn.addEventListener("click", async () => {
    try {
        const month = reportMonthInput.value;
        const query = new URLSearchParams({ month, page: "1", page_size: "1000" });
        if (reportSearch) {
            query.set("search", reportSearch);
        }
        const report = await api(`/api/reports/monthly?${query.toString()}`);
        const rows = report.vouchers.map((voucher) => ({
            serial_number: voucher.serial_number,
            issue_date: voucher.issue_date,
            employee_name: voucher.employee_name,
            area: voucher.area,
            vehicle_id: voucher.vehicle_id,
            fuel_type: voucher.fuel_type,
            liters: voucher.liters,
            station: voucher.station,
            notes: voucher.notes || "",
        }));
        const filename = `vales_${month}${reportSearch ? `_${reportSearch.replace(/\s+/g, "_")}` : ""}.xlsx`;
        const blob = await fetch("/api/export/vouchers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ month, search: reportSearch, filename }),
        }).then((response) => {
            if (!response.ok) {
                throw new Error("No se pudo generar el Excel");
            }
            return response.blob();
        });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        link.click();
        window.URL.revokeObjectURL(url);
        showToast("Excel descargado", "success");
    } catch (error) {
        alert(error.message);
    }
});

reportPrevPageBtn.addEventListener("click", async () => {
    if (reportPage <= 1) return;
    reportPage -= 1;
    try {
        await loadReport();
    } catch (error) {
        alert(error.message);
    }
});

reportNextPageBtn.addEventListener("click", async () => {
    if (reportPage >= reportTotalPages) return;
    reportPage += 1;
    try {
        await loadReport();
    } catch (error) {
        alert(error.message);
    }
});

invoicePrevPageBtn.addEventListener("click", async () => {
    if (invoicePage <= 1) return;
    invoicePage -= 1;
    try {
        await loadInvoices();
    } catch (error) {
        alert(error.message);
    }
});

invoiceNextPageBtn.addEventListener("click", async () => {
    if (invoicePage >= invoiceTotalPages) return;
    invoicePage += 1;
    try {
        await loadInvoices();
    } catch (error) {
        alert(error.message);
    }
});

(async function init() {
    reportMonthInput.value = currentMonthValue();
    resetInvoiceForm();
    voucherForm.issue_date.value = new Date().toISOString().split("T")[0];
    try {
        await loadVehicles();
        await loadReport();
        await loadInvoices();
        await loadStationBreakdown();
    } catch (error) {
        alert(error.message);
    }
})();
