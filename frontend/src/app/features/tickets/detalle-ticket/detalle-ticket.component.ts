import { Component, computed, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { concat, finalize, forkJoin } from 'rxjs';

import { CardModule } from 'primeng/card';
import { TagModule } from 'primeng/tag';
import { SelectModule } from 'primeng/select';
import { ButtonModule } from 'primeng/button';
import { TimelineModule } from 'primeng/timeline';
import { MessageModule } from 'primeng/message';
import { MessageService } from 'primeng/api';

import { TicketService } from '../../../core/services/ticket.service';
import { CatalogoService } from '../../../core/services/catalogo.service';
// Ajusta estas rutas/nombres si tus modelos están en otro archivo:
import { TicketDetalle } from '../../../core/models/ticket';
import { Catalogos } from '../../../core/models/catalogos';
import { Historial } from '../../../core/models/historial';

import { EstadoBadgeComponent } from '../../../shared/estado-badge/estado-badge.component';
import { PrioridadBadgeComponent } from '../../../shared/prioridad-badge/prioridad-badge.component';

type Severidad = 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast';

@Component({
  selector: 'app-detalle-ticket',
  imports: [
    DatePipe, 
    FormsModule, 
    RouterLink,
    CardModule, 
    TagModule, 
    SelectModule, 
    ButtonModule, 
    TimelineModule, 
    MessageModule,
    EstadoBadgeComponent,
    PrioridadBadgeComponent,
  ],
  templateUrl: './detalle-ticket.component.html',
})
export class DetalleTicketComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private tickets = inject(TicketService);
  private catalogoService = inject(CatalogoService);
  private toast = inject(MessageService);
  private destroyRef = inject(DestroyRef);

  private id = 0;

  ticket = signal<TicketDetalle | null>(null);
  historial = signal<Historial[]>([]);
  transiciones = signal<Record<string, string[]>>({});
  catalogos = signal<Catalogos | null>(null);

  cargando = signal(true);
  guardando = signal(false);
  error = signal<string | null>(null);

  // Valores de los selects
  responsableId = signal<number | null>(null);
  nuevoEstado = signal<string | null>(null);

  cerrado = computed(() => this.ticket()?.estado === 'Cerrado');

  estadosPermitidos = computed(() => {
    const t = this.ticket();
    return t ? (this.transiciones()[t.estado] ?? []) : [];
  });

  hayCambios = computed(() => {
    const t = this.ticket();
    if (!t) return false;
    const cambioResp =
      this.responsableId() !== null && this.responsableId() !== t.responsable_id;
    return cambioResp || this.nuevoEstado() !== null;
  });

  ngOnInit() {
    this.id = Number(this.route.snapshot.paramMap.get('id'));

    forkJoin({
      ticket: this.tickets.obtener(this.id),
      historial: this.tickets.historial(this.id),
      transiciones: this.tickets.transiciones(),
      catalogos: this.catalogoService.catalogos$,
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (r) => {
          this.transiciones.set(r.transiciones);
          this.catalogos.set(r.catalogos);
          this.aplicarTicket(r.ticket, r.historial);
          this.cargando.set(false);
        },
        error: (e) => {
          this.error.set(this.mensajeError(e));
          this.cargando.set(false);
        },
      });
  }

  actualizar() {
    const t = this.ticket();
    if (!t || !this.hayCambios()) return;

    const llamadas = [];
    const resp = this.responsableId();
    if (resp !== null && resp !== t.responsable_id) {
      llamadas.push(this.tickets.asignarResponsable(this.id, resp));
    }
    const estado = this.nuevoEstado();
    if (estado) {
      llamadas.push(this.tickets.cambiarEstado(this.id, estado));
    }

    this.guardando.set(true);
    this.error.set(null);

    // concat: ejecuta en orden (primero responsable, luego estado) y se detiene si una falla
    concat(...llamadas)
      .pipe(
        finalize(() => this.guardando.set(false)),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe({
        error: (e) => {
          this.error.set(this.mensajeError(e));
          this.refrescar(); // muestra lo que realmente quedó guardado
        },
        complete: () => {
          this.toast.add({ severity: 'success', summary: 'Ticket actualizado' });
          this.refrescar();
        },
      });
  }

  private refrescar() {
    forkJoin({
      ticket: this.tickets.obtener(this.id),
      historial: this.tickets.historial(this.id),
    })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (r) => this.aplicarTicket(r.ticket, r.historial),
        error: (e) => this.error.set(this.mensajeError(e)),
      });
  }

  private aplicarTicket(t: TicketDetalle, h: Historial[]) {
    this.ticket.set(t);
    this.historial.set(h);
    this.responsableId.set(t.responsable_id ?? null);
    this.nuevoEstado.set(null);
  }

  private mensajeError(e: unknown): string {
    if (e instanceof HttpErrorResponse) {
      if (e.status === 0) return 'No se pudo conectar con la API.';
      if (typeof e.error?.detail === 'string') return e.error.detail;
    }
    return 'Ocurrió un error inesperado.';
  }

  severidadEstado(estado: string): Severidad {
    const mapa: Record<string, Severidad> = {
      'Nuevo': 'info',
      'En proceso': 'warn',
      'Resuelto': 'success',
      'Cerrado': 'secondary',
    };
    return mapa[estado] ?? 'secondary';
  }

  severidadPrioridad(prioridad: string): Severidad {
    const mapa: Record<string, Severidad> = {
      'Alta': 'danger',
      'Media': 'warn',
      'Baja': 'success',
    };
    return mapa[prioridad] ?? 'secondary';
  }
}