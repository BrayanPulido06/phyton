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
  // Cuando está en Docker con Nginx, usa rutas relativas
  // IMPORTANTE: El "/" al final es necesario para FastAPI
  private apiUrl = '/api/soportes/';

  constructor(private http: HttpClient) {}

  /**
   * Obtener todos los soportes
   */
  getSoportes(): Observable<Soporte[]> {
    return this.http.get<Soporte[]>(this.apiUrl)
      .pipe(catchError(this.handleError));
  }

  /**
   * Obtener un soporte por ID
   */
  getSoporteById(id: number): Observable<Soporte> {
    return this.http.get<Soporte>(`${this.apiUrl}/${id}`)
      .pipe(catchError(this.handleError));
  }

  /**
   * Crear un nuevo soporte
   */
  crearSoporte(soporte: Soporte): Observable<Soporte> {
    return this.http.post<Soporte>(this.apiUrl, soporte)
      .pipe(catchError(this.handleError));
  }

  /**
   * Eliminar un soporte
   */
  eliminarSoporte(id: number): Observable<SoporteResponse> {
    return this.http.delete<SoporteResponse>(`${this.apiUrl}/${id}`)
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