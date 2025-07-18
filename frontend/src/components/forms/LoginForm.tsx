import React from "react";
import { useForm } from "react-hook-form";
import Input from "../common/Input";
import Button from "../common/Button";

type LoginFormInputs = {
  email: string;
  password: string;
};

export default function LoginForm({
  onSubmit,
}: {
  onSubmit: (data: LoginFormInputs) => void;
}) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormInputs>();

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="max-w-sm mx-auto p-6 bg-white rounded-xl shadow space-y-4"
    >
      <h2 className="text-2xl font-bold text-center">Login</h2>

      <div>
        <label htmlFor="email" className="block mb-1 font-medium">
          Email
        </label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          {...register("email", { required: "Email is required" })}
        />
        {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
      </div>

      <div>
        <label htmlFor="password" className="block mb-1 font-medium">
          Password
        </label>
        <Input
          id="password"
          type="password"
          placeholder="••••••••"
          {...register("password", { required: "Password is required" })}
        />
        {errors.password && (
          <p className="text-sm text-red-500">{errors.password.message}</p>
        )}
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "Logging in..." : "Login"}
      </Button>
    </form>
  );
}
