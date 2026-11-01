
"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  FolderOpen,
  Loader2,
  Palette,
  RefreshCw,
  Trash2,
} from "lucide-react";

import { useAuth } from "@/context/AuthContext";
import api from "@/services/api";

interface Design {
  id: string;
  room_type: string;
  design_input: Record<string, unknown>;
  design_result: Record<string, unknown>;
  created_at: string;
}

interface DesignsResponse {
  items: Design[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const PAGE_SIZE = 9;

export default function DesignsPage() {
  const router = useRouter();
  const { isLoading, isAuthenticated } = useAuth();

  const [designs, setDesigns] = useState<Design[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);

  const [roomType, setRoomType] = useState("");
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  const fetchDesigns = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      setLoading(true);
      setError("");

      const response = await api.get<DesignsResponse>("/api/designs/", {
        params: {
          page,
          page_size: PAGE_SIZE,
          ...(roomType.trim() ? { room_type: roomType.trim() } : {}),
        },
      });

      setDesigns(response.data.items);
      setTotal(response.data.total);
      setTotalPages(response.data.total_pages);
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
          : "Unable to load your designs. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, page, roomType]);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      fetchDesigns();
    }
  }, [isLoading, isAuthenticated, fetchDesigns]);

  async function handleDelete(designId: string) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this design? This action cannot be undone."
    );

    if (!confirmed) return;

    try {
      setDeletingId(designId);
      setError("");
      setSuccess("");

      await api.delete(`/api/designs/${designId}`);

      setSuccess("Design deleted successfully.");

      // If the deleted design was the only item on this page,
      // move back to the previous page.
      if (designs.length === 1 && page > 1) {
        setPage((current) => current - 1);
      } else {
        await fetchDesigns();
      }
    } catch {
      setError("Unable to delete this design. Please try again.");
    } finally {
      setDeletingId(null);
    }
  }

  function handleFilterChange(value: string) {
    setRoomType(value);
    setPage(1);
    setSuccess("");
  }

  if (isLoading || !isAuthenticated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-stone-50">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-700" />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="border-b border-stone-200 bg-white">
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
            href="/dashboard"
            className="flex items-center gap-2 rounded-xl border border-stone-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-stone-100"
          >
            <ArrowLeft className="h-4 w-4" />
            Dashboard
          </Link>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-5 py-10 lg:px-8">
        {/* Page heading */}
        <div className="mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-emerald-700">
              <Palette className="h-4 w-4" />
              YOUR CREATIVE COLLECTION
            </div>

            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              My Designs
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              View and manage your previously generated room designs.
            </p>
          </div>

          <Link
            href="/"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-800"
          >
            <Palette className="h-4 w-4" />
            Create New Design
          </Link>
        </div>

        {/* Statistics and filter */}
        <section className="mb-7 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100">
              <FolderOpen className="h-6 w-6 text-emerald-700" />
            </div>

            <div>
              <p className="text-xs font-medium text-slate-500">
                Total Saved Designs
              </p>
              <p className="text-2xl font-bold text-slate-900">
                {total}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <input
              type="text"
              value={roomType}
              onChange={(e) => handleFilterChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  setPage(1);
                  fetchDesigns();
                }
              }}
              placeholder="Filter by room type..."
              className="min-w-0 flex-1 rounded-xl border border-stone-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 sm:w-64 sm:flex-none"
            />

            <button
              onClick={() => fetchDesigns()}
              disabled={loading}
              className="flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition hover:bg-stone-100 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </section>

        {/* Messages */}
        {error && (
          <div
            role="alert"
            className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        {success && (
          <div
            role="status"
            className="mb-6 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
          >
            {success}
          </div>
        )}

        {/* Designs */}
        {loading ? (
          <div className="flex min-h-64 items-center justify-center">
            <div className="text-center">
              <Loader2 className="mx-auto h-9 w-9 animate-spin text-emerald-700" />
              <p className="mt-3 text-sm text-slate-500">
                Loading your designs...
              </p>
            </div>
          </div>
        ) : designs.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-stone-300 bg-white px-6 py-16 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-stone-100">
              <FolderOpen className="h-8 w-8 text-slate-400" />
            </div>

            <h3 className="mt-5 text-xl font-bold text-slate-900">
              {roomType.trim()
                ? "No matching designs found"
                : "No saved designs yet"}
            </h3>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              {roomType.trim()
                ? "Try another room type or clear your filter to see your designs."
                : "Your generated designs will appear here. Start by creating your first AI-powered room design."}
            </p>

            {roomType.trim() ? (
              <button
                onClick={() => handleFilterChange("")}
                className="mt-6 rounded-xl border border-stone-200 px-5 py-3 text-sm font-semibold text-slate-700 hover:bg-stone-100"
              >
                Clear Filter
              </button>
            ) : (
              <Link
                href="/"
                className="mt-6 inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-sm font-semibold text-white hover:bg-emerald-800"
              >
                <Palette className="h-4 w-4" />
                Create Your First Design
              </Link>
            )}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {designs.map((design) => (
                <article
                  key={design.id}
                  className="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
                >
                  <div className="flex h-36 items-center justify-center bg-gradient-to-br from-emerald-50 via-stone-100 to-amber-50">
                    <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/80 shadow-sm">
                      <Palette className="h-8 w-8 text-emerald-700" />
                    </div>
                  </div>

                  <div className="p-5">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="text-lg font-bold capitalize text-slate-900">
                          {design.room_type || "Room Design"}
                        </h3>

                        <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
                          <CalendarDays className="h-4 w-4" />
                          {new Date(design.created_at).toLocaleDateString(
                            undefined,
                            {
                              year: "numeric",
                              month: "short",
                              day: "numeric",
                            }
                          )}
                        </div>
                      </div>

                      <span className="rounded-lg bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                        Saved
                      </span>
                    </div>

                    <div className="mt-5 flex items-center justify-between border-t border-stone-100 pt-4">
                      <Link
                        href={`/designs/${design.id}`}
                        className="inline-flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:text-emerald-900"
                      >
                        View Details
                        <ArrowRight className="h-4 w-4" />
                      </Link>

                      <button
                        onClick={() => handleDelete(design.id)}
                        disabled={deletingId === design.id}
                        aria-label="Delete design"
                        title="Delete design"
                        className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-400 transition hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
                      >
                        {deletingId === design.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-9 flex flex-wrap items-center justify-between gap-4 border-t border-stone-200 pt-6">
                <p className="text-sm text-slate-500">
                  Page {page} of {totalPages} · {total} designs
                </p>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage((current) => current - 1)}
                    disabled={page <= 1}
                    className="flex items-center gap-1 rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Previous
                  </button>

                  <button
                    onClick={() => setPage((current) => current + 1)}
                    disabled={page >= totalPages}
                    className="flex items-center gap-1 rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Next
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}
