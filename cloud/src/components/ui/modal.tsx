import * as React from "react";
import { cn } from "@/src/lib/utils";

type ModalProps = {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
};

export function Modal({ isOpen, onClose, children, className }: ModalProps) {
  // Handle escape key
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      {/* Modal content */}
      <div
        className={cn(
          "relative z-50 w-full max-w-md rounded-lg bg-background p-6 shadow-lg border border-border",
          className,
        )}
        role="dialog"
        aria-modal="true"
      >
        {children}
      </div>
    </div>
  );
}

type ModalHeaderProps = {
  children: React.ReactNode;
  className?: string;
};

export function ModalHeader({ children, className }: ModalHeaderProps) {
  return (
    <div className={cn("mb-4", className)}>
      <h2 className="text-lg font-semibold">{children}</h2>
    </div>
  );
}

type ModalBodyProps = {
  children: React.ReactNode;
  className?: string;
};

export function ModalBody({ children, className }: ModalBodyProps) {
  return (
    <div className={cn("mb-6 text-muted-foreground", className)}>
      {children}
    </div>
  );
}

type ModalFooterProps = {
  children: React.ReactNode;
  className?: string;
};

export function ModalFooter({ children, className }: ModalFooterProps) {
  return (
    <div className={cn("flex justify-end gap-3", className)}>{children}</div>
  );
}
