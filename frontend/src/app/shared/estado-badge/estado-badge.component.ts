import { Component, computed, input } from '@angular/core';
import { TagModule } from 'primeng/tag';

type Severidad = 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast';

const MAPA: Record<string, Severidad> = {
  'Nuevo': 'info',
  'En proceso': 'warn',
  'Resuelto': 'success',
  'Cerrado': 'secondary',
};

@Component({
  selector: 'app-estado-badge',
  imports: [TagModule],
  template: `<p-tag [value]="estado()" [severity]="severidad()" />`,
})
export class EstadoBadgeComponent {
  estado = input.required<string>();
  severidad = computed<Severidad>(() => MAPA[this.estado()] ?? 'secondary');
}