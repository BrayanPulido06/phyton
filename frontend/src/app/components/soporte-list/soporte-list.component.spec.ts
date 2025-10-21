import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router'; // ← LÍNEA NUEVA

@Component({
  selector: 'app-soporte-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink], // ← AGREGADO RouterLink
  templateUrl: './soporte-list.component.html',
  styleUrl: './soporte-list.component.css'
})
export class SoporteListComponent {
  // Aquí va tu código del componente (variables, métodos, etc.)
  // Por ejemplo:
  soportes: any[] = [];
  nuevoSoporte = {
    nombre: '',
    cedula: '',
    direccion: ''
  };
  alertas: any[] = [];
  cargando = false;

  crearSoporte() {
    // Tu lógica aquí
  }

  cargarSoportes() {
    // Tu lógica aquí
  }

  eliminarSoporte(id: number) {
    // Tu lógica aquí
  }

  formatearFecha(fecha: string) {
    // Tu lógica aquí
    return fecha;
  }
}