import React from "react";
import LoginForm from "../components/forms/LoginForm";
import { login } from "../services/authService";

type LoginPageProps = {
  onLoginSuccess: () => void;
};

export default function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const handleLogin = async (data: { email: string; password: string }) => {
    try {
      await login(data.email, data.password);
      onLoginSuccess();
    } catch (error) {
      alert("Login failed");
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <LoginForm onSubmit={handleLogin} />
    </div>
  );
}
