// Validación de formulario con Bootstrap
(function () {
    'use strict';
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();

// Restricción de fechas
document.addEventListener('DOMContentLoaded', () => {
    const fechaVencimientoInput = document.getElementById("fecha_vencimiento");
    const fechaCorteInput = document.getElementById("fecha_corte");
    const today = new Date();

    const formatDate = (date) => {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${year}-${month}-${day}`;
    };

    fechaVencimientoInput.min = formatDate(today);
    fechaVencimientoInput.addEventListener('change', () => {
        const fechaSeleccionada = new Date(fechaVencimientoInput.value);
        if (fechaSeleccionada.getMonth() !== today.getMonth() || fechaSeleccionada.getFullYear() !== today.getFullYear()) {
            fechaVencimientoInput.setCustomValidity("La fecha de vencimiento debe estar dentro del mes actual.");
        } else {
            fechaVencimientoInput.setCustomValidity("");
        }

        const nuevaFechaMinCorte = new Date(fechaSeleccionada);
        nuevaFechaMinCorte.setDate(nuevaFechaMinCorte.getDate() + 1);
        fechaCorteInput.min = formatDate(nuevaFechaMinCorte);
    });

    fechaCorteInput.addEventListener('change', () => {
        const fechaCorte = new Date(fechaCorteInput.value);
        const fechaVencimiento = new Date(fechaVencimientoInput.value);
        if (fechaCorte <= fechaVencimiento) {
            fechaCorteInput.setCustomValidity("La fecha de corte debe ser posterior a la fecha de vencimiento.");
        } else {
            fechaCorteInput.setCustomValidity("");
        }
    });
});

async function generarRecibos(button) {
    const url = button.getAttribute('data-url');
    try {
        const response = await fetch(url);
        if (response.ok) {
            const result = await response.json();

            // Mostrar el mensaje en el modal
            const mensajeModal = document.getElementById("mensajeModal");
            mensajeModal.textContent = `Recibos del mes de "${result.mes}" generados con éxito.`;

            // Mostrar el modal
            const modal = new bootstrap.Modal(document.getElementById("recibosModal"));
            modal.show();

            // Abrir el PDF en una nueva pestaña después de un pequeño retraso
            setTimeout(() => {
                window.open(result.pdf_path, '_blank');
            }, 1000);
        } else {
            alert("Hubo un problema al generar los recibos. Intente nuevamente.");
        }
    } catch (error) {
        console.error("Error al generar los recibos:", error);
        alert("Ocurrió un error al intentar generar los recibos.");
    }
}