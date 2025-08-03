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
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '2rem',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0
    }}>
      <LoginForm onSubmit={handleLogin} />
    </div>
  );
}