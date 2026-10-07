import { Component, computed, input } from '@angular/core';
import { TagModule } from 'primeng/tag';

type Severidad = 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast';

const MAPA: Record<string, Severidad> = {
  'Crítica': 'danger',
  'Alta': 'warn',
  'Media': 'secondary',
  'Baja': 'info',
};

@Component({
  selector: 'app-prioridad-badge',
  imports: [TagModule],
  template: `<p-tag [value]="prioridad()" [severity]="severidad()" />`,
})
export class PrioridadBadgeComponent {
  prioridad = input.required<string>();
  severidad = computed<Severidad>(() => MAPA[this.prioridad()] ?? 'secondary');
}