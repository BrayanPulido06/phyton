import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface Soporte {
  id?: number;
  nombre: string;
  cedula: string;
  direccion: string;
  fecha_creacion?: string;
}

export interface SoporteResponse {
  message: string;
  id?: number;
}

@Injectable({
  providedIn: 'root'
})
export class SoporteService {
  private apiUrl = 'http://localhost:8000/api'; // Asegúrate de que este puerto coincida con el de tu backend
  constructor(private http: HttpClient) {}

  /**
   * Obtener todos los soportes
   */
  getSoportes(): Observable<Soporte[]> {
    return this.http.get<Soporte[]>(`${this.apiUrl}/soportes/`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Obtener un soporte por ID
   */
  getSoporteById(id: number): Observable<Soporte> {
    return this.http.get<Soporte>(`${this.apiUrl}/soportes/${id}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Crear un nuevo soporte
   */
  crearSoporte(soporte: Soporte): Observable<Soporte> {
    return this.http.post<Soporte>(`${this.apiUrl}/soportes/`, soporte)
      .pipe(catchError(this.handleError));
  }

  /**
   * Eliminar un soporte
   */
  eliminarSoporte(id: number): Observable<SoporteResponse> {
    return this.http.delete<SoporteResponse>(`${this.apiUrl}/soportes/${id}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Exportar a Excel
   */
  exportToExcel(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/soportes/export/excel`, { responseType: 'blob' })
      .pipe(catchError(this.handleError));
  }

  /**
   * Exportar a PDF
   */
  exportToPDF(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/soportes/export/pdf`, { responseType: 'blob' })
      .pipe(catchError(this.handleError));
  }

  /**
   * Manejo de errores
   */
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Ocurrió un error desconocido';
    
    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Error del lado del servidor
      errorMessage = error.error?.detail || `Error ${error.status}: ${error.message}`;
    }
    
    console.error('Error completo:', error);
    return throwError(() => new Error(errorMessage));
  }
}