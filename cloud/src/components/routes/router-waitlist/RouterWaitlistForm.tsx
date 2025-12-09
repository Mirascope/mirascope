import { useState, useTransition } from "react";
import { Input } from "@/src/components/ui/input";
import { Button } from "@/src/components/ui/button";
import { Card, CardContent } from "@/src/components/ui/card";
import { cn } from "@/src/lib/utils";

export function RouterWaitlistForm() {
  const [success, setSuccess] = useState(false);
  const [isPending, startTransition] = useTransition();

  return (
    <Card className="mx-auto max-w-md border bg-white/10">
      <CardContent className="flex flex-col gap-3 p-4">
        <form
          className="flex flex-col gap-3"
          onSubmit={async (e) => {
            e.preventDefault();
            const form = e.currentTarget;
            const formData = new FormData(form);
            const payload = {
              firstName: formData.get("firstName"),
              lastName: formData.get("lastName"),
              email: formData.get("email"),
            };

            startTransition(async () => {
              try {
                const res = await fetch("https://mirascope.com/cf/join-router-waitlist", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify(payload),
                });

                if (res.ok) {
                  setSuccess(true);
                  form.reset();
                } else {
                  const err = await res.text();
                  alert(`Something went wrong: ${err}`);
                }
              } catch (err) {
                alert("Failed to submit. Please try again later.");
              }
            });
          }}
        >
          <div className="flex flex-col gap-2 md:flex-row">
            <Input
              name="firstName"
              placeholder="First name"
              required
              className="text-foreground bg-white/90"
            />
            <Input
              name="lastName"
              placeholder="Last name"
              required
              className="text-foreground bg-white/90"
            />
          </div>
          <Input
            name="email"
            type="email"
            placeholder="you@company.com"
            required
            className="text-foreground bg-white/90"
          />
          <Button
            type="submit"
            className={cn("w-full cursor-pointer", success ? "bg-lilypad-green" : "")}
            disabled={isPending}
          >
            {success ? "You're on the list! ✅" : "Join the Waitlist"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
