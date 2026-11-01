
"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  User,
  Mail,
  CalendarDays,
  ShieldCheck,
  LogOut,
  Loader2,
  Palette,
} from "lucide-react";

import { useAuth } from "@/context/AuthContext";

export default function ProfilePage() {
  const router = useRouter();

  const { user, isLoading, isAuthenticated, logout } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

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
            href="/dashboard"
            className="flex items-center gap-2 rounded-xl border border-stone-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-stone-100"
          >
            <ArrowLeft className="h-4 w-4" />
            Dashboard
          </Link>
        </div>
      </header> */}

      <div className="mx-auto max-w-4xl px-5 py-10 lg:px-8">
        {/* Page heading */}
        <div className="mb-8">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-emerald-700">
            <User className="h-4 w-4" />
            ACCOUNT SETTINGS
          </div>

          <h2 className="text-3xl font-bold tracking-tight text-slate-900">
            My Profile
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            View your account information and manage your account.
          </p>
        </div>

        {/* Profile card */}
        <section className="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
          <div className="bg-gradient-to-r from-emerald-800 to-emerald-600 px-6 py-9 sm:px-8">
            <div className="flex flex-col items-center gap-4 sm:flex-row">
              <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-white/20 bg-white/15 text-white">
                <User className="h-10 w-10" />
              </div>

              <div className="text-center sm:text-left">
                <h3 className="text-2xl font-bold text-white">
                  {user.full_name}
                </h3>
                <p className="mt-1 text-sm text-emerald-50">
                  {user.email}
                </p>
                <span className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold text-white">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  {user.is_active ? "Active Account" : "Inactive Account"}
                </span>
              </div>
            </div>
          </div>

          <div className="p-6 sm:p-8">
            <h3 className="mb-6 text-lg font-bold text-slate-900">
              Personal Information
            </h3>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div className="rounded-xl border border-stone-200 p-4">
                <div className="mb-3 flex items-center gap-2 text-slate-400">
                  <User className="h-4 w-4" />
                  <span className="text-xs font-semibold uppercase tracking-wide">
                    Full Name
                  </span>
                </div>

                <p className="break-words font-semibold text-slate-800">
                  {user.full_name}
                </p>
              </div>

              <div className="rounded-xl border border-stone-200 p-4">
                <div className="mb-3 flex items-center gap-2 text-slate-400">
                  <Mail className="h-4 w-4" />
                  <span className="text-xs font-semibold uppercase tracking-wide">
                    Email Address
                  </span>
                </div>

                <p className="break-all font-semibold text-slate-800">
                  {user.email}
                </p>
              </div>

              <div className="rounded-xl border border-stone-200 p-4">
                <div className="mb-3 flex items-center gap-2 text-slate-400">
                  <CalendarDays className="h-4 w-4" />
                  <span className="text-xs font-semibold uppercase tracking-wide">
                    Member Since
                  </span>
                </div>

                <p className="font-semibold text-slate-800">
                  {new Date(user.created_at).toLocaleDateString(undefined, {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </div>

              <div className="rounded-xl border border-stone-200 p-4">
                <div className="mb-3 flex items-center gap-2 text-slate-400">
                  <ShieldCheck className="h-4 w-4" />
                  <span className="text-xs font-semibold uppercase tracking-wide">
                    Account Status
                  </span>
                </div>

                <p
                  className={`font-semibold ${
                    user.is_active ? "text-emerald-700" : "text-red-600"
                  }`}
                >
                  {user.is_active ? "Active" : "Inactive"}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Quick links */}
        <section className="mt-7 rounded-2xl border border-stone-200 bg-white p-6 shadow-sm sm:p-8">
          <h3 className="mb-5 text-lg font-bold text-slate-900">
            Your Workspace
          </h3>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Link
              href="/dashboard"
              className="flex items-center justify-between rounded-xl border border-stone-200 p-4 transition hover:border-emerald-300 hover:bg-emerald-50"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                  <Palette className="h-5 w-5 text-emerald-700" />
                </div>

                <div>
                  <p className="font-semibold text-slate-800">Dashboard</p>
                  <p className="text-xs text-slate-500">
                    View your workspace
                  </p>
                </div>
              </div>

              <ArrowLeft className="h-4 w-4 rotate-180 text-slate-400" />
            </Link>

            <Link
              href="/designs"
              className="flex items-center justify-between rounded-xl border border-stone-200 p-4 transition hover:border-emerald-300 hover:bg-emerald-50"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-100">
                  <Palette className="h-5 w-5 text-amber-700" />
                </div>

                <div>
                  <p className="font-semibold text-slate-800">My Designs</p>
                  <p className="text-xs text-slate-500">
                    Explore saved designs
                  </p>
                </div>
              </div>

              <ArrowLeft className="h-4 w-4 rotate-180 text-slate-400" />
            </Link>
          </div>
        </section>

        {/* Logout */}
        <section className="mt-7 rounded-2xl border border-red-100 bg-white p-6 shadow-sm">
          <h3 className="font-bold text-slate-900">Sign Out</h3>

          <p className="mt-2 text-sm text-slate-500">
            Sign out of your account on this device.
          </p>

          <button
            onClick={handleLogout}
            className="mt-5 inline-flex items-center gap-2 rounded-xl bg-red-50 px-5 py-3 text-sm font-semibold text-red-600 transition hover:bg-red-100"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </section>
      </div>
    </main>
  );
}
