"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Loader2, Search, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { searchFoods, type FoodSearchResult } from "@/lib/api";

interface FoodSearchProps {
  onSelect: (food: FoodSearchResult) => void;
  placeholder?: string;
  className?: string;
}

export function FoodSearch({
  onSelect,
  placeholder = "Search food… e.g. idli, dal, banana",
  className,
}: FoodSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<FoodSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const runSearch = useCallback(async (q: string) => {
    if (q.trim().length < 2) {
      setResults([]);
      setOpen(false);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const data = await searchFoods(q.trim());
      setResults(data);
      setOpen(data.length > 0);
      setActiveIndex(-1);
    } catch {
      setResults([]);
      setOpen(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => runSearch(query), 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query, runSearch]);

  const handleSelect = (food: FoodSearchResult) => {
    onSelect(food);
    setQuery("");
    setResults([]);
    setOpen(false);
    setActiveIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!open || results.length === 0) return;
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActiveIndex((i) => Math.min(i + 1, results.length - 1));
        break;
      case "ArrowUp":
        e.preventDefault();
        setActiveIndex((i) => Math.max(i - 1, 0));
        break;
      case "Enter":
        e.preventDefault();
        if (activeIndex >= 0) handleSelect(results[activeIndex]);
        break;
      case "Escape":
        setOpen(false);
        setActiveIndex(-1);
        break;
    }
  };

  // Scroll active item into view
  useEffect(() => {
    if (activeIndex >= 0 && listRef.current) {
      const item = listRef.current.children[activeIndex] as HTMLElement;
      item?.scrollIntoView({ block: "nearest" });
    }
  }, [activeIndex]);

  const clearQuery = () => {
    setQuery("");
    setResults([]);
    setOpen(false);
    inputRef.current?.focus();
  };

  const noResults = !loading && open && results.length === 0 && query.trim().length >= 2;

  return (
    <div className={cn("relative", className)}>
      {/* Input */}
      <div className="relative flex items-center">
        <Search className="absolute left-3 w-4 h-4 text-dark/40 pointer-events-none" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          placeholder={placeholder}
          autoComplete="off"
          className={cn(
            "w-full pl-9 pr-9 py-2.5 rounded-xl border border-border",
            "bg-card font-body text-sm text-dark placeholder:text-dark/40",
            "focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary",
            "transition-colors"
          )}
        />
        <div className="absolute right-3 flex items-center">
          {loading && <Loader2 className="w-4 h-4 text-dark/40 animate-spin" />}
          {!loading && query && (
            <button
              onClick={clearQuery}
              className="text-dark/40 hover:text-dark transition-colors"
              tabIndex={-1}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Dropdown */}
      {open && results.length > 0 && (
        <ul
          ref={listRef}
          className={cn(
            "absolute z-50 w-full mt-1 bg-card border border-border rounded-xl shadow-lg",
            "max-h-60 overflow-y-auto py-1"
          )}
        >
          {results.map((food, i) => (
            <li key={food.food_id}>
              <button
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => handleSelect(food)}
                className={cn(
                  "w-full text-left px-4 py-2.5 font-body text-sm transition-colors",
                  "flex items-center justify-between gap-2",
                  i === activeIndex
                    ? "bg-primary/10 text-primary"
                    : "hover:bg-muted text-dark"
                )}
              >
                <span className="truncate">{food.food_name}</span>
                <span className="text-xs text-dark/40 shrink-0">{food.serving_unit}</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {/* No results */}
      {noResults && (
        <div className="absolute z-50 w-full mt-1 bg-card border border-border rounded-xl shadow-lg px-4 py-3">
          <p className="font-body text-sm text-dark/50">
            No foods found for <span className="font-medium text-dark">"{query}"</span>.
            Try a different spelling or use Quick Add below.
          </p>
        </div>
      )}
    </div>
  );
}
