"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Camera, Plus, Loader2, Check, AlertCircle, X, Upload } from "lucide-react";

interface Meal {
  type: "breakfast" | "lunch" | "dinner";
  foods: string[];
  image_url?: string;
  completed: boolean;
}

interface DayProgress {
  day: number;
  meals: Meal[];
}

const MEAL_TYPES = [
  { id: "breakfast", label: "🌅 Breakfast", emoji: "🥣" },
  { id: "lunch", label: "🍽️ Lunch", emoji: "🍛" },
  { id: "dinner", label: "🌙 Dinner", emoji: "🍲" },
] as const;

export function DailyMealLogger() {
  const router = useRouter();
  const params = useParams();
  const dayNumber = parseInt(params.day as string);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [dayProgress, setDayProgress] = useState<DayProgress | null>(null);
  const [error, setError] = useState("");
  const [currentMealType, setCurrentMealType] = useState<"breakfast" | "lunch" | "dinner">("breakfast");
  const [foodInput, setFoodInput] = useState("");

  useEffect(() => {
    loadDayProgress();
  }, [dayNumber]);

  const loadDayProgress = async () => {
    try {
      const clientId = localStorage.getItem("clientId");
      const token = localStorage.getItem("authToken");

      if (!clientId) {
        router.push("/login");
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/challenge/${clientId}/day/${dayNumber}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error("Failed to load day progress");

      const data = await response.json();
      setDayProgress(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddFood = (type: typeof MEAL_TYPES[number]["id"]) => {
    if (!foodInput.trim()) return;

    setDayProgress((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        meals: prev.meals.map((meal) => {
          if (meal.type === type) {
            return {
              ...meal,
              foods: [...meal.foods, foodInput],
            };
          }
          return meal;
        }),
      };
    });
    setFoodInput("");
  };

  const handleRemoveFood = (type: typeof MEAL_TYPES[number]["id"], index: number) => {
    setDayProgress((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        meals: prev.meals.map((meal) => {
          if (meal.type === type) {
            return {
              ...meal,
              foods: meal.foods.filter((_, i) => i !== index),
            };
          }
          return meal;
        }),
      };
    });
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>, type: typeof MEAL_TYPES[number]["id"]) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // TODO: Upload image to backend
    const reader = new FileReader();
    reader.onload = (event) => {
      setDayProgress((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          meals: prev.meals.map((meal) => {
            if (meal.type === type) {
              return {
                ...meal,
                image_url: event.target?.result as string,
              };
            }
            return meal;
          }),
        };
      });
    };
    reader.readAsDataURL(file);
  };

  const handleSaveDay = async () => {
    try {
      setIsSaving(true);
      const clientId = localStorage.getItem("clientId");
      const token = localStorage.getItem("authToken");

      if (!clientId || !dayProgress) return;

      // POST /challenge/{client_id}/meals (for each meal)
      for (const meal of dayProgress.meals) {
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/challenge/${clientId}/submit-meal`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            day_number: dayNumber,
            meal_type: meal.type.toUpperCase(),
            foods: meal.foods,
            image_url: meal.image_url,
          }),
        });
      }

      // Show success and redirect
      router.push("/app/challenge");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save day");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!dayProgress) return null;

  return (
    <div className="p-4 md:p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading font-bold text-dark">Day {dayNumber} Meals</h1>
            <p className="text-dark/60 mt-1 font-body">Log your breakfast, lunch, and dinner</p>
          </div>
          <Button variant="outline" onClick={() => router.back()}>
            ← Back
          </Button>
        </div>
      </motion.div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700 font-body flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </p>
        </div>
      )}

      {/* Meal Tabs */}
      <div className="flex gap-2 border-b border-border">
        {MEAL_TYPES.map((mealType) => (
          <button
            key={mealType.id}
            onClick={() => setCurrentMealType(mealType.id as any)}
            className={`px-4 py-3 font-semibold border-b-2 transition-colors ${
              currentMealType === mealType.id
                ? "border-primary text-primary"
                : "border-transparent text-dark/60 hover:text-dark"
            }`}
          >
            {mealType.emoji} {mealType.label}
          </button>
        ))}
      </div>

      {/* Meal Content */}
      <motion.div
        key={currentMealType}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="p-6 space-y-6">
          {dayProgress.meals
            .filter((m) => m.type === currentMealType)
            .map((meal) => (
              <div key={meal.type} className="space-y-6">
                {/* Image Upload */}
                <div className="space-y-3">
                  <label className="block text-sm font-semibold text-dark font-body">
                    <Camera className="w-4 h-4 inline mr-2" />
                    Upload Meal Photo
                  </label>
                  {meal.image_url ? (
                    <div className="relative inline-block">
                      <img
                        src={meal.image_url}
                        alt={meal.type}
                        className="w-full max-w-md h-48 object-cover rounded-lg"
                      />
                      <button
                        onClick={() => {
                          setDayProgress((prev) => {
                            if (!prev) return null;
                            return {
                              ...prev,
                              meals: prev.meals.map((m) => {
                                if (m.type === meal.type) return { ...m, image_url: undefined };
                                return m;
                              }),
                            };
                          });
                        }}
                        className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <label className="border-2 border-dashed border-border rounded-lg p-6 cursor-pointer hover:bg-dark/5 transition-colors">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleImageUpload(e, meal.type)}
                        className="hidden"
                      />
                      <div className="text-center">
                        <Upload className="w-8 h-8 text-dark/40 mx-auto mb-2" />
                        <p className="text-sm font-semibold text-dark">Click to upload or drag and drop</p>
                        <p className="text-xs text-dark/60">PNG, JPG up to 10MB</p>
                      </div>
                    </label>
                  )}
                </div>

                {/* Food List */}
                <div className="space-y-3">
                  <label className="block text-sm font-semibold text-dark font-body">
                    <Plus className="w-4 h-4 inline mr-2" />
                    Food Items
                  </label>

                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={foodInput}
                      onChange={(e) => setFoodInput(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === "Enter") handleAddFood(meal.type);
                      }}
                      placeholder='e.g., "2 idli with sambar"'
                      className="flex-1 px-4 py-2 border border-border rounded-lg font-body focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    <Button
                      onClick={() => handleAddFood(meal.type)}
                      className="bg-primary hover:bg-primary/90"
                    >
                      Add
                    </Button>
                  </div>

                  {meal.foods.length > 0 && (
                    <div className="space-y-2">
                      {meal.foods.map((food, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-3 bg-primary/5 rounded-lg border border-primary/20"
                        >
                          <span className="font-body text-dark">{food}</span>
                          <button
                            onClick={() => handleRemoveFood(meal.type, idx)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Completion Indicator */}
                {meal.foods.length > 0 && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
                    <Check className="w-5 h-5 text-green-600" />
                    <p className="text-sm font-body text-green-700">
                      <strong>{meal.foods.length}</strong> food item{meal.foods.length !== 1 ? "s" : ""} logged
                    </p>
                  </div>
                )}
              </div>
            ))}
        </Card>
      </motion.div>

      {/* Summary */}
      <Card className="p-6 bg-primary/5">
        <h3 className="font-heading font-bold text-dark mb-4">Day {dayNumber} Summary</h3>
        <div className="grid grid-cols-3 gap-4">
          {dayProgress.meals.map((meal) => (
            <div key={meal.type} className="text-center p-3 bg-white rounded-lg border border-border">
              <p className="text-sm font-semibold text-dark capitalize">{meal.type}</p>
              <p className="text-2xl font-heading font-bold text-primary">{meal.foods.length}</p>
              <p className="text-xs text-dark/60">items logged</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <Button
          onClick={() => router.back()}
          variant="outline"
          className="flex-1"
          disabled={isSaving}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSaveDay}
          disabled={isSaving || dayProgress.meals.every((m) => m.foods.length === 0)}
          className="flex-1 bg-primary hover:bg-primary/90"
        >
          {isSaving ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Check className="w-4 h-4 mr-2" />
              Save Day {dayNumber}
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
