import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { catchError, forkJoin, of, switchMap, timer } from 'rxjs';
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { SelectModule } from 'primeng/select';
import { TagModule } from 'primeng/tag';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { TicketService } from '../../../core/services/ticket.service';
import { CatalogoService } from '../../../core/services/catalogo.service';
import { TicketResumen } from '../../../core/models/ticket';
import { Resumen } from '../../../core/models/resumen';
import { DatePipe } from '@angular/common';
import { EstadoBadgeComponent } from '../../../shared/estado-badge/estado-badge.component';
import { PrioridadBadgeComponent } from '../../../shared/prioridad-badge/prioridad-badge.component';


type Severidad = 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast';

@Component({
  selector: 'app-lista-tickets',
  imports: [
    FormsModule,
    DatePipe, 
    RouterLink,
    ButtonModule, 
    TableModule, 
    SelectModule, 
    TagModule, 
    CardModule, 
    MessageModule,
    EstadoBadgeComponent,
    PrioridadBadgeComponent,
  ],
  templateUrl: './lista-tickets.component.html',
  styleUrl: './lista-tickets.component.css',
})
export class ListaTicketsComponent {
  private ticketService = inject(TicketService);
  private catalogoService = inject(CatalogoService);

  // Datos que vienen de la API
  tickets = signal<TicketResumen[]>([]);
  resumen = signal<Resumen | null>(null);
  error = signal<string | null>(null);
  catalogos = toSignal(this.catalogoService.catalogos$);


  filtroEstado = signal<string | null>(null);
  filtroPrioridad = signal<string | null>(null);
  filtroCategoria = signal<string | null>(null);

   private colorEstado: Record<string, Severidad> = {
      'Nuevo': 'info',
      'En proceso': 'warn',
      'Resuelto': 'success',
      'Cerrado': 'secondary',
    };
    private colorPrioridad: Record<string, Severidad> = {
      'Crítica': 'danger',
      'Alta': 'warn',
      'Media': 'secondary',
      'Baja': 'info',
    };

    severidadEstado(estado: string): Severidad {
      return this.colorEstado[estado] ?? 'secondary';
    }
    severidadPrioridad(prioridad: string): Severidad {
      return this.colorPrioridad[prioridad] ?? 'secondary';
    }
  // Lista filtrada: se recalcula sola cuando cambia un filtro o llegan datos
  ticketsFiltrados = computed(() => {
    const estado = this.filtroEstado();
    const prioridad = this.filtroPrioridad();
    const categoria = this.filtroCategoria();


    return this.tickets().filter(
      (t) =>
        (!estado || t.estado === estado) &&
        (!prioridad || t.prioridad === prioridad) &&
        (!categoria || t.categoria === categoria),
    );
  });

  // Contador por estado, con 0 si no hay ninguno
  contar(estado: string): number {
    return this.resumen()?.por_estado[estado] ?? 0;
  }

  constructor() {
    timer(0, 5000)
      .pipe(
        switchMap(() =>
          forkJoin({
            tickets: this.ticketService.listar(),
            resumen: this.ticketService.resumen(),
          }).pipe(
            
            catchError(() => {
              this.error.set('No se pudo conectar con la API.');
              return of(null);
            }),
          ),
        ),
        takeUntilDestroyed(),
      )
      .subscribe((datos) => {
        if (!datos) return;
        this.error.set(null);
        this.tickets.set(datos.tickets);
        this.resumen.set(datos.resumen);
      });
  }

  limpiarFiltros() {
    this.filtroEstado.set(null);
    this.filtroPrioridad.set(null);
    this.filtroCategoria.set(null);
  }
}