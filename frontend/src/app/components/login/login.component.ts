import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';

interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    email?: string;
  };
}

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  private API_URL = 'http://localhost:8000/api';

  // Modelo del formulario
  loginData: LoginRequest = {
    username: '',
    password: ''
  };

  // Estados
  cargando: boolean = false;
  mostrarPassword: boolean = false;
  errorMensaje: string = '';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Verificar si ya hay sesión activa
    this.verificarSesion();
  }

  /**
   * Verificar si ya hay una sesión activa
   */
  verificarSesion(): void {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Si ya hay token, redirigir a soportes
      this.router.navigate(['/soportes']);
    }
  }

  /**
   * Alternar visibilidad de la contraseña
   */
  togglePasswordVisibility(): void {
    this.mostrarPassword = !this.mostrarPassword;
  }

  /**
   * Validar formulario
   */
  validarFormulario(): boolean {
    if (!this.loginData.username || !this.loginData.password) {
      this.errorMensaje = 'Por favor complete todos los campos';
      return false;
    }

    if (this.loginData.username.length < 3) {
      this.errorMensaje = 'El usuario debe tener al menos 3 caracteres';
      return false;
    }

    if (this.loginData.password.length < 4) {
      this.errorMensaje = 'La contraseña debe tener al menos 4 caracteres';
      return false;
    }

    return true;
  }

  /**
   * Iniciar sesión
   */
  async login(): Promise<void> {
    // Limpiar mensaje de error
    this.errorMensaje = '';

    // Validar formulario
    if (!this.validarFormulario()) {
      return;
    }

    this.cargando = true;

    try {
      // Preparar datos para FormData (OAuth2 requiere form-data)
      const formData = new FormData();
      formData.append('username', this.loginData.username);
      formData.append('password', this.loginData.password);

      // Hacer petición de login
      const response = await this.http.post<LoginResponse>(
        `${this.API_URL}/auth/login`,
        formData
      ).toPromise();

      if (response && response.access_token) {
        // Guardar token en localStorage
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('token_type', response.token_type);
        
        // Guardar información del usuario
        if (response.user) {
          localStorage.setItem('user', JSON.stringify(response.user));
        }

        // Redirigir a la página de soportes
        this.router.navigate(['/soportes']);
      }

    } catch (error: any) {
      console.error('Error de login:', error);
      
      // Manejar diferentes tipos de errores
      if (error.status === 401) {
        this.errorMensaje = 'Usuario o contraseña incorrectos';
      } else if (error.status === 0) {
        this.errorMensaje = 'No se puede conectar con el servidor';
      } else {
        this.errorMensaje = error.error?.detail || 'Error al iniciar sesión';
      }
    } finally {
      this.cargando = false;
    }
  }

  /**
   * Limpiar mensaje de error
   */
  limpiarError(): void {
    this.errorMensaje = '';
  }
}