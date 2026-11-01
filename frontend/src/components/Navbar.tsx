
"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Armchair,
  LayoutDashboard,
  LogIn,
  LogOut,
  User,
  UserPlus,
  FolderOpen,
} from "lucide-react";

import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  const linkClass = (path: string) =>
    `flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition ${
      pathname === path
        ? "bg-amber-100 text-amber-900"
        : "text-slate-600 hover:bg-stone-100 hover:text-slate-900"
    }`;

  return (
    <header className="sticky top-0 z-50 border-b border-stone-200 bg-white/95 shadow-sm backdrop-blur">
      <nav className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-5 py-4 sm:px-8">
        {/* BRAND */}
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
            <Armchair size={22} />
          </div>

          <div>
            <h1 className="text-base font-bold tracking-tight text-slate-900 sm:text-lg">
              AI Home Decorator
            </h1>
            <p className="hidden text-xs text-slate-500 sm:block">
              Design your space intelligently
            </p>
          </div>
        </Link>

        {/* NAVIGATION */}
        <div className="flex w-full flex-wrap items-center justify-center gap-1 sm:w-auto sm:justify-end sm:gap-2">
          {isLoading ? (
            <span className="px-3 py-2 text-sm text-slate-400">
              Loading...
            </span>
          ) : isAuthenticated ? (
            <>
              <Link href="/dashboard" className={linkClass("/dashboard")}>
                <LayoutDashboard size={17} />
                <span>Dashboard</span>
              </Link>

              <Link href="/designs" className={linkClass("/designs")}>
                <FolderOpen size={17} />
                <span>My Designs</span>
              </Link>

              <Link href="/profile" className={linkClass("/profile")}>
                <User size={17} />
                <span>Profile</span>
              </Link>

              <button
                type="button"
                onClick={handleLogout}
                className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-red-600 transition hover:bg-red-50"
              >
                <LogOut size={17} />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className={linkClass("/login")}>
                <LogIn size={17} />
                <span>Login</span>
              </Link>

              <Link
                href="/signup"
                className="flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
              >
                <UserPlus size={17} />
                <span>Sign Up</span>
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
