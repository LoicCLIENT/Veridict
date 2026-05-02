"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Plus } from "lucide-react";

const navItems = [
  { href: "/casos", label: "Historial" },
  { href: "/demo", label: "Demo" },
  { href: "/docs", label: "Documentación" },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/[0.06] bg-[#0a0a0a]/90 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-[1200px] items-center justify-between px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <span className="text-xl font-semibold text-white tracking-tight">
            Veridict
          </span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          {navItems.map((item) => {
            const isActive = pathname === item.href ||
              (item.href === "/casos" && pathname.startsWith("/casos") && pathname !== "/casos/nuevo");

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`text-sm transition-colors ${
                  isActive
                    ? "text-white"
                    : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* CTA */}
        <Link
          href="/casos/nuevo"
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            pathname === "/casos/nuevo"
              ? "bg-[#C2E94B] text-[#0a0a0a]"
              : "bg-[#C2E94B] text-[#0a0a0a] hover:bg-[#d4f55d]"
          }`}
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Nuevo caso</span>
        </Link>
      </div>

      {/* Mobile nav */}
      <nav className="md:hidden flex items-center justify-center gap-8 pb-3 border-t border-white/[0.04] pt-3">
        {navItems.map((item) => {
          const isActive = pathname === item.href ||
            (item.href === "/casos" && pathname.startsWith("/casos") && pathname !== "/casos/nuevo");

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`text-xs transition-colors ${
                isActive ? "text-white" : "text-zinc-500"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
