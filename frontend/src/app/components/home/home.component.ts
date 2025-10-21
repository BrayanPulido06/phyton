import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  // Características del sistema
  caracteristicas = [
    {
      icono: '📋',
      titulo: 'Registro de Soportes',
      descripcion: 'Registra y gestiona solicitudes de soporte de manera eficiente'
    },
    {
      icono: '📁',
      titulo: 'Carga Masiva',
      descripcion: 'Importa múltiples registros desde archivos Excel'
    },
    {
      icono: '🔍',
      titulo: 'Consulta Rápida',
      descripcion: 'Busca y visualiza tus soportes registrados'
    },
    {
      icono: '📊',
      titulo: 'Reportes',
      descripcion: 'Genera reportes y estadísticas de entregas'
    }
  ];

  // Estadísticas (puedes conectarlas con el backend después)
  estadisticas = [
    { valor: '500+', etiqueta: 'Entregas Realizadas' },
    { valor: '98%', etiqueta: 'Satisfacción' },
    { valor: '24/7', etiqueta: 'Disponibilidad' }
  ];
}