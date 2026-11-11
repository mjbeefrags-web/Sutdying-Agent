"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { apiRequest, ApiError, Course, Organization } from "@/lib/api";
import { Button, Field, Notice, PageCard, TextInput } from "@/components/ui";

export function CourseLibrary() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const orgs = await apiRequest<Organization[]>("/organizations");
      setOrganizations(orgs);
      const courseLists = await Promise.all(
        orgs.map((organization) =>
          apiRequest<Course[]>(`/organizations/${organization.id}/courses`),
        ),
      );
      setCourses(courseLists.flat());
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Courses could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    apiRequest<Organization[]>("/organizations")
      .then(async (orgs) => ({
        orgs,
        courseLists: await Promise.all(
          orgs.map((organization) =>
            apiRequest<Course[]>(`/organizations/${organization.id}/courses`),
          ),
        ),
      }))
      .then(({ orgs, courseLists }) => {
        if (active) {
          setOrganizations(orgs);
          setCourses(courseLists.flat());
          setError("");
        }
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof ApiError ? reason.message : "Courses could not be loaded.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  async function createCourse(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!organizations[0]) {
      setError("A personal study space is not available. Please contact support.");
      return;
    }
    setBusy(true);
    setError("");
    const form = event.currentTarget;
    const values = new FormData(form);
    try {
      await apiRequest<Course>(`/organizations/${organizations[0].id}/courses`, {
        method: "POST",
        body: JSON.stringify({
          name: String(values.get("name") ?? ""),
          description: String(values.get("description") ?? "") || null,
        }),
      });
      form.reset();
      await load();
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Course could not be created.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl">
      <header className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal">Your study space</p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">Library</h1>
        <p className="mt-2 max-w-2xl text-slate-600">
          Organize courses here. Documents and AI tools will appear as their processing features are added.
        </p>
      </header>

      <PageCard>
        <h2 className="text-xl font-semibold">Create a course</h2>
        <form className="mt-5 grid gap-4 sm:grid-cols-2" onSubmit={createCourse}>
          <Field label="Course name" htmlFor="course-name">
            <TextInput id="course-name" name="name" required maxLength={120} placeholder="e.g. Molecular Biology" />
          </Field>
          <Field label="Description (optional)" htmlFor="course-description">
            <TextInput id="course-description" name="description" maxLength={2000} placeholder="A short note about this course" />
          </Field>
          <Button className="sm:col-span-2 sm:w-fit" disabled={busy || loading}>
            {busy ? "Creating…" : "Create course"}
          </Button>
        </form>
      </PageCard>

      <section className="mt-10" aria-labelledby="courses-title">
        <div className="flex items-center justify-between gap-4">
          <h2 id="courses-title" className="text-xl font-semibold">Courses</h2>
          <Button className="bg-white text-ink ring-1 ring-slate-300 hover:bg-paper" onClick={() => void load()}>
            Refresh
          </Button>
        </div>
        {error && <div className="mt-4"><Notice>{error}</Notice></div>}
        {loading ? (
          <p className="mt-5" aria-live="polite">Loading courses…</p>
        ) : courses.length === 0 ? (
          <PageCard>
            <p className="font-medium">Your library is ready for its first course.</p>
            <p className="mt-2 text-sm text-slate-600">Create a course above to get started.</p>
          </PageCard>
        ) : (
          <ul className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {courses.map((course) => (
              <li key={course.id}>
                <Link
                  className="block h-full rounded-2xl border border-slate-200 bg-white p-5 text-ink no-underline shadow-sm transition hover:border-teal"
                  href={`/app/courses/${course.id}`}
                >
                  <h3 className="font-semibold">{course.name}</h3>
                  <p className="mt-2 line-clamp-3 text-sm text-slate-600">
                    {course.description || "No description"}
                  </p>
                  <span className="mt-5 inline-block text-sm font-medium text-teal">Open course →</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
