import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NuevoTicket, TicketDetalle, TicketResumen, Transiciones } from '../models/ticket';
import { Resumen } from '../models/resumen';
import { Historial } from '../models/historial';

@Injectable({ providedIn: 'root' })
export class TicketService {
  private http = inject(HttpClient);
  private base = environment.apiUrl;

  listar(): Observable<TicketResumen[]> {
    return this.http.get<TicketResumen[]>(`${this.base}/tickets`);
  }

  resumen(): Observable<Resumen> {
    return this.http.get<Resumen>(`${this.base}/resumen`);
  }

  transiciones(): Observable<Transiciones> {
    return this.http.get<Transiciones>(`${this.base}/transiciones`);
  }

  obtener(id: number): Observable<TicketDetalle> {
    return this.http.get<TicketDetalle>(`${this.base}/tickets/${id}`);
  }

  historial(id: number): Observable<Historial[]> {
    return this.http.get<Historial[]>(`${this.base}/tickets/${id}/historial`);
  }

  crear(ticket: NuevoTicket): Observable<{ id: number }> {
    return this.http.post<{ id: number }>(`${this.base}/tickets`, ticket);
  }

  asignarResponsable(id: number, responsableId: number): Observable<TicketDetalle> {
    return this.http.patch<TicketDetalle>(`${this.base}/tickets/${id}/responsable`, {
      responsable_id: responsableId,
    });
  }

  cambiarEstado(id: number, nuevoEstado: string): Observable<TicketDetalle> {
    return this.http.patch<TicketDetalle>(`${this.base}/tickets/${id}/estado`, {
      nuevo_estado: nuevoEstado,
    });
  }
}