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
  coordinates?: Coordinates;
};

export type TodoItem = {
  task: string;
  estimated_time: number;
  deadline?: string;
  course?: string;
  link?: string;
  source?: string;
};

export type SchedulerMeta = {
  config_ready: boolean;
  travel_time_buffer: number;
};

export type CampusBreakdown = {
  location: string;
  count: number;
};

export type ScheduleInsights = {
  total_tasks: number;
  scheduled_tasks: number;
  remaining_tasks: number;
  campus_breakdown: CampusBreakdown[];
};

export type OptimizeResponse = {
  schedule: ScheduleItem[];
  todos: TodoItem[];
  optimized_schedule: ScheduleItem[];
  remaining_todos: TodoItem[];
  meta: SchedulerMeta;
  insights: ScheduleInsights;
};
