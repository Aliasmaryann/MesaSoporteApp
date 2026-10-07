export interface TicketResumen {
  id: number;
  titulo: string;
  descripcion: string;   // nuevo
  fecha_creacion: string;
  categoria: string;
  prioridad: string;
  estado: string;
  responsable: string | null;
  solicitante: string;
}

export interface TicketDetalle {
  id: number;
  titulo: string;
  descripcion: string;
  fecha_creacion: string;
  fecha_cierre: string | null;
  solicitante_id: number;
  solicitante: string;
  responsable_id: number | null;
  responsable: string | null;
  categoria_id: number;
  categoria: string;
  prioridad_id: number;
  prioridad: string;
  estado_id: number;
  estado: string;
}

export interface NuevoTicket {
  solicitante_id: number;
  titulo: string;
  descripcion: string;
  categoria_id: number;
  prioridad_id: number;
}

export type Transiciones = Record<string, string[]>;
