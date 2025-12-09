import React from "react";
import { ErrorContent, PageMeta } from "@/src/components";

const NotFound: React.FC = () => {
  return (
    <div className="relative">
      <PageMeta
        title="404 - Page Not Found"
        description="The page you are looking for does not exist."
        robots="noindex, nofollow"
      />

      <ErrorContent
        title="404 - Page Not Found"
        message="The page you're looking for doesn't exist or has been moved."
        showBackButton={true}
        backTo="/"
        backLabel="Back to Home"
      />
    </div>
  );
};

export default NotFound;
