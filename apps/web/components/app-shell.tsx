"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

import { apiRequest, ApiError, User } from "@/lib/api";
import { Button, Notice } from "@/components/ui";

export function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadSession() {
    setLoading(true);
    setError("");
    try {
      setUser(await apiRequest<User>("/auth/session"));
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) {
        router.replace(`/login?next=${encodeURIComponent(pathname)}`);
        return;
      }
      setError(reason instanceof ApiError ? reason.message : "Could not load your account.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    apiRequest<User>("/auth/session")
      .then((session) => {
        if (active) {
          setUser(session);
          setError("");
        }
      })
      .catch((reason: unknown) => {
        if (!active) return;
        if (reason instanceof ApiError && reason.status === 401) {
          router.replace(`/login?next=${encodeURIComponent(pathname)}`);
        } else {
          setError(reason instanceof ApiError ? reason.message : "Could not load your account.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [pathname, router]);

  async function logout() {
    setError("");
    try {
      await apiRequest<void>("/auth/logout", { method: "POST" });
      router.replace("/login");
      router.refresh();
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Could not sign out. Retry.");
    }
  }

  if (loading) {
    return <main className="p-8" aria-live="polite">Loading your study space…</main>;
  }
  if (!user) {
    return (
      <main className="mx-auto max-w-xl p-8">
        <Notice>{error || "Your session could not be loaded."}</Notice>
        <Button className="mt-4" onClick={() => void loadSession()}>Retry</Button>
      </main>
    );
  }

  return (
    <div className="min-h-screen md:grid md:grid-cols-[240px_1fr]">
      <aside className="border-b border-slate-200 bg-white p-5 md:border-b-0 md:border-r">
        <Link className="text-lg font-semibold text-ink no-underline" href="/app/library">
          Study Platform
        </Link>
        <nav className="mt-8 grid gap-2" aria-label="Main navigation">
          <Link className="rounded-lg px-3 py-2 hover:bg-paper" href="/app/library">Library</Link>
          <Link className="rounded-lg px-3 py-2 hover:bg-paper" href="/app/settings/profile">Profile</Link>
        </nav>
        <div className="mt-8 border-t border-slate-200 pt-4">
          <p className="truncate text-sm font-medium">{user.display_name}</p>
          <p className="truncate text-xs text-slate-500">{user.email}</p>
          <Button className="mt-4 w-full bg-slate-800 hover:bg-slate-700" onClick={() => void logout()}>
            Sign out
          </Button>
          {error && <p className="mt-3 text-sm text-red-800" role="alert">{error}</p>}
        </div>
      </aside>
      <main className="min-w-0 px-5 py-8 md:px-10">{children}</main>
    </div>
  );
}
