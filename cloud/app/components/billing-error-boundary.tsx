import { AlertTriangle } from "lucide-react";
import { Component, type ReactNode, type ErrorInfo } from "react";

import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/app/components/ui/card";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error boundary for the billing section.
 * Catches errors from Stripe operations and displays a user-friendly message.
 */
export class BillingErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console for debugging
    console.error("Billing error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <Card>
          <CardHeader>
            <CardTitle>Billing</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <AlertTriangle className="mb-4 h-12 w-12 text-amber-600" />
              <h3 className="mb-2 text-lg font-semibold">
                Unable to Load Billing Information
              </h3>
              <p className="mb-4 text-sm text-muted-foreground max-w-md">
                We encountered an error while loading your billing information.
                This might be a temporary issue with our payment provider.
              </p>
              {this.state.error && (
                <p className="mb-4 text-xs text-muted-foreground font-mono bg-muted px-3 py-2 rounded">
                  {this.state.error.message}
                </p>
              )}
              <Button onClick={this.handleReset} variant="outline">
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      );
    }

    return this.props.children;
  }
}
