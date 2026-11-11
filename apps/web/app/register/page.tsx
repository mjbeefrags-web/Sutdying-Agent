import { AuthForm } from "@/components/auth-form";
import { AuthPage } from "@/components/auth-page";

export default function RegisterPage() {
  return (
    <AuthPage title="Create your account" description="Start with a private study space for your courses.">
      <AuthForm mode="register" />
    </AuthPage>
  );
}
