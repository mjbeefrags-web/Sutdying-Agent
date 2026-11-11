import { AuthPage } from "@/components/auth-page";
import { ResetPasswordForm, ResetPasswordRequestForm } from "@/components/auth-form";

export default async function ResetPasswordPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token = "" } = await searchParams;
  return (
    <AuthPage
      title={token ? "Choose a new password" : "Reset your password"}
      description={token ? "Create a new password for your account." : "We will send a reset link if the account exists."}
    >
      {token ? <ResetPasswordForm initialToken={token} /> : <ResetPasswordRequestForm />}
    </AuthPage>
  );
}
