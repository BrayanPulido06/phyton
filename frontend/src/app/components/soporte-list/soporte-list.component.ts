import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { SoporteService, Soporte } from '../../services/soporte.service';

@Component({
  selector: 'app-soporte-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './soporte-list.component.html',
  styleUrl: './soporte-list.component.css'
})
export class SoporteListComponent implements OnInit {
  soportes: Soporte[] = [];
  cargando = false;
  alertas: { mensaje: string; tipo: 'success' | 'error' | 'warning' }[] = [];

  nuevoSoporte: Soporte = {
    nombre: '',
    cedula: '',
    direccion: ''
  };

  constructor(private soporteService: SoporteService) {}

  ngOnInit(): void {
    this.cargarSoportes();
  }

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

  crearSoporte(): void {
    if (this.nuevoSoporte.nombre && this.nuevoSoporte.cedula && this.nuevoSoporte.direccion) {
      this.soporteService.crearSoporte(this.nuevoSoporte).subscribe({
        next: (soporte: Soporte) => {
          this.soportes.push(soporte);
          this.limpiarFormulario();
          this.mostrarAlerta('Soporte creado con éxito', 'success');
        },
      error: (error: Error) => {
          console.error('Error al crear soporte:', error);
          this.mostrarAlerta('Error al crear el soporte', 'error');
        }
      });
    } else {
      this.mostrarAlerta('Por favor, complete todos los campos', 'warning');
    }
  }

  eliminarSoporte(id: number): void {
    this.soporteService.eliminarSoporte(id).subscribe({
      next: () => {
        this.soportes = this.soportes.filter(s => s.id !== id);
        this.mostrarAlerta('Soporte eliminado con éxito', 'success');
      },
      error: (error: Error) => {
        console.error('Error al eliminar soporte:', error);
        this.mostrarAlerta('Error al eliminar el soporte', 'error');
      }
    });
  }

  mostrarAlerta(mensaje: string, tipo: 'success' | 'error' | 'warning'): void {
    this.alertas.push({ mensaje, tipo });
    setTimeout(() => this.alertas.shift(), 5000);
  }

  limpiarFormulario(): void {
    this.nuevoSoporte = {
      nombre: '',
      cedula: '',
      direccion: ''
    };
  }

  formatearFecha(fechaStr: string): string {
    if (!fechaStr) {
      return 'Fecha no disponible';
    }
    const fecha = new Date(fechaStr);
    return fecha.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  exportToExcel(): void {
    this.soporteService.exportToExcel().subscribe({
      next: (data: Blob) => {
        const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'soportes.xlsx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: (error: Error) => {
        console.error('Error al exportar a Excel:', error);
        this.mostrarAlerta('Error al exportar a Excel', 'error');
      }
    });
  }

  exportToPDF(): void {
    this.soporteService.exportToPDF().subscribe({
      next: (data: Blob) => {
        const blob = new Blob([data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'soportes.pdf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: (error: Error) => {
        console.error('Error al exportar a PDF:', error);
        this.mostrarAlerta('Error al exportar a PDF', 'error');
      }
    });
  }
}
