const elements = {
    sorteoSelect: document.getElementById("sorteo"),
    fechaInput: document.getElementById("fecha"),
    hiddenLimite: document.getElementById("limiteMax"),
    hiddenLimiteReventado: document.getElementById("limite_Reventado"),
    contenedor: document.querySelector(".grid-container"),
    tablaBody: document.getElementById("tabla-body"),
    numerosContainer: document.getElementById("numeros-container"),
    totalDisplay: document.getElementById("total"),
    reventadoCheckbox: document.getElementById('reventado'),
    reventadoInput: document.querySelector('.reventado_monto'),
    agregarBtn: document.getElementById('agregar-btn'),
};

const limites = {
    maximo: parseInt(elements.hiddenLimite.value),
    reventado: parseInt(elements.hiddenLimiteReventado.value),
};

let total = 0;
let index = 0;

function actualizarResumenFacturas() {
    const fecha = elements.fechaInput.value;
    const [sorteoID] = elements.sorteoSelect.value.split(",");
    const filtradas = facturasData.filter(f => f.Fecha_Vendida === fecha && f.idLista == sorteoID);

    const resumen = {};
    const resumenReventado = {};
    filtradas.forEach(factura => {
        factura.Numeros.forEach(item => {
            const numero = parseInt(item.numero);
            resumen[numero] = (resumen[numero] || 0) + parseInt(item.monto);
            resumenReventado[numero] = (resumenReventado[numero] || 0) + parseInt(item.reventado);
        });
    });

    elements.contenedor.innerHTML = ""; // Clear previous content
    for (let num = 0; num <= 99; num++) {
        const valor = resumen[num] || 0;
        const valorReventado = resumenReventado[num] || 0;
        const color = valor > 8000 ? "red" : valor >= 5000 ? "yellow" : valor > 0 ? "yellowgreen" : "white";

        elements.contenedor.innerHTML += `
            <div class="cuadro" style="background-color: ${color};">
                <div class="numero">${num.toString().padStart(2, '0')}</div>
                <div class="vendido">Monto: ₡${valor}</div>
                <div class="restante">Restante: ₡${limites.maximo - valor}</div>
                <div class="vendido">Reventado: ₡${valorReventado}</div>
            </div>`;
    }
}

function agregarNumero() {
    const id = `fila-${index++}`;
    const numero = parseInt(document.querySelector('.numero').value);
    const monto = parseInt(document.querySelector('.monto').value);
    let montoReventado = parseInt(document.querySelector('.reventado_monto').value) || 0;

    if (!numero || !monto || monto <= 0 || monto > limites.maximo || monto % 5 !== 0 || montoReventado % 5 !== 0) {
        alert("Número o monto inválido.");
        return;
    }

    const fecha = elements.fechaInput.value;
    const [sorteoID] = elements.sorteoSelect.value.split(",");
    const filtradas = facturasData.filter(f => f.Fecha_Vendida === fecha && f.idLista == sorteoID);
    
    // Sumar lo que hay en las facturas filtradas
    let montoVendido = 0, montoVendidoRestante = 0;
    filtradas.forEach(factura => {
        factura.Numeros.forEach(item => {
            if (parseInt(item.numero) === numero) {
                montoVendido += parseInt(item.monto);
                montoVendidoRestante += parseInt(item.reventado);
            }
        });
    });

    // Sumar lo que hay en la tabla también
    let numerosTabla = Array.from(document.querySelectorAll("#tabla-body tr td:nth-child(1)")).map(td => parseInt(td.innerText));
    let montosTabla = Array.from(document.querySelectorAll("#tabla-body tr td:nth-child(2)")).map(td => parseInt(td.innerText.replace("₡", "")));
    let montosReventadoTabla = Array.from(document.querySelectorAll("#tabla-body tr td:nth-child(3)")).map(td => parseInt(td.innerText.replace("₡", "")));

    for (let i = 0; i < numerosTabla.length; i++) {
        if (numerosTabla[i] === numero) {
            montoVendido += montosTabla[i];
            montoVendidoRestante += montosReventadoTabla[i];
        }
    }

    const restante = limites.maximo - montoVendido;
    const restanteReventado = limites.reventado - montoVendidoRestante;

    if (monto > restante || montoReventado > restanteReventado) {
        alert(`El monto excede el límite. Restante: ₡${restante}, Reventado: ₡${restanteReventado}`);
        return;
    }

    elements.tablaBody.innerHTML += `
        <tr>
            <td>${numero}</td>
            <td>₡${monto}</td>
            <td>₡${montoReventado}</td>
            <td><button class='btn' style="width: 60%;" type="button" onclick="BorrarNumero(event, '${id}')">❌</button></td>
        </tr>`;

    ["numero", "monto", "reventado_monto"].forEach(name => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = `${name}[]`;
        input.id = id;
        input.value = name === "numero" ? numero : name === "monto" ? monto : montoReventado;
        elements.numerosContainer.appendChild(input);
    });

    total += monto + montoReventado;
    elements.totalDisplay.innerText = total;

    document.querySelector('.numero').value = "";
    document.querySelector('.numero').focus();
}

function validarValores() {
    const numero = parseInt(document.querySelector('.numero').value);
    const monto = parseInt(document.querySelector('.monto').value);
    const montoReventado = parseInt(document.querySelector('.reventado_monto').value);

    if (numero > 99) document.querySelector('.numero').value = "";
    if (monto > limites.maximo) document.querySelector('.monto').value = "";
    if (montoReventado > monto || montoReventado > limites.reventado) document.querySelector('.reventado_monto').value = "";
}

function verficar_numeros(event) {
    event.preventDefault(); // Evitar el envío del formulario por defecto
    if (elements.tablaBody.rows.length === 0) {
        alert("No hay números ingresados. Por favor, ingrese al menos un número.");
        event.preventDefault() 
    } else {
        const confirmacion = confirm("¿Estás seguro de que quieres confirmar esta compra?\nUna vez procesada no se puede modificar.");
        if (confirmacion) {   
            event.target.closest("form").submit();
        }
    }
}


function BorrarNumero(event, id) {
    const fila = event.target.closest("tr");
    const monto = parseInt(fila.cells[1].innerText.replace("₡", ""));
    const montoReventado = parseInt(fila.cells[2].innerText.replace("₡", ""));
    total -= (monto + montoReventado);
    elements.totalDisplay.innerText = total;
    fila.remove();
    document.querySelectorAll(`input[id='${id}']`).forEach(input => input.remove());
}



document.addEventListener('DOMContentLoaded', () => {
    elements.reventadoCheckbox.addEventListener('change', () => {
        elements.reventadoInput.disabled = !elements.reventadoCheckbox.checked;
        if (!elements.reventadoCheckbox.checked) elements.reventadoInput.value = '';
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
    if (sorteoSelect.value !== "" && inputFecha.value !== "") {
        actualizarResumenFacturas();
    }
});

document.addEventListener('keydown', event => {
    if (event.key === 'Enter') {
        event.preventDefault();
        elements.agregarBtn.click();
    }
});

window.addEventListener("pageshow", event => {
    if (event.persisted || performance.getEntriesByType("navigation")[0].type === "back_forward") {
        location.reload();
    }
});