import { createFileRoute } from "@tanstack/react-router";
import { AppLayout, PageMeta } from "@/src/components";

/**
 * Test component for visualizing AppLayout behavior
 *
 * Note: Footer is handled by root layout and doesn't need to be included here
 */
export const Route = createFileRoute("/dev/layout-test")({
  ssr: false, // Client-side rendered
  component: LayoutTestPage,
});

function LayoutTestPage() {
  // Generate repeated content for testing scrolling
  const generateRepeatedContent = (count: number) => {
    const content = [];
    for (let i = 1; i <= count; i++) {
      content.push(
        <div key={i} className="bg-muted/50 border-secondary mb-4 border-l-4 p-4">
          <h2 className="mb-2 font-bold">Content Section {i}</h2>
          <p>This is repeated content section {i} for testing scroll behavior.</p>
          <p className="mt-2">
            The sidebars should remain fixed while this content scrolls independently. Long content
            ensures we can properly test the layout's scroll behavior.
          </p>
        </div>
      );
    }
    return content;
  };

  return (
    <>
      <PageMeta title="Layout Test" description="Test AppLayout component behavior" />
      <AppLayout>
        <AppLayout.LeftSidebar>
          <div className="border-primary border-2">
            <div className="p-4">
              <h2 className="mb-4 font-bold">Left Sidebar</h2>
              <div className="bg-muted mb-2 p-2">Navigation Item 1</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 2</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 3</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 4</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 5</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 6</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 7</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 8</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 9</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 10</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 11</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 12</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 13</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 14</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 15</div>
              <div className="bg-muted mb-2 p-2">Navigation Item 16</div>

              <div className="text-muted-foreground mt-6 text-sm">
                Sidebar should have its own scrollbar if content overflows
              </div>
            </div>
          </div>
        </AppLayout.LeftSidebar>

        <AppLayout.Content>
          <div className="border-secondary border-2">
            <div className="py-6">
              <div className="mx-auto max-w-5xl">
                <h1 className="mb-8 text-xl font-semibold">AppLayout Test</h1>

                <div className="bg-muted/50 mb-4 p-4">
                  <h2 className="mb-2 font-bold">Main Content Area</h2>
                  <p>This area represents the main content region with typical styling patterns.</p>
                  <p className="mt-2">
                    It includes py-6 padding and max-w-5xl for readable content width. The content
                    below is long to test scrolling behavior.
                  </p>
                </div>

                <div className="bg-muted/50 mb-4 p-4">
                  <h2 className="mb-2 font-bold">Layout Structure</h2>
                  <p>AppLayout manages the three-column layout structure:</p>
                  <ul className="mt-2 list-disc pl-5">
                    <li>Left sidebar (fixed position, fixed width, independent scrolling)</li>
                    <li>Main content (flexible width, scrolls independently)</li>
                    <li>Right sidebar (fixed position, fixed width, independent scrolling)</li>
                  </ul>
                </div>

                <div className="border-accent bg-accent/5 mb-8 border-l-4 p-4 text-sm font-medium">
                  <p>Scroll down to test the sidebar behavior. The sidebars should:</p>
                  <ul className="mt-2 list-disc pl-5">
                    <li>Stay fixed in place while main content scrolls</li>
                    <li>Have their own independent scrollbars if their content is too long</li>
                    <li>Maintain proper alignment with header and main content</li>
                  </ul>
                </div>

                <h2 className="mb-4 text-lg font-bold">Scroll Test Content</h2>
                {generateRepeatedContent(20)}

                <div className="bg-primary/5 border-primary mt-8 border-l-4 p-4">
                  <h2 className="mb-2 font-bold">Bottom of Content</h2>
                  <p>You've reached the end of the test content.</p>
                  <p className="mt-2">
                    The sidebars should have remained fixed in place while scrolling.
                  </p>
                </div>

                <div className="text-muted-foreground mt-8 mb-4 text-sm">
                  <p>Note: Colored borders visualize component boundaries.</p>
                  <p className="mt-1">Green border: AppLayout.Content</p>
                  <p className="mt-1">Blue border: AppLayout.LeftSidebar</p>
                  <p className="mt-1">Purple border: AppLayout.RightSidebar</p>
                </div>
              </div>
            </div>
          </div>
        </AppLayout.Content>

        <AppLayout.RightSidebar>
          <div className="border-accent border-2">
            <div className="p-4">
              <h2 className="mb-4 font-bold">Right Sidebar</h2>
              <div className="bg-muted mb-2 p-2">Table of Contents</div>
              <div className="bg-muted mb-2 p-2">- Introduction</div>
              <div className="bg-muted mb-2 p-2">- Layout Structure</div>
              <div className="bg-muted mb-2 p-2">- Scroll Test</div>
              <div className="bg-muted mb-2 p-2">- Section 5</div>
              <div className="bg-muted mb-2 p-2">- Section 6</div>
              <div className="bg-muted mb-2 p-2">- Section 7</div>
              <div className="bg-muted mb-2 p-2">- Section 8</div>
              <div className="bg-muted mb-2 p-2">- Section 9</div>
              <div className="bg-muted mb-2 p-2">- Section 10</div>
              <div className="bg-muted mb-2 p-2">- Section 11</div>
              <div className="bg-muted mb-2 p-2">- Section 12</div>
              <div className="bg-muted mb-2 p-2">- Section 13</div>
              <div className="bg-muted mb-2 p-2">- Section 14</div>
              <div className="bg-muted mb-2 p-2">- Section 15</div>
              <div className="bg-muted p-2">- Conclusion</div>

              <div className="text-muted-foreground mt-6 text-sm">
                Sidebar should have its own scrollbar if content overflows
              </div>
            </div>
          </div>
        </AppLayout.RightSidebar>
      </AppLayout>
    </>
  );
}

