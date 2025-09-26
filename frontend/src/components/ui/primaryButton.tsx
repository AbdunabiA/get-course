import React from "react";

type PrimyeButtonProps = {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  className?: string;
};

const PrimaryButton: React.FC<PrimyeButtonProps> = ({
  children,
  onClick,
  type = "button",
  className = "",
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`${className}`}
    >
      {children}
    </button>
  );
};

export default PrimaryButton;