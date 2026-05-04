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

let vehicles = [];
let editingInvoiceId = null;

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
            <td style="text-align:center"><button type="button" class="table-action danger icon-btn" onclick="window.open('/print/${voucher.id}','_blank')" title="Imprimir" style="margin:0;background:#15803d;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg></button></td>
        `;
        vouchersTableBody.appendChild(tr);
    });
}

function setInvoiceRows(summary) {
    invoicesTableBody.innerHTML = "";

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
}

function resetInvoiceForm() {
    editingInvoiceId = null;
    invoiceForm.reset();
    invoiceMonthInput.value = reportMonthInput.value;
    invoiceSubmitBtn.textContent = "Guardar factura mensual";
    invoiceCancelEditBtn.style.display = "none";
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
    const report = await api(`/api/reports/monthly?month=${month}`);
    totalVouchers.textContent = String(report.total_vouchers);
    setVoucherRows(report.vouchers);
}

async function loadInvoices() {
    const month = reportMonthInput.value;
    const summary = await api(`/api/monthly-invoices?month=${month}`);
    setInvoiceRows(summary);
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
        await loadReport();
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
        await api(editingInvoiceId ? `/api/monthly-invoices/${editingInvoiceId}` : "/api/monthly-invoices", {
            method: editingInvoiceId ? "PUT" : "POST",
            body: JSON.stringify(payload),
        });
        resetInvoiceForm();
        await loadInvoices();
    } catch (error) {
        alert(error.message);
    }
});

invoiceCancelEditBtn.addEventListener("click", () => {
    resetInvoiceForm();
});

vehiclesTableBody.addEventListener("click", async (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
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
        const month = reportMonthInput.value;
        try {
            const summary = await api(`/api/monthly-invoices?month=${month}`);
            const invoice = summary.invoices.find((item) => item.id === id);
            if (!invoice) {
                alert("No se encontro la factura seleccionada");
                return;
            }
            populateInvoiceForm(invoice);
        } catch (error) {
            alert(error.message);
        }
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
        } catch (error) {
            alert(error.message);
        }
    }
});

reportMonthInput.addEventListener("change", async () => {
    if (!editingInvoiceId) {
        invoiceMonthInput.value = reportMonthInput.value;
    }
    try {
        await loadReport();
        await loadInvoices();
    } catch (error) {
        alert(error.message);
    }
});

refreshBtn.addEventListener("click", async () => {
    try {
        await loadReport();
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
    } catch (error) {
        alert(error.message);
    }
})();
