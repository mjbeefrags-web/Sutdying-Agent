import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from "react";

export function Button({
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`inline-flex min-h-11 items-center justify-center rounded-lg bg-teal px-5 py-2.5 font-medium text-white transition-colors hover:bg-[#154B47] disabled:cursor-not-allowed disabled:opacity-60 ${className}`}
      {...props}
    />
  );
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={`min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-ink shadow-sm placeholder:text-slate-500 focus-visible:border-teal ${props.className ?? ""}`}
    />
  );
}

export function Field({
  label,
  htmlFor,
  children,
}: {
  label: string;
  htmlFor: string;
  children: ReactNode;
}) {
  return (
    <div className="grid gap-2">
      <label className="text-sm font-medium text-ink" htmlFor={htmlFor}>{label}</label>
      {children}
    </div>
  );
}

export function Notice({
  children,
  kind = "error",
}: {
  children: ReactNode;
  kind?: "error" | "info" | "success";
}) {
  const styles = {
    error: "border-red-300 bg-red-50 text-red-900",
    info: "border-slate-200 bg-slate-50 text-slate-700",
    success: "border-emerald-300 bg-emerald-50 text-emerald-900",
  };
  return (
    <div className={`rounded-lg border p-3 text-sm ${styles[kind]}`} role="status">
      {children}
    </div>
  );
}

export function PageCard({ children }: { children: ReactNode }) {
  return <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">{children}</section>;
}
