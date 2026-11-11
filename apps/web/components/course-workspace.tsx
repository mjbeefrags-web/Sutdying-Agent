"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { Button, Notice, PageCard } from "@/components/ui";
import { apiRequest, ApiError, Course } from "@/lib/api";

export function CourseWorkspace({ courseId }: { courseId: string }) {
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      setCourse(await apiRequest<Course>(`/courses/${courseId}`));
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Course could not be loaded.");
    }
  }

  useEffect(() => {
    let active = true;
    apiRequest<Course>(`/courses/${courseId}`)
      .then((result) => {
        if (active) {
          setCourse(result);
          setError("");
        }
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof ApiError ? reason.message : "Course could not be loaded.");
        }
      });
    return () => {
      active = false;
    };
  }, [courseId]);

  return (
    <AppShell>
      <div className="mx-auto max-w-5xl">
        <Link href="/app/library">← Back to library</Link>
        {error ? (
          <div className="mt-6 grid gap-4">
            <Notice>{error}</Notice>
            <Button className="w-fit" onClick={() => void load()}>Retry</Button>
          </div>
        ) : course ? (
          <>
            <header className="mb-8 mt-6">
              <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal">Course workspace</p>
              <h1 className="mt-2 text-3xl font-semibold text-ink">{course.name}</h1>
              {course.description && <p className="mt-2 text-slate-600">{course.description}</p>}
            </header>
            <PageCard>
              <h2 className="text-xl font-semibold">Your course space</h2>
              <p className="mt-2 text-slate-600">
                Course access is private to your study space. Document upload and study activities are coming in the next implementation milestone.
              </p>
              <p className="mt-4 text-sm text-slate-500">Course ID: {course.id}</p>
            </PageCard>
          </>
        ) : (
          <p className="mt-6" aria-live="polite">Loading course…</p>
        )}
      </div>
    </AppShell>
  );
}
