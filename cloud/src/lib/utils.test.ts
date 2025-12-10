import { describe, test, expect } from "bun:test";
import { getAllRoutes } from "./router-utils";
import { routeToFilename } from "./utils";

describe("router-utils", () => {
  describe("routeToFilename", () => {
    test("should handle root path correctly", () => {
      expect(routeToFilename("/")).toBe("index");
    });

    test("should convert routes to filenames correctly", () => {
      expect(routeToFilename("/blog")).toBe("blog");
      expect(routeToFilename("/blog/post")).toBe("blog-post");
      expect(routeToFilename("/docs/mirascope/getting-started")).toBe(
        "docs-mirascope-getting-started",
      );
    });

    test("should not have filename conflicts for all routes", async () => {
      // Get all routes in the application
      const routes = await getAllRoutes();

      // Map each route to its filename
      const filenames = routes.map((route) => routeToFilename(route));

      // Check for duplicates by creating a Set
      const uniqueFilenames = new Set(filenames);

      // If there are duplicates, these two counts will differ
      expect(uniqueFilenames.size).toBe(filenames.length);

      // Additional diagnostic: find any duplicates if they exist
      const filenameCounts = filenames.reduce(
        (acc, filename) => {
          acc[filename] = (acc[filename] || 0) + 1;
          return acc;
        },
        {} as Record<string, number>,
      );

      // Find duplicates (filenames that appear more than once)
      const duplicates = Object.entries(filenameCounts)
        .filter(([_, count]) => count > 1)
        .map(([filename, count]) => {
          // Find the routes that map to this filename
          const routesWithFilename = routes.filter(
            (route) => routeToFilename(route) === filename,
          );
          return { filename, count, routes: routesWithFilename };
        });

      // Expect no duplicates
      expect(duplicates.length).toBe(0);
    });
  });
});
