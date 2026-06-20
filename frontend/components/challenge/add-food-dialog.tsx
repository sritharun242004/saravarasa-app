"use client";

import { useState } from "react";
import { Plus, Minus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FoodSearch } from "./food-search";
import { type FoodSearchResult, type StructuredFood } from "@/lib/api";

const UNITS = ["piece", "cup", "bowl", "plate", "g", "100g", "tbsp", "tsp", "serving"] as const;
type Unit = (typeof UNITS)[number];

interface AddFoodDialogProps {
  onAdd: (food: StructuredFood) => void;
}

export function AddFoodDialog({ onAdd }: AddFoodDialogProps) {
  const [selectedFood, setSelectedFood] = useState<FoodSearchResult | null>(null);
  const [quantity, setQuantity] = useState<number>(1);
  const [unit, setUnit] = useState<Unit>("piece");

  const handleSelect = (food: FoodSearchResult) => {
    setSelectedFood(food);
    // Pre-select the food's default serving unit when available
    const fu = food.serving_unit?.toLowerCase() as Unit;
    if (UNITS.includes(fu)) setUnit(fu);
    else setUnit("piece");
    setQuantity(1);
  };

  const handleAdd = () => {
    if (!selectedFood) return;
    onAdd({
      food_id:   selectedFood.food_id,
      food_name: selectedFood.food_name,
      quantity,
      unit,
    });
    setSelectedFood(null);
    setQuantity(1);
    setUnit("piece");
  };

  const isValid = selectedFood !== null && quantity > 0;

  return (
    <div className="space-y-3 p-4 bg-muted/30 rounded-2xl border border-border">
      <p className="font-body text-xs text-dark/50 uppercase tracking-wide font-semibold">
        Add Food
      </p>

      {/* Food search */}
      <FoodSearch onSelect={handleSelect} />

      {/* Selected food preview */}
      {selectedFood && (
        <div className="flex items-center gap-2 px-3 py-2 bg-primary/5 border border-primary/20 rounded-xl">
          <span className="font-body text-sm font-medium text-primary truncate flex-1">
            {selectedFood.food_name}
          </span>
          <button
            onClick={() => setSelectedFood(null)}
            className="text-dark/40 hover:text-dark transition-colors shrink-0"
          >
            ×
          </button>
        </div>
      )}

      {/* Quantity + Unit row */}
      <div className="flex gap-2">
        <div className="flex-1">
          <label className="font-body text-xs text-dark/50 mb-1 block">Quantity</label>
          <div className="flex items-center border border-border rounded-xl bg-card overflow-hidden">
            <button
              type="button"
              onClick={() => setQuantity((q) => Math.max(0.5, parseFloat((q - (unit === "g" || unit === "100g" ? 25 : 0.5)).toFixed(1))))}
              className="px-3 py-2 text-dark/50 hover:text-dark hover:bg-muted/50 transition-colors border-r border-border"
            >
              <Minus className="w-3.5 h-3.5" />
            </button>
            <input
              type="number"
              min={0.5}
              step={unit === "g" || unit === "100g" ? 25 : 0.5}
              value={quantity}
              onChange={(e) => setQuantity(Math.max(0.5, parseFloat(e.target.value) || 1))}
              className="flex-1 text-center py-2 bg-transparent font-body text-sm font-semibold text-dark focus:outline-none w-12"
            />
            <button
              type="button"
              onClick={() => setQuantity((q) => parseFloat((q + (unit === "g" || unit === "100g" ? 25 : 0.5)).toFixed(1)))}
              className="px-3 py-2 text-dark/50 hover:text-dark hover:bg-muted/50 transition-colors border-l border-border"
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        <div className="flex-1">
          <label className="font-body text-xs text-dark/50 mb-1 block">Unit</label>
          <select
            value={unit}
            onChange={(e) => {
              const u = e.target.value as Unit;
              setUnit(u);
              // Reset to a sensible default quantity when switching unit type
              setQuantity(u === "g" ? 100 : u === "100g" ? 1 : 1);
            }}
            className="w-full px-3 py-2 rounded-xl border border-border bg-card font-body text-sm text-dark focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          >
            {UNITS.map((u) => (
              <option key={u} value={u}>{u}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Add button */}
      <Button
        onClick={handleAdd}
        disabled={!isValid}
        size="sm"
        className="w-full"
      >
        <Plus className="w-4 h-4 mr-1" />
        Add {selectedFood ? selectedFood.food_name : "Food"}
      </Button>
    </div>
  );
}
