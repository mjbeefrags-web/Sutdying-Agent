"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { apiRequest, ApiError, User } from "@/lib/api";
import { Button, Field, Notice, TextInput } from "@/components/ui";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    const values = new FormData(event.currentTarget);
    const email = String(values.get("email") ?? "");
    const password = String(values.get("password") ?? "");
    try {
      if (mode === "register") {
        const displayName = String(values.get("display_name") ?? "");
        const result = await apiRequest<{ message: string }>("/auth/register", {
          method: "POST",
          body: JSON.stringify({ email, password, display_name: displayName }),
        });
        setMessage(result.message);
      } else {
        await apiRequest<User>("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
        router.replace("/app/library");
        router.refresh();
      }
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Something went wrong. Please retry.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="grid gap-5" onSubmit={submit}>
      {mode === "register" && (
        <Field label="Your name" htmlFor="display_name">
          <TextInput id="display_name" name="display_name" autoComplete="name" required maxLength={100} />
        </Field>
      )}
      <Field label="University email" htmlFor="email">
        <TextInput
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          maxLength={254}
        />
      </Field>
      <Field label="Password" htmlFor="password">
        <TextInput
          id="password"
          name="password"
          type="password"
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          required
          minLength={mode === "login" ? 1 : 12}
          maxLength={128}
        />
      </Field>
      {error && <Notice>{error}</Notice>}
      {message && <Notice kind="success">{message}</Notice>}
      <Button disabled={busy} type="submit">
        {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
      </Button>
      {mode === "login" && (
        <Link className="text-sm" href="/reset-password">Forgot your password?</Link>
      )}
      <p className="text-sm text-slate-600">
        {mode === "login" ? "New here? " : "Already have an account? "}
        <Link href={mode === "login" ? "/register" : "/login"}>
          {mode === "login" ? "Create an account" : "Sign in"}
        </Link>
      </p>
    </form>
  );
}

export function VerifyEmailForm({ initialToken }: { initialToken: string }) {
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const token = String(new FormData(event.currentTarget).get("token") ?? "");
    try {
      const result = await apiRequest<{ message: string }>("/auth/email/verify", {
        method: "POST",
        body: JSON.stringify({ token }),
      });
      setDone(true);
      setError(result.message);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Verification could not be completed.");
    } finally {
      setBusy(false);
    }
  }

  if (done) {
    return (
      <div className="grid gap-4">
        <Notice kind="success">{error}</Notice>
        <Link href="/login">Continue to sign in</Link>
      </div>
    );
  }
  return (
    <form className="grid gap-5" onSubmit={submit}>
      <Field label="Verification token" htmlFor="token">
        <TextInput id="token" name="token" defaultValue={initialToken} required minLength={32} />
      </Field>
      {error && <Notice>{error}</Notice>}
      <Button disabled={busy}>{busy ? "Verifying…" : "Verify email"}</Button>
    </form>
  );
}

export function ResetPasswordRequestForm() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const email = String(new FormData(event.currentTarget).get("email") ?? "");
    try {
      const result = await apiRequest<{ message: string }>("/auth/password-reset/request", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setMessage(result.message);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "The request could not be completed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="grid gap-5" onSubmit={submit}>
      <Field label="University email" htmlFor="email">
        <TextInput id="email" name="email" type="email" required autoComplete="email" />
      </Field>
      {message && <Notice kind="success">{message}</Notice>}
      {error && <Notice>{error}</Notice>}
      <Button disabled={busy}>{busy ? "Sending…" : "Send reset link"}</Button>
    </form>
  );
}

export function ResetPasswordForm({ initialToken }: { initialToken: string }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const values = new FormData(event.currentTarget);
    const password = String(values.get("password") ?? "");
    const confirmation = String(values.get("confirmation") ?? "");
    if (password !== confirmation) {
      setError("Passwords do not match.");
      setBusy(false);
      return;
    }
    try {
      await apiRequest<{ message: string }>("/auth/password-reset/confirm", {
        method: "POST",
        body: JSON.stringify({
          token: String(values.get("token") ?? ""),
          new_password: password,
        }),
      });
      router.replace("/login?passwordReset=1");
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "The password could not be changed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="grid gap-5" onSubmit={submit}>
      <Field label="Reset token" htmlFor="token">
        <TextInput id="token" name="token" defaultValue={initialToken} required minLength={32} />
      </Field>
      <Field label="New password" htmlFor="password">
        <TextInput id="password" name="password" type="password" required minLength={12} maxLength={128} autoComplete="new-password" />
      </Field>
      <Field label="Confirm new password" htmlFor="confirmation">
        <TextInput id="confirmation" name="confirmation" type="password" required minLength={12} maxLength={128} autoComplete="new-password" />
      </Field>
      {error && <Notice>{error}</Notice>}
      <Button disabled={busy}>{busy ? "Updating…" : "Update password"}</Button>
    </form>
  );
}
