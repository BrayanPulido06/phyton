import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { SoporteListComponent } from './components/soporte-list/soporte-list.component';
import { UploadExcelComponent } from './components/upload-excel/upload-excel.component';


export const routes: Routes = [
  { path: '', component: HomeComponent }, // Página de inicio/presentación
  { path: 'login', component: LoginComponent }, // Login
  { path: 'soportes', component: SoporteListComponent }, // Lista de soportes (protegida)
  { path: 'upload-excel', component: UploadExcelComponent }, // Carga masiva
  { path: '**', redirectTo: '' } // Redirección para rutas no encontradas
];