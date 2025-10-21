import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface ResultadoCarga {
  exitosos: number;
  fallidos: number;
  total_procesados: number;
  errores: ErrorCarga[];
}

interface ErrorCarga {
  fila: number;
  cedula: string;
  error: string;
}

interface RespuestaCarga {
  mensaje: string;
  resultado: ResultadoCarga;
}

@Component({
  selector: 'app-upload-excel',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './upload-excel.component.html',
  styleUrl: './upload-excel.component.css'
})
export class UploadExcelComponent {
  private API_URL = 'http://localhost:8000/api';
  
  // Variables del formulario
  archivoSeleccionado: File | null = null;
  nombreArchivo: string = 'No se ha seleccionado ningún archivo';
  limite: number = 100;
  
  // Variables de estado
  cargando: boolean = false;
  mostrarProgreso: boolean = false;
  porcentajeProgreso: number = 0;
  textoProgreso: string = 'Procesando...';
  mostrarResultados: boolean = false;
  
  // Variables de resultados
  exitosos: number = 0;
  fallidos: number = 0;
  totalProcesados: number = 0;
  errores: ErrorCarga[] = [];
  
  // Alertas
  alertas: { mensaje: string; tipo: 'success' | 'error' | 'warning' }[] = [];

  constructor(private http: HttpClient) {}

  /**
   * Manejar selección de archivo
   */
  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.archivoSeleccionado = file;
      this.nombreArchivo = file.name;
    } else {
      this.archivoSeleccionado = null;
      this.nombreArchivo = 'No se ha seleccionado ningún archivo';
    }
  }

  /**
   * Mostrar alerta temporal
   */
  mostrarAlerta(mensaje: string, tipo: 'success' | 'error' | 'warning'): void {
    const alerta = { mensaje, tipo };
    this.alertas.push(alerta);

    // Eliminar la alerta después de 8 segundos
    setTimeout(() => {
      const index = this.alertas.indexOf(alerta);
      if (index > -1) {
        this.alertas.splice(index, 1);
      }
    }, 8000);
  }

  /**
   * Actualizar barra de progreso
   */
  actualizarProgreso(porcentaje: number, texto: string): void {
    this.mostrarProgreso = true;
    this.porcentajeProgreso = porcentaje;
    this.textoProgreso = texto;
  }

  /**
   * Ocultar barra de progreso
   */
  ocultarBarraProgreso(): void {
    setTimeout(() => {
      this.mostrarProgreso = false;
      this.porcentajeProgreso = 0;
    }, 1000);
  }

  /**
   * Validar archivo antes de cargar
   */
  validarArchivo(): boolean {
    if (!this.archivoSeleccionado) {
      this.mostrarAlerta('Por favor selecciona un archivo Excel', 'error');
      return false;
    }

    // Validar extensión
    const extension = this.archivoSeleccionado.name.split('.').pop()?.toLowerCase();
    if (extension !== 'xlsx' && extension !== 'xls') {
      this.mostrarAlerta('El archivo debe ser de tipo Excel (.xlsx o .xls)', 'error');
      return false;
    }

    // Validar tamaño (máximo 5MB)
    if (this.archivoSeleccionado.size > 5 * 1024 * 1024) {
      this.mostrarAlerta('El archivo es demasiado grande. Máximo 5MB', 'error');
      return false;
    }

    return true;
  }

  /**
   * Cargar archivo Excel
   */
  async cargarExcel(): Promise<void> {
    // Validar archivo
    if (!this.validarArchivo()) {
      return;
    }

    // Preparar FormData
    const formData = new FormData();
    formData.append('file', this.archivoSeleccionado!);

    // Cambiar estado
    this.cargando = true;
    this.mostrarResultados = false;

    // Mostrar progreso
    this.actualizarProgreso(30, 'Subiendo archivo...');

    try {
      // Hacer petición HTTP
      const response = await this.http.post<RespuestaCarga>(
        `${this.API_URL}/soportes/upload-excel/?limite=${this.limite}`,
        formData
      ).toPromise();

      this.actualizarProgreso(70, 'Procesando datos...');

      if (response) {
        this.actualizarProgreso(100, '¡Completado!');
        this.ocultarBarraProgreso();

        // Actualizar resultados
        this.exitosos = response.resultado.exitosos;
        this.fallidos = response.resultado.fallidos;
        this.totalProcesados = response.resultado.total_procesados;
        this.errores = response.resultado.errores || [];

        // Mostrar alertas según resultado
        if (response.resultado.exitosos > 0) {
          this.mostrarAlerta(
            `✅ Carga completada: ${response.resultado.exitosos} registros insertados correctamente`,
            'success'
          );
        }

        if (response.resultado.fallidos > 0) {
          this.mostrarAlerta(
            `⚠️ ${response.resultado.fallidos} registros no pudieron ser insertados`,
            'warning'
          );
        }

        // Mostrar sección de resultados
        this.mostrarResultados = true;

        // Limpiar formulario
        this.limpiarFormulario();

        // Scroll hacia resultados
        setTimeout(() => {
          document.getElementById('resultsSection')?.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
          });
        }, 100);
      }

    } catch (error: any) {
      console.error('Error:', error);
      this.actualizarProgreso(100, 'Error en el proceso');
      this.ocultarBarraProgreso();
      
      const mensajeError = error.error?.detail || error.message || 'Error al procesar el archivo';
      this.mostrarAlerta(mensajeError, 'error');
    } finally {
      this.cargando = false;
    }
  }

  /**
   * Limpiar formulario
   */
  limpiarFormulario(): void {
    this.archivoSeleccionado = null;
    this.nombreArchivo = 'No se ha seleccionado ningún archivo';
    this.limite = 100;
    
    // Limpiar input file
    const fileInput = document.getElementById('excelFile') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  }
}