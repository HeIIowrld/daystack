"use client";

import { useState, useEffect } from "react";
import {
  addScheduleItem,
  deleteScheduleItem,
  fetchSchedule,
  updateScheduleItem,
} from "@/lib/api";
import { ScheduleItem } from "@/lib/types";

export function ScheduleManager() {
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState<Partial<ScheduleItem>>({
    name: "",
    location: "",
    start_time: "",
    end_time: "",
  });

  useEffect(() => {
    loadSchedule();
  }, []);

  const loadSchedule = async () => {
    try {
      setLoading(true);
      const data = await fetchSchedule();
      setSchedule(data);
    } catch (error) {
      console.error("Failed to load schedule:", error);
      alert("Failed to load schedule. Please check if the API server is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!formData.name) {
      alert("Please enter a name for the schedule item");
      return;
    }

    try {
      const newItem = await addScheduleItem(formData as ScheduleItem);
      setSchedule([...schedule, newItem].sort((a, b) => {
        const aTime = a.start_time || a.end_time || "";
        const bTime = b.start_time || b.end_time || "";
        return aTime.localeCompare(bTime);
      }));
      setFormData({ name: "", location: "", start_time: "", end_time: "" });
      setShowAddForm(false);
    } catch (error: any) {
      alert(`Failed to add schedule item: ${error.message}`);
    }
  };

  const handleUpdate = async (id: string) => {
    if (!formData.name) {
      alert("Please enter a name for the schedule item");
      return;
    }

    try {
      const updated = await updateScheduleItem(id, formData as ScheduleItem);
      setSchedule(
        schedule
          .map((item) => (item.id === id ? updated : item))
          .sort((a, b) => {
            const aTime = a.start_time || a.end_time || "";
            const bTime = b.start_time || b.end_time || "";
            return aTime.localeCompare(bTime);
          })
      );
      setEditingId(null);
      setFormData({ name: "", location: "", start_time: "", end_time: "" });
    } catch (error: any) {
      alert(`Failed to update schedule item: ${error.message}`);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this schedule item?")) {
      return;
    }

    try {
      await deleteScheduleItem(id);
      setSchedule(schedule.filter((item) => item.id !== id));
    } catch (error: any) {
      alert(`Failed to delete schedule item: ${error.message}`);
    }
  };

  const startEdit = (item: ScheduleItem) => {
    setEditingId(item.id || null);
    setFormData({
      name: item.name,
      location: item.location || "",
      start_time: item.start_time || "",
      end_time: item.end_time || "",
    });
    setShowAddForm(false);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setShowAddForm(false);
    setFormData({ name: "", location: "", start_time: "", end_time: "" });
  };

  if (loading) {
    return (
      <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
        <p className="text-zinc-600">Loading schedule...</p>
      </section>
    );
  }

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white/70 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-zinc-900">Manage Schedule</h2>
        <button
          onClick={() => {
            cancelEdit();
            setShowAddForm(!showAddForm);
          }}
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
        >
          {showAddForm ? "Cancel" : "+ Add Item"}
        </button>
      </div>

      {showAddForm && (
        <div className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50/50 p-4">
          <h3 className="mb-3 text-sm font-semibold text-emerald-900">Add New Schedule Item</h3>
          <div className="grid gap-3 md:grid-cols-2">
            <div>
              <label className="block text-xs font-medium text-zinc-700 mb-1">
                Name *
              </label>
              <input
                type="text"
                value={formData.name || ""}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                placeholder="e.g., 오전 수업"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-700 mb-1">
                Location
              </label>
              <input
                type="text"
                value={formData.location || ""}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                placeholder="e.g., 연세로 50"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-700 mb-1">
                Start Time
              </label>
              <input
                type="time"
                value={formData.start_time || ""}
                onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-700 mb-1">
                End Time
              </label>
              <input
                type="time"
                value={formData.end_time || ""}
                onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
            </div>
          </div>
          <div className="mt-3 flex gap-2">
            <button
              onClick={handleAdd}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
            >
              Add
            </button>
            <button
              onClick={cancelEdit}
              className="rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 transition-colors hover:bg-zinc-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {schedule.length === 0 ? (
          <p className="text-sm text-zinc-500">No schedule items. Add one to get started!</p>
        ) : (
          schedule.map((item) => (
            <div
              key={item.id}
              className="rounded-xl border border-zinc-100 bg-zinc-50/60 px-4 py-3"
            >
              {editingId === item.id ? (
                <div className="space-y-3">
                  <div className="grid gap-3 md:grid-cols-2">
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 mb-1">
                        Name *
                      </label>
                      <input
                        type="text"
                        value={formData.name || ""}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 mb-1">
                        Location
                      </label>
                      <input
                        type="text"
                        value={formData.location || ""}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                        className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 mb-1">
                        Start Time
                      </label>
                      <input
                        type="time"
                        value={formData.start_time || ""}
                        onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                        className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 mb-1">
                        End Time
                      </label>
                      <input
                        type="time"
                        value={formData.end_time || ""}
                        onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                        className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => item.id && handleUpdate(item.id)}
                      className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-700"
                    >
                      Save
                    </button>
                    <button
                      onClick={cancelEdit}
                      className="rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 transition-colors hover:bg-zinc-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-zinc-500">
                      {item.start_time && item.end_time
                        ? `${item.start_time} - ${item.end_time}`
                        : item.start_time
                        ? `${item.start_time} -`
                        : item.end_time
                        ? `- ${item.end_time}`
                        : "Time TBD"}
                    </p>
                    <p className="text-base font-semibold text-zinc-900">{item.name}</p>
                    {item.location && (
                      <p className="text-sm text-zinc-500">{item.location}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => startEdit(item)}
                      className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-xs font-semibold text-zinc-700 transition-colors hover:bg-zinc-50"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => item.id && handleDelete(item.id)}
                      className="rounded-lg border border-rose-300 bg-white px-3 py-1.5 text-xs font-semibold text-rose-700 transition-colors hover:bg-rose-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </section>
  );
}

