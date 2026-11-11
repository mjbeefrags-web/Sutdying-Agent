import { AuthForm } from "@/components/auth-form";
import { AuthPage } from "@/components/auth-page";

export default function LoginPage() {
  return (
    <AuthPage title="Welcome back" description="Sign in to return to your courses.">
      <AuthForm mode="login" />
    </AuthPage>
  );
}
