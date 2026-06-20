import { Navbar } from "./navbar";
import { BottomNav } from "./bottom-nav";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="pb-20 md:pb-0 pt-16">{children}</main>
      <BottomNav />
    </div>
  );
}
