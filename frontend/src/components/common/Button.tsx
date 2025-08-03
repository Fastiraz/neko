import React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>;

const Button = ({ className = "", ...props }: ButtonProps) => {
  return (
    <button
      className="send-button"
      {...props}
    />
  );
};

export default Button;