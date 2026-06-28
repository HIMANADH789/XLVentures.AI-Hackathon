"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { Search, Sun, Moon, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";

interface NavbarProps {
  onSearchClick?: () => void;
  onRunDiscovery?: () => void;
  isDiscovering?: boolean;
}

export function Navbar({ onSearchClick, onRunDiscovery, isDiscovering = false }: NavbarProps) {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    if (resolvedTheme === "dark") {
      setTheme("light");
    } else {
      setTheme("dark");
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <div className="flex items-center space-x-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-xs">
            <Sparkles className="h-4.5 w-4.5 text-indigo-400 animate-pulse" />
          </div>
          <span className="font-bold tracking-tight text-lg text-foreground select-none">
            Prospect<span className="text-indigo-500 font-extrabold">IQ</span>
          </span>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          {/* Global Search command menu indicator */}
          <button
            onClick={onSearchClick}
            className="flex h-9 w-40 items-center justify-between rounded-lg border border-input bg-muted/30 px-3 text-xs text-muted-foreground transition-all hover:bg-muted/50 hover:text-foreground md:w-56 cursor-pointer max-sm:w-9 max-sm:justify-center max-sm:p-0"
            title="Search Companies"
          >
            <div className="flex items-center space-x-2">
              <Search className="h-3.5 w-3.5" />
              <span className="max-sm:hidden">Search leads...</span>
            </div>
            <kbd className="pointer-events-none select-none rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 max-sm:hidden">
              ⌘K
            </kbd>
          </button>

          {/* Theme Toggle with Rotation Icon Animation */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="h-9 w-9 rounded-lg border border-border bg-background/50 cursor-pointer"
            aria-label="Toggle theme"
          >
            <AnimatePresence mode="wait" initial={false}>
              {mounted && resolvedTheme === "dark" ? (
                <motion.div
                  key="moon"
                  initial={{ rotate: -90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: 90, opacity: 0 }}
                  transition={{ duration: 0.15 }}
                >
                  <Moon className="h-[18px] w-[18px] text-indigo-400" />
                </motion.div>
              ) : (
                <motion.div
                  key="sun"
                  initial={{ rotate: 90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: -90, opacity: 0 }}
                  transition={{ duration: 0.15 }}
                >
                  <Sun className="h-[18px] w-[18px] text-amber-500" />
                </motion.div>
              )}
            </AnimatePresence>
          </Button>

          {/* Run Discovery Trigger Button */}
          <Button
            onClick={onRunDiscovery}
            disabled={isDiscovering}
            className="h-9 rounded-lg bg-indigo-600 px-4 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 disabled:opacity-50 select-none relative overflow-hidden group cursor-pointer"
          >
            {isDiscovering ? (
              <span className="flex items-center space-x-1.5">
                <span className="h-2 w-2 animate-ping rounded-full bg-white" />
                <span>Running...</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1.5">
                <Sparkles className="h-3.5 w-3.5 text-white/90" />
                <span>Run Discovery</span>
              </span>
            )}
          </Button>
        </div>
      </div>
    </header>
  );
}
