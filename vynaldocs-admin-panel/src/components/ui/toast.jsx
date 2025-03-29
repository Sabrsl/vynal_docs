import React from "react";
import { X } from "lucide-react";
import * as ToastPrimitives from "@radix-ui/react-toast";
import { cn } from "../../lib/utils";

const ToastProvider = ToastPrimitives.Provider;

const ToastViewport = React.forwardRef(({ className, ...props }, ref) => (
  <ToastPrimitives.Viewport
    ref={ref}
    className={cn(
      "fixed top-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]",
      className
    )}
    {...props}
  />
));
ToastViewport.displayName = ToastPrimitives.Viewport.displayName;

const Toast = React.forwardRef(({ className, variant, ...props }, ref) => (
  <ToastPrimitives.Root
    ref={ref}
    className={cn(
      "group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-bottom-full",
      variant === "destructive" && "border-destructive bg-destructive text-destructive-foreground",
      variant === "success" && "border-green-600 bg-green-100 text-green-700",
      className
    )}
    {...props}
  />
));
Toast.displayName = ToastPrimitives.Root.displayName;

const ToastAction = React.forwardRef(({ className, ...props }, ref) => (
  <ToastPrimitives.Action
    ref={ref}
    className={cn(
      "inline-flex h-8 shrink-0 items-center justify-center rounded-md border bg-background px-3 text-sm font-medium ring-offset-background transition-colors hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 group-[.destructive]:border-muted/40 group-[.destructive]:hover:border-destructive/30 group-[.destructive]:hover:bg-destructive group-[.destructive]:hover:text-destructive-foreground group-[.destructive]:focus:ring-destructive",
      className
    )}
    {...props}
  />
));
ToastAction.displayName = ToastPrimitives.Action.displayName;

const ToastClose = React.forwardRef(({ className, ...props }, ref) => (
  <ToastPrimitives.Close
    ref={ref}
    className={cn(
      "absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100 group-[.destructive]:text-red-300 group-[.destructive]:hover:text-red-50 group-[.destructive]:focus:ring-red-400 group-[.destructive]:focus:ring-offset-red-600",
      className
    )}
    toast-close=""
    {...props}
  >
    <X className="h-4 w-4" />
  </ToastPrimitives.Close>
));
ToastClose.displayName = ToastPrimitives.Close.displayName;

const ToastTitle = React.forwardRef(({ className, ...props }, ref) => (
  <ToastPrimitives.Title
    ref={ref}
    className={cn("text-sm font-semibold", className)}
    {...props}
  />
));
ToastTitle.displayName = ToastPrimitives.Title.displayName;

const ToastDescription = React.forwardRef(({ className, ...props }, ref) => (
  <ToastPrimitives.Description
    ref={ref}
    className={cn("text-sm opacity-90", className)}
    {...props}
  />
));
ToastDescription.displayName = ToastPrimitives.Description.displayName;

// Toast hook pour création simple
const useToast = () => {
  const [toasts, setToasts] = React.useState([]);

  const toast = ({ title, description, action, variant, duration = 5000 }) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast = { id, title, description, action, variant, duration };
    setToasts((prevToasts) => [...prevToasts, newToast]);

    if (duration) {
      setTimeout(() => {
        setToasts((prevToasts) => prevToasts.filter((t) => t.id !== id));
      }, duration);
    }

    return id;
  };

  const dismiss = (id) => {
    setToasts((prevToasts) => prevToasts.filter((t) => t.id !== id));
  };

  return { toast, dismiss, toasts };
};

// Composant principal Toaster
export function Toaster() {
  const { toasts } = useToast();

  return (
    <ToastProvider>
      {toasts.map(({ id, title, description, action, ...props }) => (
        <Toast key={id} {...props}>
          <div className="grid gap-1">
            {title && <ToastTitle>{title}</ToastTitle>}
            {description && <ToastDescription>{description}</ToastDescription>}
          </div>
          {action && <ToastAction altText="Action">{action}</ToastAction>}
          <ToastClose />
        </Toast>
      ))}
      <ToastViewport />
    </ToastProvider>
  );
}

// Singleton pattern pour le toast
let toastInstance;

export const toast = ({ title, description, variant, duration = 5000 }) => {
  if (typeof window === 'undefined') return;
  
  // Créer un élément toast dans le DOM s'il n'existe pas
  if (!toastInstance) {
    const toastRoot = document.createElement('div');
    toastRoot.id = 'toast-root';
    document.body.appendChild(toastRoot);
    
    // Style pour positionner les toasts
    const style = document.createElement('style');
    style.innerHTML = `
      #toast-root {
        position: fixed;
        z-index: 9999;
        top: 16px;
        right: 16px;
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .toast {
        padding: 12px 16px;
        border-radius: 4px;
        background: white;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        display: flex;
        flex-direction: column;
        max-width: 400px;
        min-width: 300px;
        animation: slideIn 0.2s ease-out;
      }
      .toast-success {
        border-color: #10b981;
        background-color: #ecfdf5;
      }
      .toast-destructive {
        border-color: #ef4444;
        background-color: #fef2f2;
      }
      .toast-title {
        font-weight: 600;
        margin-bottom: 4px;
        font-size: 14px;
      }
      .toast-description {
        font-size: 14px;
        opacity: 0.9;
      }
      @keyframes slideIn {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      @keyframes slideOut {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(100%);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }
  
  // Créer le toast
  const toastEl = document.createElement('div');
  toastEl.className = `toast ${variant ? `toast-${variant}` : ''}`;
  
  // Ajouter le titre
  if (title) {
    const titleEl = document.createElement('div');
    titleEl.className = 'toast-title';
    titleEl.textContent = title;
    toastEl.appendChild(titleEl);
  }
  
  // Ajouter la description
  if (description) {
    const descEl = document.createElement('div');
    descEl.className = 'toast-description';
    descEl.textContent = description;
    toastEl.appendChild(descEl);
  }
  
  // Ajouter le toast au DOM
  document.getElementById('toast-root')?.appendChild(toastEl);
  
  // Supprimer le toast après la durée spécifiée
  setTimeout(() => {
    toastEl.style.animation = 'slideOut 0.2s ease-in forwards';
    setTimeout(() => {
      toastEl.remove();
    }, 200);
  }, duration);
};

export {
  useToast,
  ToastProvider,
  ToastViewport,
  Toast,
  ToastTitle,
  ToastDescription,
  ToastClose,
  ToastAction,
}; 