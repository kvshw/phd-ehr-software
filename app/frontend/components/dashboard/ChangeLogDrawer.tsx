"use client";

import { useState, useEffect } from "react";

interface ChangeLogEntry {
  id: string;
  type: string;
  feature?: string;
  time: string;
  confidence: number;
  explanation: string;
  was_rolled_back: boolean;
}

interface DayGroup {
  date: string;
  changes: ChangeLogEntry[];
}

interface ChangeLogDrawerProps {
  trigger?: React.ReactNode;
  className?: string;
}

/**
 * ChangeLogDrawer Component
 * 
 * Shows history of MAPE-K adaptations with full transparency.
 * Users can see what changed, when, and why.
 */
export function ChangeLogDrawer({ className }: ChangeLogDrawerProps) {
  const [open, setOpen] = useState(false);
  const [changeLog, setChangeLog] = useState<DayGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [periodDays, setPeriodDays] = useState<number>(30);

  useEffect(() => {
    if (open) {
      fetchChangeLog();
    }
  }, [open, periodDays]);

  const fetchChangeLog = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/assurance/logs/me?days=${periodDays}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setChangeLog(data.change_log || []);
      }
    } catch (error) {
      console.error("Error fetching change log:", error);
    } finally {
      setLoading(false);
    }
  };

  const totalChanges = changeLog.reduce(
    (sum, day) => sum + day.changes.length,
    0
  );

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setOpen(true)}
        className={`inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 ${className || ""}`}
      >
        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Change Log
      </button>

      {/* Drawer */}
      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40 bg-black/50"
            onClick={() => setOpen(false)}
          />
          
          {/* Drawer Content */}
          <div className="fixed right-0 top-0 z-50 h-full w-full max-w-md bg-white shadow-xl flex flex-col">
            {/* Header */}
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Adaptation History
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">
                    See how your dashboard has been personalized
                  </p>
                </div>
                <button
                  onClick={() => setOpen(false)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Filters */}
            <div className="p-4 border-b flex items-center justify-between">
              <span className="text-sm text-gray-500">
                {totalChanges} change{totalChanges !== 1 ? "s" : ""} found
              </span>
              <select
                value={periodDays}
                onChange={(e) => setPeriodDays(parseInt(e.target.value))}
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
              </select>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto p-4">
              {loading ? (
                <div className="flex items-center justify-center h-40">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
                </div>
              ) : changeLog.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-40 text-gray-500">
                  <svg className="w-12 h-12 mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p>No adaptations found</p>
                  <p className="text-sm">Your dashboard will adapt as you use it</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {changeLog.map((dayGroup) => (
                    <div key={dayGroup.date}>
                      <h3 className="text-sm font-medium text-gray-500 mb-3">
                        {formatDate(dayGroup.date)}
                      </h3>
                      <div className="space-y-3">
                        {dayGroup.changes.map((change) => (
                          <ChangeLogItem key={change.id} change={change} />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t bg-gray-50">
              <p className="text-xs text-gray-500 text-center">
                Adaptations are made automatically based on your usage patterns.
              </p>
            </div>
          </div>
        </>
      )}
    </>
  );
}

function ChangeLogItem({ change }: { change: ChangeLogEntry }) {
  return (
    <div
      className={`rounded-lg border p-3 ${
        change.was_rolled_back
          ? "bg-red-50 border-red-200"
          : "bg-white hover:bg-gray-50"
      }`}
    >
      <div className="flex items-start gap-3">
        <div
          className={`rounded-full p-2 ${
            change.was_rolled_back
              ? "bg-red-100"
              : "bg-blue-100"
          }`}
        >
          <svg
            className={`w-4 h-4 ${
              change.was_rolled_back ? "text-red-600" : "text-blue-600"
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"
            />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
              {formatType(change.type)}
            </span>
            {change.feature && (
              <span className="text-sm font-medium truncate">
                {change.feature}
              </span>
            )}
            {change.was_rolled_back && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                Rolled back
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600">{change.explanation}</p>
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
            <span>{formatTime(change.time)}</span>
            <span className="flex items-center gap-1">
              {Math.round(change.confidence * 100)}% confidence
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatType(type: string): string {
  const labels: Record<string, string> = {
    dashboard_layout: "Layout",
    feature_promotion: "Promotion",
    suggestion_density: "Suggestions",
    alert_threshold: "Alerts",
    section_order: "Reorder",
  };

  if (type.startsWith("rollback_")) {
    return "Rollback";
  }

  return labels[type] || type.replace(/_/g, " ");
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (dateString === today.toISOString().split("T")[0]) {
    return "Today";
  }
  if (dateString === yesterday.toISOString().split("T")[0]) {
    return "Yesterday";
  }

  return date.toLocaleDateString("en-US", {
    weekday: "long",
    month: "short",
    day: "numeric",
  });
}

function formatTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

export default ChangeLogDrawer;
