import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { AvatarModule } from 'primeng/avatar';
import { TagModule } from 'primeng/tag';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ButtonModule, AvatarModule, TagModule],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.css',
})
export class LayoutComponent {
  version = environment.version;

  // Usuario fijo por ahora; cuando haya login vendrá de un servicio
  usuario = { nombre: 'Usuario Demo', rol: 'Soporte TI' };

  // Pantallas principales del menú lateral
  menu = [
    { label: 'Tickets', icono: 'pi pi-list', ruta: '/tickets' },
    { label: 'Nuevo ticket', icono: 'pi pi-plus-circle', ruta: '/tickets/nuevo' },
  ];

  cerrarSesion() {
    // Solo visual 
  }

  get iniciales(): string {
    return this.usuario.nombre
      .split(' ')
      .map((p) => p[0])
      .join('')
      .slice(0, 2)
      .toUpperCase();
  }
}
