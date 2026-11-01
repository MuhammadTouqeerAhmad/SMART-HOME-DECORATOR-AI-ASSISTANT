
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Palette,
  User,
  LogOut,
  Plus,
  Sparkles,
  FolderOpen,
  Loader2,
  ArrowRight,
} from "lucide-react";

import { useAuth } from "@/context/AuthContext";
import api from "@/services/api";

interface DesignsResponse {
  items: unknown[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading, isAuthenticated, logout } = useAuth();

  const [totalDesigns, setTotalDesigns] = useState<number | null>(null);
  const [designsLoading, setDesignsLoading] = useState(true);
  const [designsError, setDesignsError] = useState("");

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isLoading || !isAuthenticated) return;

    let isMounted = true;

    async function fetchDesignCount() {
      try {
        setDesignsLoading(true);
        setDesignsError("");

        const response = await api.get<DesignsResponse>("/api/designs/", {
          params: {
            page: 1,
            page_size: 1,
          },
        });

        if (isMounted) {
          setTotalDesigns(response.data.total);
        }
      } catch {
        if (isMounted) {
          setDesignsError("Unable to load your saved designs.");
        }
      } finally {
        if (isMounted) {
          setDesignsLoading(false);
        }
      }
    }

    fetchDesignCount();

    return () => {
      isMounted = false;
    };
  }, [isLoading, isAuthenticated]);

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  if (isLoading || !isAuthenticated || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-stone-50">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-700" />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-stone-50">
      {/* Navigation */}
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

          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-xl bg-stone-100 px-3 py-2 sm:flex">
              <User className="h-4 w-4 text-slate-500" />
              <span className="max-w-40 truncate text-sm font-medium text-slate-700">
                {user.full_name}
              </span>
            </div>

            <Link
                href="/profile"
                className="flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-stone-100"
                >
                <User className="h-4 w-4" />
                <span className="hidden sm:inline">Profile</span>
            </Link>

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-red-50 hover:text-red-600"
            >
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </header> */}

      <div className="mx-auto max-w-7xl px-5 py-10 lg:px-8">
        {/* Welcome section */}
        <section className="mb-10">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-emerald-700">
            <Sparkles className="h-4 w-4" />
            YOUR PERSONAL DESIGN SPACE
          </div>

          <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Welcome back, {user.full_name.split(" ")[0]}!
          </h2>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base">
            Ready to transform your space? Start a new design or explore your
            saved design history.
          </p>
        </section>

        {/* Statistics */}
        <section className="mb-10 grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">
                  Total Saved Designs
                </p>

                <div className="mt-3 text-3xl font-bold text-slate-900">
                  {designsLoading ? (
                    <Loader2 className="h-7 w-7 animate-spin text-emerald-700" />
                  ) : designsError ? (
                    <span className="text-base text-red-500">Unavailable</span>
                  ) : (
                    totalDesigns
                  )}
                </div>
              </div>

              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100">
                <FolderOpen className="h-6 w-6 text-emerald-700" />
              </div>
            </div>

            {designsError && (
              <p className="mt-3 text-xs text-red-500">{designsError}</p>
            )}
          </div>

          <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">
                  Account Status
                </p>

                <p className="mt-3 text-2xl font-bold text-emerald-700">
                  {user.is_active ? "Active" : "Inactive"}
                </p>
              </div>

              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100">
                <User className="h-6 w-6 text-emerald-700" />
              </div>
            </div>
          </div>
        </section>

        {/* Main actions */}
        <section>
          <h3 className="mb-5 text-xl font-bold text-slate-900">
            Get Started
          </h3>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            {/* Create design */}
            <div className="group rounded-2xl border border-stone-200 bg-white p-7 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100">
                <Plus className="h-6 w-6 text-emerald-700" />
              </div>

              <h4 className="text-lg font-bold text-slate-900">
                Create New Design
              </h4>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                Upload your room details, select your preferred style, and let
                AI generate personalized interior design recommendations.
              </p>

              <Link
                href="/"
                className="mt-6 inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-800"
              >
                Start Designing
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            {/* Design history */}
            <div className="group rounded-2xl border border-stone-200 bg-white p-7 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100">
                <Palette className="h-6 w-6 text-amber-700" />
              </div>

              <h4 className="text-lg font-bold text-slate-900">
                My Designs
              </h4>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                Explore your previously generated designs and revisit your
                saved room recommendations.
              </p>

              <Link
                href="/designs"
                className="mt-6 inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-800"
                >
                Explore My Designs
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* Account information */}
        <section className="mt-10 rounded-2xl border border-stone-200 bg-white p-6">
          <h3 className="mb-4 text-lg font-bold text-slate-900">
            Account Information
          </h3>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Full Name
              </p>
              <p className="mt-1 text-sm font-medium text-slate-700">
                {user.full_name}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Email Address
              </p>
              <p className="mt-1 break-all text-sm font-medium text-slate-700">
                {user.email}
              </p>
            </div>

            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Member Since
              </p>
              <p className="mt-1 text-sm font-medium text-slate-700">
                {new Date(user.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
