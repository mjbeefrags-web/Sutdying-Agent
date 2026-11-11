import Link from "next/link";
import type { ReactNode } from "react";

import { PageCard } from "@/components/ui";

export function AuthPage({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-12">
      <div className="w-full max-w-md">
        <Link className="text-sm font-medium text-teal no-underline" href="/">Study Platform</Link>
        <PageCard>
          <h1 className="text-3xl font-semibold text-ink">{title}</h1>
          <p className="mb-6 mt-2 text-slate-600">{description}</p>
          {children}
        </PageCard>
        <p className="mt-4 text-center text-xs text-slate-500">
          Your study materials are private to your account.
        </p>
      </div>
    </main>
  );
}
