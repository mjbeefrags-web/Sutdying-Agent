import { AuthPage } from "@/components/auth-page";
import { VerifyEmailForm } from "@/components/auth-form";

export default async function VerifyEmailPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token = "" } = await searchParams;
  return (
    <AuthPage title="Verify your email" description="Confirm the email address on your account.">
      <VerifyEmailForm initialToken={token} />
    </AuthPage>
  );
}
