import { Routes } from '@angular/router';
import { ListaTicketsComponent } from './lista-tickets/lista-tickets.component';
import { NuevoTicketComponent } from './nuevo-ticket/nuevo-ticket.component';
import { DetalleTicketComponent } from './detalle-ticket/detalle-ticket.component';

export const TICKETS_ROUTES: Routes = [
  { path: '', component: ListaTicketsComponent },
  { path: 'nuevo', component: NuevoTicketComponent }, // antes de ':id'
  { path: ':id', component: DetalleTicketComponent },
];