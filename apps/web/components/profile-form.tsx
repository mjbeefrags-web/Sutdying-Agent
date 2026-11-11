"use client";

import { FormEvent, useEffect, useState } from "react";

import { apiRequest, ApiError, User } from "@/lib/api";
import { Button, Field, Notice, PageCard, TextInput } from "@/components/ui";

export function ProfileForm() {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    apiRequest<User>("/account/profile")
      .then(setUser)
      .catch((reason: unknown) => {
        setError(reason instanceof ApiError ? reason.message : "Profile could not be loaded.");
      });
  }, []);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setSaved(false);
    setError("");
    const values = new FormData(event.currentTarget);
    try {
      const next = await apiRequest<User>("/account/profile", {
        method: "PATCH",
        body: JSON.stringify({
          display_name: String(values.get("display_name") ?? ""),
          locale: String(values.get("locale") ?? ""),
        }),
      });
      setUser(next);
      setSaved(true);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Profile could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <PageCard>
      <h1 className="text-2xl font-semibold">Profile settings</h1>
      <p className="mt-2 text-slate-600">Manage the personal details used in your study space.</p>
      {user ? (
        <form className="mt-6 grid max-w-xl gap-5" onSubmit={save}>
          <Field label="Email" htmlFor="email">
            <TextInput id="email" value={user.email} readOnly aria-describedby="email-status" />
            <span id="email-status" className="text-xs text-slate-600">
              {user.email_verified ? "Verified" : "Not verified"}
            </span>
          </Field>
          <Field label="Display name" htmlFor="display_name">
            <TextInput id="display_name" name="display_name" defaultValue={user.display_name} required maxLength={100} />
          </Field>
          <Field label="Language and region" htmlFor="locale">
            <TextInput id="locale" name="locale" defaultValue={user.locale} required minLength={2} maxLength={16} />
          </Field>
          {error && <Notice>{error}</Notice>}
          {saved && <Notice kind="success">Your profile was saved.</Notice>}
          <Button disabled={busy}>{busy ? "Saving…" : "Save profile"}</Button>
        </form>
      ) : error ? (
        <div className="mt-5"><Notice>{error}</Notice></div>
      ) : (
        <p className="mt-5" aria-live="polite">Loading profile…</p>
      )}
    </PageCard>
  );
}
