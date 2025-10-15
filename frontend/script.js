const API_URL = 'http://localhost:8000/api';

const soporteForm = document.getElementById('soporteForm');
const soportesTableBody = document.getElementById('soportesTableBody');
const alertContainer = document.getElementById('alertContainer');
const refreshBtn = document.getElementById('refreshBtn');

function mostrarAlerta(mensaje, tipo) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${tipo}`;
    alert.textContent = mensaje;
    alertContainer.appendChild(alert);
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function formatearFecha(fechaStr) {
    const fecha = new Date(fechaStr);
    return fecha.toLocaleString('es-CO', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function cargarSoportes() {
    try {
        soportesTableBody.innerHTML = '<tr><td colspan="6" class="loading">Cargando datos...</td></tr>';
        const response = await fetch(`${API_URL}/soportes/`);
        if (!response.ok) {
            throw new Error('Error al cargar los soportes');
        }
        const soportes = await response.json();
        if (soportes.length === 0) {
            soportesTableBody.innerHTML = '<tr><td colspan="6" class="empty-state">No hay soportes registrados</td></tr>';
            return;
        }
        soportesTableBody.innerHTML = '';
        soportes.forEach(soporte => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${soporte.id}</td>
                <td>${soporte.nombre}</td>
                <td>${soporte.cedula}</td>
                <td>${soporte.direccion}</td>
                <td>${formatearFecha(soporte.fecha_creacion)}</td>
                <td>
                    <button class="btn btn-danger" onclick="eliminarSoporte(${soporte.id})">
                        🗑️ Eliminar
                    </button>
                </td>
            `;
            soportesTableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error:', error);
        soportesTableBody.innerHTML = '<tr><td colspan="6" class="empty-state">Error al cargar los datos</td></tr>';
        mostrarAlerta('Error al cargar los soportes', 'error');
    }
}

async function crearSoporte(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        nombre: formData.get('nombre'),
        cedula: formData.get('cedula'),
        direccion: formData.get('direccion')
    };
    try {
        const response = await fetch(`${API_URL}/soportes/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al crear el soporte');
        }
        mostrarAlerta('Soporte registrado exitosamente', 'success');
        soporteForm.reset();
        cargarSoportes();
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta(error.message, 'error');
    }
}

async function eliminarSoporte(id) {
    if (!confirm('¿Está seguro de que desea eliminar este soporte?')) {
        return;
    }
    try {
        const response = await fetch(`${API_URL}/soportes/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            throw new Error('Error al eliminar el soporte');
        }
        mostrarAlerta('Soporte eliminado exitosamente', 'success');
        cargarSoportes();
    } catch (error) {
        console.error('Error:', error);
        mostrarAlerta(error.message, 'error');
    }
}

soporteForm.addEventListener('submit', crearSoporte);
refreshBtn.addEventListener('click', cargarSoportes);
document.addEventListener('DOMContentLoaded', () => {
    cargarSoportes();
});
