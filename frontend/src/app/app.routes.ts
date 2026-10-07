import { Routes } from '@angular/router';
import { LayoutComponent } from './core/layout/layout/layout.component.js';

export const routes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'tickets' },
      {
        path: 'tickets',
        loadChildren: () =>
          import('./features/tickets/tickets.routes').then((m) => m.TICKETS_ROUTES),
      },
      {
        path: 'ayuda',
        loadComponent: () =>
          import('./features/ayuda/ayuda/ayuda.component').then((m) => m.AyudaComponent),
      },
    ],
  },
  { path: '**', redirectTo: 'tickets' },
];