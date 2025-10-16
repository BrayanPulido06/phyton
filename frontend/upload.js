const API_URL = 'http://localhost:8000/api';

const uploadForm = document.getElementById('uploadForm');
const excelFileInput = document.getElementById('excelFile');
const fileNameDisplay = document.getElementById('fileName');
const alertContainer = document.getElementById('alertContainer');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const uploadBtn = document.getElementById('uploadBtn');

// Mostrar nombre del archivo seleccionado
excelFileInput.addEventListener('change', function(e) {
    if (e.target.files.length > 0) {
        const fileName = e.target.files[0].name;
        fileNameDisplay.textContent = fileName;
        fileNameDisplay.style.color = '#2ecc71';
    } else {
        fileNameDisplay.textContent = 'No se ha seleccionado ningún archivo';
        fileNameDisplay.style.color = '#7f8c8d';
    }
});

function mostrarAlerta(mensaje, tipo) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${tipo}`;
    alert.textContent = mensaje;
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 8000);
}

function mostrarProgreso(porcentaje, texto) {
    progressContainer.style.display = 'block';
    progressFill.style.width = porcentaje + '%';
    progressText.textContent = texto;
}

function ocultarProgreso() {
    setTimeout(() => {
        progressContainer.style.display = 'none';
        progressFill.style.width = '0%';
    }, 1000);
}

function mostrarResultados(data) {
    resultsSection.style.display = 'block';
    
    const resultado = data.resultado;
    
    document.getElementById('exitososCount').textContent = resultado.exitosos;
    document.getElementById('fallidosCount').textContent = resultado.fallidos;
    document.getElementById('totalCount').textContent = resultado.total_procesados;
    
    // Mostrar errores si existen
    if (resultado.errores && resultado.errores.length > 0) {
        const erroresContainer = document.getElementById('erroresContainer');
        const erroresList = document.getElementById('erroresList');
        
        erroresContainer.style.display = 'block';
        erroresList.innerHTML = '';
        
        resultado.errores.forEach(error => {
            const errorItem = document.createElement('div');
            errorItem.className = 'error-item';
            errorItem.innerHTML = `
                <strong>Fila ${error.fila}</strong> - Cédula: ${error.cedula}
                <br><span>${error.error}</span>
            `;
            erroresList.appendChild(errorItem);
        });
    }
    
    // Scroll hacia los resultados
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function cargarExcel(event) {
    event.preventDefault();
    
    const file = excelFileInput.files[0];
    const limite = document.getElementById('limite').value;
    
    if (!file) {
        mostrarAlerta('Por favor selecciona un archivo Excel', 'error');
        return;
    }
    
    // Validar extensión
    const extension = file.name.split('.').pop().toLowerCase();
    if (extension !== 'xlsx' && extension !== 'xls') {
        mostrarAlerta('El archivo debe ser de tipo Excel (.xlsx o .xls)', 'error');
        return;
    }
    
    // Validar tamaño (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
        mostrarAlerta('El archivo es demasiado grande. Máximo 5MB', 'error');
        return;
    }
    
    // Preparar FormData
    const formData = new FormData();
    formData.append('file', file);
    
    // Deshabilitar botón
    uploadBtn.disabled = true;
    uploadBtn.textContent = '⏳ Procesando...';
    
    // Ocultar resultados anteriores
    resultsSection.style.display = 'none';
    
    // Mostrar progreso
    mostrarProgreso(30, 'Subiendo archivo...');
    
    try {
        const response = await fetch(`${API_URL}/soportes/upload-excel/?limite=${limite}`, {
            method: 'POST',
            body: formData
        });
        
        mostrarProgreso(70, 'Procesando datos...');
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al procesar el archivo');
        }
        
        mostrarProgreso(100, '¡Completado!');
        
        const data = await response.json();
        
        ocultarProgreso();
        
        // Mostrar mensaje según resultado
        if (data.resultado.exitosos > 0) {
            mostrarAlerta(
                `✅ Carga completada: ${data.resultado.exitosos} registros insertados correctamente`, 
                'success'
            );
        }
        
        if (data.resultado.fallidos > 0) {
            mostrarAlerta(
                `⚠️ ${data.resultado.fallidos} registros no pudieron ser insertados`, 
                'warning'
            );
        }
        
        // Mostrar resultados
        mostrarResultados(data);
        
        // Limpiar formulario
        uploadForm.reset();
        fileNameDisplay.textContent = 'No se ha seleccionado ningún archivo';
        fileNameDisplay.style.color = '#7f8c8d';
        
    } catch (error) {
        console.error('Error:', error);
        mostrarProgreso(100, 'Error en el proceso');
        ocultarProgreso();
        mostrarAlerta(error.message, 'error');
    } finally {
        // Rehabilitar botón
        uploadBtn.disabled = false;
        uploadBtn.textContent = '📤 Cargar Archivo';
    }
}

// Event Listeners
uploadForm.addEventListener('submit', cargarExcel);