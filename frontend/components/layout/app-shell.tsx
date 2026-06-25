import { Navbar } from "./navbar";
import { BottomNav } from "./bottom-nav";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="pb-24 md:pb-0 pt-24">{children}</main>
      <BottomNav />
    </div>
  );
}
