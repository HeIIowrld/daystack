export type Coordinates = {
  lat: number;
  lng: number;
};

export type ScheduleItem = {
  name: string;
  location?: string;
  start_time?: string;
  end_time?: string;
  type?: string;
<<<<<<< HEAD
  coordinates?: Coordinates;
=======
  coordinates?: Coordinates | null;
>>>>>>> 5a1bfb6 (scheduling algorithm)
};

export type TodoItem = {
  task: string;
  estimated_time: number;
  deadline?: string;
  course?: string;
};

export type SchedulerMeta = {
  config_ready: boolean;
  travel_time_buffer: number;
};

export type OptimizeResponse = {
  schedule: ScheduleItem[];
  todos: TodoItem[];
  optimized_schedule: ScheduleItem[];
  remaining_todos: TodoItem[];
  meta: SchedulerMeta;
};
