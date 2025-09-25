import { ReactNode } from "react";

interface ProtectedLayoutProps {
  requiredRole?: "STUDENT" | "INSTRUCTOR" | "ADMIN";
  children:ReactNode
}


const ProtectedLayout = ({ children }:ProtectedLayoutProps) => {
  return children;
};

export default ProtectedLayout