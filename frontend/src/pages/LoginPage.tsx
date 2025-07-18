import React from "react";
import LoginForm from "../components/forms/LoginForm";
import { login } from "../services/authService";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const navigate = useNavigate();

  const handleLogin = async (data: { email: string; password: string }) => {
    try {
      const { user, token } = await login(data.email, data.password);
      console.log("Logged in!", user, token);
      // Navigate to chat or dashboard
      navigate("/chat");
    } catch (error) {
      console.error("Login failed:", error);
      alert("Login failed: " + error.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <LoginForm onSubmit={handleLogin} />
    </div>
  );
}
