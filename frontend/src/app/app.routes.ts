import { Routes } from '@angular/router';
import { SoporteListComponent } from './components/soporte-list/soporte-list.component';
import { UploadExcelComponent } from './components/upload-excel/upload-excel.component';


export const routes: Routes = [
  { path: '', component: SoporteListComponent}, // Ruta principal
  { path: 'upload-excel', component: UploadExcelComponent },
  { path: '**', redirectTo: '' } // Redirección para rutas no encontradas
];
