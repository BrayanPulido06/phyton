import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router'; // ← AGREGAR ESTA LÍNEA
import { SoporteService, Soporte } from '../../services/soporte.service';

@Component({
  selector: 'app-soporte-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink], // ← AGREGAR RouterLink AQUÍ
  templateUrl: './soporte-list.component.html',
  styleUrl: './soporte-list.component.css'
})
export class SoporteListComponent implements OnInit {
  // ... resto del código igual
  soportes: Soporte[] = [];
  cargando = false;
  alertas: { mensaje: string; tipo: 'success' | 'error' | 'warning' }[] = [];

  // Modelo para el formulario
  nuevoSoporte: Soporte = {
    nombre: '',
    cedula: '',
    direccion: ''
  };

  constructor(private soporteService: SoporteService) {}

  ngOnInit(): void {
    this.cargarSoportes();
  }

  /**
   * Cargar todos los soportes desde la API
   */
  cargarSoportes(): void {
    this.cargando = true;
    
    this.soporteService.getSoportes().subscribe({
      next: (data: Soporte[]) => {
        this.soportes = data;
        this.cargando = false;
        console.log('Soportes cargados:', data);
      },
      error: (error: Error) => {
        console.error('Error al cargar soportes:', error);
        this.mostrarAlerta('Error al cargar los soportes', 'error');
        this.cargando = false;
      }
    });
  }

  /**
   * Crear un nuevo soporte
   */
  crearSoporte(): void {
    // Validaciones básicas
    if (!this.nuevoSoporte.nombre || !this.nuevoSoporte.cedula || !this.nuevoSoporte.direccion) {
      this.mostrarAlerta('Por favor complete todos los campos', 'warning');
      return;
    }

    if (this.nuevoSoporte.nombre.length < 3) {
      this.mostrarAlerta('El nombre debe tener al menos 3 caracteres', 'warning');
      return;
    }

    if (this.nuevoSoporte.cedula.length < 5) {
      this.mostrarAlerta('La cédula debe tener al menos 5 caracteres', 'warning');
      return;
    }

    if (this.nuevoSoporte.direccion.length < 5) {
      this.mostrarAlerta('La dirección debe tener al menos 5 caracteres', 'warning');
      return;
    }

    this.soporteService.crearSoporte(this.nuevoSoporte).subscribe({
      next: (response: Soporte) => {
        this.mostrarAlerta('Soporte registrado exitosamente', 'success');
        this.limpiarFormulario();
        this.cargarSoportes();
      },
      error: (error: Error) => {
        console.error('Error al crear soporte:', error);
        this.mostrarAlerta(error.message, 'error');
      }
    });
  }

  /**
   * Eliminar un soporte
   */
  eliminarSoporte(id: number): void {
    if (!confirm('¿Está seguro de que desea eliminar este soporte?')) {
      return;
    }

    this.soporteService.eliminarSoporte(id).subscribe({
      next: (response: any) => {
        this.mostrarAlerta('Soporte eliminado exitosamente', 'success');
        this.cargarSoportes();
      },
      error: (error: Error) => {
        console.error('Error al eliminar soporte:', error);
        this.mostrarAlerta(error.message, 'error');
      }
    });
  }

  /**
   * Mostrar alerta temporal
   */
  mostrarAlerta(mensaje: string, tipo: 'success' | 'error' | 'warning'): void {
    const alerta = { mensaje, tipo };
    this.alertas.push(alerta);

    // Eliminar la alerta después de 5 segundos
    setTimeout(() => {
      const index = this.alertas.indexOf(alerta);
      if (index > -1) {
        this.alertas.splice(index, 1);
      }
    }, 5000);
  }

  /**
   * Limpiar el formulario
   */
  limpiarFormulario(): void {
    this.nuevoSoporte = {
      nombre: '',
      cedula: '',
      direccion: ''
    };
  }

  /**
   * Formatear fecha al estilo colombiano
   */
  formatearFecha(fechaStr: string): string {
    const fecha = new Date(fechaStr);
    return fecha.toLocaleString('es-CO', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}