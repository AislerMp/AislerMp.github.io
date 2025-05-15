const elements = {
    sorteoSelect: document.getElementById("sorteo"),
    fechaInput: document.getElementById("fecha"),
    reventadoCheckbox: document.getElementById('reventado'),
    boolInput: document.getElementById('hiddenBoolean'),
    numeroInput: document.getElementById('numeroGanador')
};

function confirmacion_numeroGanador(event) {
    event.preventDefault(); // Evitar el envío del formulario por defecto
    if (elements.numeroInput.value === "") {
        alert("No hay números ingresados. Por favor, ingrese al menos un número.");
        event.preventDefault();
    } else {
        const confirmacion = confirm("¿Estás seguro de que quieres confirmar este Numero?\nUna vez procesada no se puede modificar.");
        if (confirmacion) {   
            event.target.closest("form").submit();
        }
    }
}

function validarValores() {
    const numero = parseInt(elements.numeroInput.value);
    if (numero > 99 || numero < 0) elements.numeroInput.value = "";
}

document.addEventListener('DOMContentLoaded', () => {
    elements.reventadoCheckbox.addEventListener('change', () => {
        if (!elements.reventadoCheckbox.checked) elements.boolInput.value = 'False';
        else elements.boolInput.value = 'True';
    });

    const inputFecha = elements.fechaInput;
    const hoy = new Date();

    const año = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0'); // Enero es 0
    const dia = String(hoy.getDate()).padStart(2, '0');
    const fechaLocal = `${año}-${mes}-${dia}`;
    inputFecha.value = fechaLocal;

    const sorteoSelect = document.getElementById("sorteo");
    const horaActual = hoy.toTimeString().split(' ')[0]; // HH:MM:SS

    let selectedIndex = sorteoSelect.selectedIndex;
    let opciones = Array.from(sorteoSelect.options);
    let cambioRealizado = false;

    // Verifica si la hora actual ya pasó el sorteo seleccionado
    const [idActual, horaSorteoActual] = sorteoSelect.value.split(',');

    if (horaActual > horaSorteoActual.trim()) {
        // Buscar el siguiente sorteo que tenga una hora mayor a la actual
        for (let i = selectedIndex + 1; i < opciones.length; i++) {
            const [id, hora] = opciones[i].value.split(',');
            if (horaActual < hora.trim()) {
                sorteoSelect.selectedIndex = i;
                cambioRealizado = true;
                break;
            }
        }

        // Si no se encontró un sorteo posterior, cambiar al primero del día siguiente
        if (!cambioRealizado) {
            sorteoSelect.selectedIndex = 0;

            // Avanza la fecha en un día
            hoy.setDate(hoy.getDate() + 1);
            const añoN = hoy.getFullYear();
            const mesN = String(hoy.getMonth() + 1).padStart(2, '0');
            const diaN = String(hoy.getDate()).padStart(2, '0');
            inputFecha.value = `${añoN}-${mesN}-${diaN}`;
        }
    }
});

window.addEventListener("pageshow", event => {
    if (event.persisted || performance.getEntriesByType("navigation")[0].type === "back_forward") {
        location.reload();
    }
});