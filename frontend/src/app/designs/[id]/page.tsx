
"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  CalendarDays,
  Loader2,
  Palette,
  Trash2,
} from "lucide-react";

import { useAuth } from "@/context/AuthContext";
import api from "@/services/api";

type DesignData = Record<string, unknown>;

function formatLabel(value: string) {
  return value
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[_-]/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function ValueDisplay({ value }: { value: unknown }): ReactNode {
  if (value === null || value === undefined) {
    return <span className="text-slate-400">Not provided</span>;
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (typeof value === "string" || typeof value === "number") {
    return String(value);
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span className="text-slate-400">No items</span>;
    }

    return (
      <ul className="space-y-2">
        {value.map((item, index) => (
          <li
            key={index}
            className="rounded-lg bg-stone-50 px-3 py-2 text-sm text-slate-700"
          >
            <ValueDisplay value={item} />
          </li>
        ))}
      </ul>
    );
  }

  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);

    if (entries.length === 0) {
      return <span className="text-slate-400">No data</span>;
    }

    return (
      <div className="space-y-3">
        {entries.map(([key, item]) => (
          <div key={key} className="min-w-0">
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
              {formatLabel(key)}
            </p>
            <div className="break-words text-sm leading-6 text-slate-700">
              <ValueDisplay value={item} />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return String(value);
}

export default function DesignDetailsPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const designId = params.id;

  const { isLoading, isAuthenticated } = useAuth();

  const [design, setDesign] = useState<DesignData | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");

  const fetchDesign = useCallback(async () => {
    if (!isAuthenticated || !designId) return;

    try {
      setLoading(true);
      setError("");

      const response = await api.get<DesignData>(
        `/api/designs/${designId}`
      );

      setDesign(response.data);
    } catch (err: unknown) {
      const message =
        typeof err === "object" &&
        err !== null &&
        "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail
          : undefined;

      setError(
        typeof message === "string"
          ? message
          : "Unable to load this design. It may have been deleted or may not exist."
      );
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, designId]);

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    fetchDesign();
  }, [isLoading, isAuthenticated, fetchDesign, router]);

  async function handleDelete() {
    const confirmed = window.confirm(
      "Are you sure you want to permanently delete this design?"
    );

    if (!confirmed) return;

    try {
      setDeleting(true);
      setError("");

      await api.delete(`/api/designs/${designId}`);

      router.push("/designs");
    } catch {
      setError("Unable to delete this design. Please try again.");
      setDeleting(false);
    }
  }

  if (isLoading || !isAuthenticated || loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-stone-50">
        <div className="text-center">
          <Loader2 className="mx-auto h-9 w-9 animate-spin text-emerald-700" />
          <p className="mt-3 text-sm text-slate-500">
            Loading design details...
          </p>
        </div>
      </main>
    );
  }

  if (error && !design) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-stone-50 px-5">
        <div className="w-full max-w-md rounded-2xl border border-stone-200 bg-white p-8 text-center shadow-sm">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-red-50">
            <Palette className="h-7 w-7 text-red-500" />
          </div>

          <h2 className="mt-5 text-xl font-bold text-slate-900">
            Design Not Available
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-500">
            {error}
          </p>

          <Link
            href="/designs"
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-sm font-semibold text-white hover:bg-emerald-800"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to My Designs
          </Link>
        </div>
      </main>
    );
  }

  if (!design) return null;

  const excludedFields = new Set([
    "id",
    "created_at",
    "updated_at",
    "room_type",
  ]);

  const detailEntries = Object.entries(design).filter(
    ([key]) => !excludedFields.has(key)
  );

  return (
    <main className="min-h-screen bg-stone-50">
      {/* Header */}
      {/* <header className="border-b border-stone-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
          <Link href="/dashboard" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100">
              <span className="text-xl">🏡</span>
            </div>

            <div>
              <h1 className="text-lg font-bold text-slate-900">
                AI Home Decorator
              </h1>
              <p className="text-xs text-slate-500">Your design workspace</p>
            </div>
          </Link>

          <Link
            href="/designs"
            className="flex items-center gap-2 rounded-xl border border-stone-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-stone-100"
          >
            <ArrowLeft className="h-4 w-4" />
            My Designs
          </Link>
        </div>
      </header> */}

      <div className="mx-auto max-w-5xl px-5 py-10 lg:px-8">
        {/* Heading */}
        <div className="mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
          <div>
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-emerald-700">
              <Palette className="h-4 w-4" />
              YOUR SAVED DESIGN
            </div>

            <h2 className="text-3xl font-bold capitalize tracking-tight text-slate-900">
              {String(design.room_type || "Room Design")}
            </h2>

            <div className="mt-3 flex items-center gap-2 text-sm text-slate-500">
              <CalendarDays className="h-4 w-4" />
              {design.created_at
                ? new Date(String(design.created_at)).toLocaleString()
                : "Creation date unavailable"}
            </div>
          </div>

          <button
            onClick={handleDelete}
            disabled={deleting}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-red-200 bg-white px-4 py-3 text-sm font-semibold text-red-600 transition hover:bg-red-50 disabled:opacity-50"
          >
            {deleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
            Delete Design
          </button>
        </div>

        {error && (
          <div
            role="alert"
            className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        {/* Design information */}
        {detailEntries.length === 0 ? (
          <div className="rounded-2xl border border-stone-200 bg-white p-8 text-center">
            <p className="text-sm text-slate-500">
              No additional design information is available.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {detailEntries.map(([key, value]) => (
              <section
                key={key}
                className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm sm:p-8"
              >
                <h3 className="mb-5 border-b border-stone-100 pb-4 text-lg font-bold text-slate-900">
                  {formatLabel(key)}
                </h3>

                <ValueDisplay value={value} />
              </section>
            ))}
          </div>
        )}

        <div className="mt-8">
          <Link
            href="/designs"
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-800"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to My Designs
          </Link>
        </div>
      </div>
    </main>
  );
}
