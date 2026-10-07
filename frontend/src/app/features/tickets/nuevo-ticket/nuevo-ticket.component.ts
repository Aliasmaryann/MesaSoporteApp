import { Component, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { HttpErrorResponse } from '@angular/common/http';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';
import { SelectModule } from 'primeng/select';
import { MessageModule } from 'primeng/message';
import { TicketService } from '../../../core/services/ticket.service';
import { CatalogoService } from '../../../core/services/catalogo.service';
import { NuevoTicket } from '../../../core/models/ticket';
import { Card } from 'primeng/card';

@Component({
  selector: 'app-nuevo-ticket',
  imports: [
    ReactiveFormsModule,
    RouterLink,
    ButtonModule,
    InputTextModule,
    TextareaModule,
    SelectModule,
    MessageModule,
    Card
],
  templateUrl: './nuevo-ticket.component.html',
  styleUrl: './nuevo-ticket.component.css',
})
export class NuevoTicketComponent {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private messages = inject(MessageService);
  private ticketService = inject(TicketService);
  private catalogoService = inject(CatalogoService);

  catalogos = toSignal(this.catalogoService.catalogos$);

  guardando = signal(false);
  error = signal<string | null>(null);

  // Validators.pattern(/\S/) evita títulos o descripciones de solo espacios
  form = this.fb.group({
    solicitante_id: [null as number | null, Validators.required],
    titulo: ['', [Validators.required, Validators.pattern(/\S/)]],
    descripcion: ['', [Validators.required, Validators.pattern(/\S/)]],
    categoria_id: [null as number | null, Validators.required],
    prioridad_id: [null as number | null, Validators.required],
  });

  // Mostrar el error de un campo solo si ya lo tocaron o intentaron guardar
  invalido(campo: keyof typeof this.form.controls): boolean {
    const c = this.form.controls[campo];
    return c.invalid && (c.touched || c.dirty);
  }

  guardar() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const v = this.form.getRawValue();
    const ticket: NuevoTicket = {
      solicitante_id: v.solicitante_id!,
      titulo: v.titulo!.trim(),
      descripcion: v.descripcion!.trim(),
      categoria_id: v.categoria_id!,
      prioridad_id: v.prioridad_id!,
    };

    this.error.set(null);
    this.guardando.set(true);

    this.ticketService.crear(ticket).subscribe({
      next: ({ id }) => {
        this.messages.add({
          severity: 'success',
          summary: 'Ticket creado',
          detail: `Se registró el ticket #${id}.`,
        });
        this.router.navigate(['/tickets', id]);
      },
      error: (e: HttpErrorResponse) => {
        this.guardando.set(false);
        if (e.status === 0) {
          this.error.set('No se pudo conectar con la API.');
        } else if (typeof e.error?.detail === 'string') {
          this.error.set(e.error.detail);
        } else {
          this.error.set('Los datos enviados no son válidos.');
        }
      },
    });
  }
}