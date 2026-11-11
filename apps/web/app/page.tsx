import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-8 py-20">
      <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-teal">
        Study, with clarity
      </p>
      <h1 className="max-w-3xl text-5xl font-semibold leading-tight text-ink">
        Your course material, made easier to understand.
      </h1>
      <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
        A calm study space for focused reading, grounded explanations, and deliberate practice.
        This Phase 1 shell is not yet connected to learning services.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Link
          className="inline-flex min-h-11 items-center rounded-lg bg-teal px-5 py-3 font-medium text-white no-underline hover:bg-[#154B47]"
          href="/register"
        >
          Create your study space
        </Link>
        <Link
          className="inline-flex min-h-11 items-center rounded-lg border border-slate-300 bg-white px-5 py-3 font-medium text-ink no-underline"
          href="/login"
        >
          Sign in
        </Link>
      </div>
    </main>
  );
}
