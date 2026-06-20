"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus, X, Loader2, Search, ChevronDown, ChevronUp,
  Zap, ArrowLeft, Flame,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  foodAutocomplete, getFoodNutrition, manualAnalyzeComplete,
  type FoodNutrition, type FoodTemplate,
} from "@/lib/api";
import { toast } from "@/lib/use-toast";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

// ── Category classifier (mirrors Streamlit CATEGORY_RULES) ───────────────────
const CATEGORY_ICONS: Record<string, string> = {
  DOSA: "🫓", IDLI: "⚪", VADA: "🍩", BIRYANI: "🍛",
  BEVERAGE: "☕", DAL: "🍲", BREAD: "🫓", RICE: "🍚",
  NON_VEG: "🍗", SWEET: "🍮", FRUIT: "🍎",
  SNACK: "🧆", CURRY: "🫕", VEGETABLE: "🥦", GENERAL: "🍽️",
};

const CATEGORY_RULES: [string, string[]][] = [
  ["DOSA",      ["dosa", "dosai", "uttapam", "uttappam", "pesarattu"]],
  ["IDLI",      ["idli", "idly"]],
  ["VADA",      ["vada", "vadai", "vade", "medu"]],
  ["BIRYANI",   ["biryani", "biriyani"]],
  ["BEVERAGE",  ["tea", "coffee", "juice", "milk", "lassi", "chai", "kaapi", "buttermilk", "shake", "drink"]],
  ["DAL",       ["sambar", "rasam", "dal", "dhal", "daal", "soup", "lentil", "paruppu"]],
  ["BREAD",     ["chapati", "chapathi", "roti", "paratha", "parantha", "naan", "puri", "poori", "parotta", "appam", "bread", "toast"]],
  ["RICE",      ["rice", "pulao", "pulav", "pongal", "khichdi", "upma", "poha", "chawal", "anna"]],
  ["NON_VEG",   ["chicken", "mutton", "fish", "egg", "prawn", "beef", "pork", "meat", "keema", "crab", "lamb", "shrimp"]],
  ["SWEET",     ["halwa", "kheer", "payasam", "ladoo", "laddoo", "barfi", "gulab jamun", "rasgulla", "jalebi", "sweet", "cake", "kulfi"]],
  ["FRUIT",     ["apple", "banana", "mango", "orange", "grape", "guava", "papaya", "watermelon", "pineapple", "fruit", "pear"]],
  ["SNACK",     ["biscuit", "chips", "murukku", "chakli", "popcorn", "pakoda", "pakora", "bajji", "bonda", "samosa", "cutlet"]],
  ["CURRY",     ["curry", "masala", "poriyal", "thoran", "sabzi", "sabji", "bhaji", "gravy", "roast", "palak", "paneer", "korma", "fry"]],
  ["VEGETABLE", ["vegetable", "greens", "salad", "spinach", "carrot", "beans", "peas", "broccoli", "cauliflower", "cabbage", "brinjal"]],
];

function classifyFood(name: string): string {
  const n = name.toLowerCase();
  for (const [cat, keywords] of CATEGORY_RULES) {
    for (const kw of keywords) {
      if (n.includes(kw)) return cat;
    }
  }
  return "GENERAL";
}

// ── Popular dishes per meal type ─────────────────────────────────────────────
type Dish = { name: string; label: string };

const POPULAR_BY_MEAL: Record<string, Dish[]> = {
  breakfast: [
    { name: "Idli",                    label: "⚪ Idli" },
    { name: "Masala dosa",             label: "🫓 Masala Dosa" },
    { name: "Plain dosa",              label: "🫓 Plain Dosa" },
    { name: "Medu vada",               label: "🍩 Medu Vada" },
    { name: "Upma",                    label: "🍚 Upma" },
    { name: "Pongal",                  label: "🍚 Pongal" },
    { name: "Poha",                    label: "🍚 Poha" },
    { name: "Uttapam",                 label: "🫓 Uttapam" },
    { name: "Sambar",                  label: "🍲 Sambar" },
    { name: "Coconut chutney",         label: "🥥 Coconut Chutney" },
    { name: "Hot tea (Garam Chai)",    label: "☕ Chai" },
    { name: "Coffee",                  label: "☕ Coffee" },
    { name: "Chapati",                 label: "🫓 Chapati" },
    { name: "Bread",                   label: "🍞 Bread" },
  ],
  lunch: [
    { name: "Boiled rice",             label: "🍚 Boiled Rice" },
    { name: "Sambar",                  label: "🍲 Sambar" },
    { name: "Rasam",                   label: "🍲 Rasam" },
    { name: "Dal",                     label: "🍲 Dal" },
    { name: "Curd rice",               label: "🍚 Curd Rice" },
    { name: "Lemon rice",              label: "🍚 Lemon Rice" },
    { name: "Mutton biryani",          label: "🍛 Mutton Biryani" },
    { name: "Chicken biryani",         label: "🍛 Chicken Biryani" },
    { name: "Chapati",                 label: "🫓 Chapati" },
    { name: "Palak paneer",            label: "🫕 Palak Paneer" },
    { name: "Chicken curry",           label: "🍗 Chicken Curry" },
    { name: "Papad",                   label: "🥙 Papad" },
    { name: "Pickle",                  label: "🫙 Pickle" },
    { name: "Curd",                    label: "🥛 Curd" },
  ],
  dinner: [
    { name: "Chapati",                 label: "🫓 Chapati" },
    { name: "Dal",                     label: "🍲 Dal" },
    { name: "Roti",                    label: "🫓 Roti" },
    { name: "Palak paneer",            label: "🫕 Palak Paneer" },
    { name: "Paneer butter masala",    label: "🫕 Paneer Butter Masala" },
    { name: "Chicken curry",           label: "🍗 Chicken Curry" },
    { name: "Mutton curry",            label: "🍗 Mutton Curry" },
    { name: "Egg curry",               label: "🍳 Egg Curry" },
    { name: "Boiled rice",             label: "🍚 Rice" },
    { name: "Sambar",                  label: "🍲 Sambar" },
    { name: "Raita",                   label: "🥛 Raita" },
    { name: "Payasam",                 label: "🍮 Payasam" },
  ],
  snack: [
    { name: "Medu vada",               label: "🍩 Medu Vada" },
    { name: "Samosa",                  label: "🥙 Samosa" },
    { name: "Pakoda",                  label: "🧆 Pakoda" },
    { name: "Murukku",                 label: "🧆 Murukku" },
    { name: "Banana chips",            label: "🍌 Banana Chips" },
    { name: "Poha",                    label: "🍚 Poha" },
    { name: "Upma",                    label: "🍚 Upma" },
    { name: "Bhel puri",               label: "🥙 Bhel Puri" },
    { name: "Bread pakoda",            label: "🧆 Bread Pakoda" },
    { name: "Cutlet",                  label: "🧆 Cutlet" },
    { name: "Sundal",                  label: "🫘 Sundal" },
    { name: "Gulab jamun",             label: "🍮 Gulab Jamun" },
  ],
  beverage: [
    { name: "Hot tea (Garam Chai)",    label: "☕ Masala Chai" },
    { name: "Coffee",                  label: "☕ Coffee" },
    { name: "Lassi",                   label: "🥛 Lassi" },
    { name: "Buttermilk",              label: "🥛 Buttermilk" },
    { name: "Mango juice",             label: "🥭 Mango Juice" },
    { name: "Lemon juice",             label: "🍋 Lemon Juice" },
    { name: "Coconut water",           label: "🥥 Coconut Water" },
    { name: "Milk",                    label: "🥛 Milk" },
    { name: "Iced tea",                label: "🧊 Iced Tea" },
    { name: "Badam milk",              label: "🥛 Badam Milk" },
  ],
};

// ── Quick meal templates ──────────────────────────────────────────────────────
const QUICK_MEALS = [
  { label: "South Indian Breakfast", icon: "🌅", foods: ["Idli", "Sambar", "Hot tea (Garam Chai)"] },
  { label: "Tamil Nadu Lunch",       icon: "🍽️", foods: ["Boiled rice", "Sambar", "Curd rice"] },
  { label: "Street Breakfast",       icon: "🥘", foods: ["Masala dosa", "Sambar", "Hot tea (Garam Chai)"] },
  { label: "Mini Tiffin",            icon: "🫕", foods: ["Idli", "Medu vada", "Sambar"] },
  { label: "North Indian Dinner",    icon: "🫓", foods: ["Chapati", "Dal"] },
];

// ── Smart companion suggestions ───────────────────────────────────────────────
const COMPANION_MAP: [string, string[]][] = [
  ["idli",      ["Sambar", "Coconut chutney", "Hot tea (Garam Chai)"]],
  ["dosa",      ["Sambar", "Coconut chutney", "Hot tea (Garam Chai)"]],
  ["uttapam",   ["Sambar", "Coconut chutney"]],
  ["pongal",    ["Sambar", "Coconut chutney"]],
  ["vada",      ["Sambar", "Coconut chutney"]],
  ["upma",      ["Coconut chutney", "Hot tea (Garam Chai)"]],
  ["poha",      ["Hot tea (Garam Chai)"]],
  ["sambar",    ["Boiled rice", "Idli"]],
  ["biryani",   ["Raita"]],
  ["chapati",   ["Dal", "Curd"]],
  ["roti",      ["Dal", "Curd"]],
  ["paratha",   ["Curd"]],
  ["rice",      ["Sambar", "Curd rice"]],
];

function getSuggestions(foods: string[]): string[] {
  if (!foods.length) return [];
  const last = foods[foods.length - 1].toLowerCase();
  for (const [kw, suggs] of COMPANION_MAP) {
    if (last.includes(kw)) {
      return suggs.filter(s => !foods.some(f => f.toLowerCase() === s.toLowerCase()));
    }
  }
  return [];
}

// ── Meal type selector ────────────────────────────────────────────────────────
const MEAL_TYPES = [
  { id: "breakfast", label: "Breakfast", icon: "🌅" },
  { id: "lunch",     label: "Lunch",     icon: "☀️" },
  { id: "dinner",    label: "Dinner",    icon: "🌙" },
  { id: "snack",     label: "Snack",     icon: "🫐" },
  { id: "beverage",  label: "Drink",     icon: "☕" },
];

// ── Types ─────────────────────────────────────────────────────────────────────
interface ComputedNutrition {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

interface MealItem {
  id: string;
  foodName: string;
  displayName: string;
  category: string;
  answers: Record<string, string>;
  base: FoodNutrition;
  computed: ComputedNutrition;
}

function applyMultipliers(base: FoodNutrition, template: FoodTemplate, answers: Record<string, string>): ComputedNutrition {
  let m = 1.0;
  for (const q of template.questions) {
    const ans = answers[q.id];
    if (ans !== undefined && q.multipliers[ans] !== undefined) m *= q.multipliers[ans];
  }
  return {
    calories: Math.round(base.calories * m * 10) / 10,
    protein:  Math.round(base.protein  * m * 10) / 10,
    carbs:    Math.round(base.carbs    * m * 10) / 10,
    fat:      Math.round(base.fat      * m * 10) / 10,
  };
}

function sumNutrition(items: MealItem[]): ComputedNutrition {
  return items.reduce(
    (a, i) => ({
      calories: a.calories + i.computed.calories,
      protein:  a.protein  + i.computed.protein,
      carbs:    a.carbs    + i.computed.carbs,
      fat:      a.fat      + i.computed.fat,
    }),
    { calories: 0, protein: 0, carbs: 0, fat: 0 },
  );
}

// ── Component ─────────────────────────────────────────────────────────────────
interface Props {
  onAnalysisStart: () => void;
}

export function ManualInputStep({ onAnalysisStart }: Props) {
  const router = useRouter();

  // browse state
  const [mealType, setMealType]         = useState("breakfast");
  const [showTemplates, setShowTemplates] = useState(false);
  const [mealItems, setMealItems]       = useState<MealItem[]>([]);
  const [inputValue, setInputValue]     = useState("");
  const [suggestions, setSuggestions]   = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [submitting, setSubmitting]     = useState(false);

  // food detail state
  const [addingFood, setAddingFood]     = useState<FoodNutrition | null>(null);
  const [addingAnswers, setAddingAnswers] = useState<Record<string, string>>({});
  const [loadingFood, setLoadingFood]   = useState(false);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef    = useRef<HTMLInputElement>(null);

  const companions   = getSuggestions(mealItems.map(i => i.displayName));
  const total        = sumNutrition(mealItems);

  // autocomplete
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (inputValue.length < 2) { setSuggestions([]); setShowSuggestions(false); return; }
    debounceRef.current = setTimeout(async () => {
      try {
        const res = await foodAutocomplete(inputValue);
        setSuggestions(res);
        setShowSuggestions(res.length > 0);
      } catch { /* silent */ }
    }, 250);
  }, [inputValue]);

  // default answers for a template
  function defaultAnswers(template: FoodTemplate): Record<string, string> {
    return Object.fromEntries(
      template.questions.map(q => [q.id, q.options[Math.min(1, q.options.length - 1)]])
    );
  }

  // select a food from autocomplete → load nutrition + switch to detail view
  async function selectFood(name: string) {
    setShowSuggestions(false);
    setInputValue("");
    setLoadingFood(true);
    try {
      const data = await getFoodNutrition(name);
      const defaults = defaultAnswers(data.template);
      setAddingFood(data);
      setAddingAnswers(defaults);
    } catch {
      toast({ title: "Could not load food data", variant: "destructive" });
    } finally {
      setLoadingFood(false);
    }
  }

  // confirm adding food with current answers → back to browse
  function confirmAddFood() {
    if (!addingFood) return;
    const computed = applyMultipliers(addingFood, addingFood.template, addingAnswers);
    setMealItems(prev => [
      ...prev,
      {
        id:          crypto.randomUUID(),
        foodName:    addingFood.food_name,
        displayName: addingFood.food_name,
        category:    addingFood.category,
        answers:     { ...addingAnswers },
        base:        addingFood,
        computed,
      },
    ]);
    setAddingFood(null);
    setAddingAnswers({});
    inputRef.current?.focus();
  }

  // add from quick template (use default answers)
  async function addQuickMealFoods(foods: string[]) {
    setShowTemplates(false);
    const newFoods = foods.filter(f => !mealItems.some(i => i.displayName.toLowerCase() === f.toLowerCase()));
    for (const name of newFoods) {
      try {
        const data = await getFoodNutrition(name);
        const defaults = defaultAnswers(data.template);
        const computed = applyMultipliers(data, data.template, defaults);
        setMealItems(prev => [
          ...prev,
          { id: crypto.randomUUID(), foodName: data.food_name, displayName: data.food_name,
            category: data.category, answers: defaults, base: data, computed },
        ]);
      } catch { /* skip unknown */ }
    }
  }

  function removeItem(id: string) {
    setMealItems(prev => prev.filter(i => i.id !== id));
  }

  function updateAnswer(qId: string, value: string) {
    if (!addingFood) return;
    const next = { ...addingAnswers, [qId]: value };
    setAddingAnswers(next);
  }

  async function handleCalculate() {
    if (!mealItems.length) return;
    setSubmitting(true);
    onAnalysisStart();
    try {
      const result = await manualAnalyzeComplete({
        meal_type: mealType,
        items: mealItems.map(i => ({
          food_name: i.foodName,
          category:  i.category,
          answers:   i.answers,
        })),
      });
      router.push(`/results/${result.meal_id}`);
    } catch {
      toast({ title: "Calculation failed", description: "Please try again.", variant: "destructive" });
      setSubmitting(false);
    }
  }

  const livePreview = addingFood
    ? applyMultipliers(addingFood, addingFood.template, addingAnswers)
    : null;

  // ── Food Detail Panel ──────────────────────────────────────────────────────
  if (addingFood) {
    return (
      <motion.div
        key="detail"
        initial={{ opacity: 0, x: 24 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -24 }}
        className="space-y-4"
      >
        <button
          type="button"
          onClick={() => { setAddingFood(null); setAddingAnswers({}); }}
          className="flex items-center gap-1.5 font-body text-sm text-dark/60 hover:text-dark transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" /> Back to meal
        </button>

        {/* Food header */}
        <div className="bg-card rounded-2xl border border-border/50 p-5 shadow-soft">
          <div className="flex items-start gap-3 mb-1">
            <span className="text-3xl">{CATEGORY_ICONS[addingFood.category] ?? "🍽️"}</span>
            <div>
              <h3 className="font-heading text-lg font-bold text-dark leading-tight">{addingFood.food_name}</h3>
              <p className="font-body text-xs text-dark/50 mt-0.5">{addingFood.servings_unit}</p>
            </div>
          </div>
        </div>

        {/* Template questions */}
        <div className="bg-card rounded-2xl border border-border/50 p-5 shadow-soft space-y-5">
          {addingFood.template.questions.map(q => (
            <div key={q.id}>
              <p className="font-body text-sm font-semibold text-dark mb-2.5">{q.label}</p>
              <div className="flex flex-wrap gap-2">
                {q.options.map(opt => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => updateAnswer(q.id, opt)}
                    className={cn(
                      "px-4 py-2 rounded-xl border-2 font-body text-sm font-medium transition-all duration-200 cursor-pointer",
                      addingAnswers[q.id] === opt
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border bg-muted/50 text-dark/70 hover:border-primary/30 hover:bg-primary/5"
                    )}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Live nutrition preview */}
        {livePreview && (
          <motion.div
            key={JSON.stringify(addingAnswers)}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-primary/5 border border-primary/20 rounded-2xl p-4"
          >
            <p className="font-body text-xs text-primary font-semibold uppercase tracking-wide mb-3">
              Estimated Nutrition
            </p>
            <div className="grid grid-cols-4 gap-3">
              {([
                ["Calories", livePreview.calories, "kcal", "text-primary"],
                ["Protein",  livePreview.protein,  "g",    "text-accent"],
                ["Carbs",    livePreview.carbs,     "g",    "text-secondary"],
                ["Fat",      livePreview.fat,       "g",    "text-dark/60"],
              ] as [string, number, string, string][]).map(([label, val, unit, cls]) => (
                <div key={label} className="text-center">
                  <p className={cn("font-heading text-lg font-bold", cls)}>{val}</p>
                  <p className="font-body text-xs text-dark/40">{unit}</p>
                  <p className="font-body text-xs text-dark/50">{label}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        <div className="flex gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => { setAddingFood(null); setAddingAnswers({}); }}
          >
            Cancel
          </Button>
          <Button className="flex-1" onClick={confirmAddFood}>
            <Plus className="w-4 h-4" />
            Add to Meal
          </Button>
        </div>
      </motion.div>
    );
  }

  // ── Browse Panel ───────────────────────────────────────────────────────────
  return (
    <motion.div
      key="browse"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      className="space-y-4"
    >
      {/* Meal type */}
      <div className="bg-card rounded-2xl border border-border/50 p-4 shadow-soft">
        <p className="font-body text-xs text-dark/50 uppercase tracking-wide font-medium mb-3">Meal Type</p>
        <div className="flex gap-2 flex-wrap">
          {MEAL_TYPES.map(mt => (
            <button
              key={mt.id}
              type="button"
              onClick={() => setMealType(mt.id)}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-body text-sm font-medium transition-all duration-200 cursor-pointer",
                mealType === mt.id
                  ? "bg-primary text-white shadow-soft"
                  : "bg-muted text-dark/60 hover:bg-primary/10 hover:text-primary"
              )}
            >
              <span>{mt.icon}</span>{mt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Quick templates */}
      <div className="bg-card rounded-2xl border border-border/50 shadow-soft overflow-hidden">
        <button
          type="button"
          onClick={() => setShowTemplates(v => !v)}
          className="w-full flex items-center justify-between p-4 font-body text-sm font-medium text-dark/70 hover:text-dark transition-colors cursor-pointer"
        >
          <span className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-primary" />
            Quick Meal Templates — one click to add a full set
          </span>
          {showTemplates ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        <AnimatePresence>
          {showTemplates && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="px-4 pb-4 grid grid-cols-1 gap-2">
                {QUICK_MEALS.map(meal => (
                  <button
                    key={meal.label}
                    type="button"
                    onClick={() => addQuickMealFoods(meal.foods)}
                    className="flex items-center gap-3 p-3 rounded-xl border border-border/50 hover:border-primary/30 hover:bg-primary/5 transition-all text-left cursor-pointer group"
                  >
                    <span className="text-xl shrink-0">{meal.icon}</span>
                    <div className="min-w-0">
                      <p className="font-body text-sm font-semibold text-dark group-hover:text-primary transition-colors">{meal.label}</p>
                      <p className="font-body text-xs text-dark/40 truncate">{meal.foods.join(" · ")}</p>
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Search */}
      <div className="bg-card rounded-2xl border border-border/50 p-5 shadow-soft">
        <p className="font-body text-sm text-dark/60 mb-3">
          Search by name — click a result to configure portions
        </p>
        <div className="relative">
          {loadingFood && (
            <div className="absolute inset-0 bg-background/60 rounded-xl flex items-center justify-center z-10">
              <Loader2 className="w-5 h-5 text-primary animate-spin" />
            </div>
          )}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark/30 pointer-events-none" />
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && suggestions.length > 0) { e.preventDefault(); selectFood(suggestions[0]); }
                  if (e.key === "Escape") setShowSuggestions(false);
                }}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                placeholder="e.g. Masala Dosa, Idli, Sambar…"
                className="w-full pl-9 pr-4 py-3 rounded-xl border border-border bg-background font-body text-sm text-dark placeholder:text-dark/30 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />

              {/* Dropdown */}
              <AnimatePresence>
                {showSuggestions && suggestions.length > 0 && (
                  <motion.ul
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    transition={{ duration: 0.15 }}
                    className="absolute z-20 top-full mt-1 left-0 right-0 bg-card border border-border rounded-xl shadow-lg overflow-hidden max-h-72 overflow-y-auto"
                  >
                    {suggestions.map((s, i) => {
                      const cat  = classifyFood(s);
                      const icon = CATEGORY_ICONS[cat] ?? "🍽️";
                      return (
                        <li key={s}>
                          <button
                            type="button"
                            onMouseDown={() => selectFood(s)}
                            className={cn(
                              "w-full flex items-center gap-3 px-4 py-2.5 font-body text-sm text-dark transition-colors cursor-pointer",
                              i === 0 ? "bg-primary/5 text-primary" : "hover:bg-primary/5 hover:text-primary"
                            )}
                          >
                            <span className="text-base shrink-0">{icon}</span>
                            <span className="flex-1 text-left">{s}</span>
                            <span className="text-xs text-dark/30 shrink-0 capitalize">{cat.toLowerCase()}</span>
                          </button>
                        </li>
                      );
                    })}
                  </motion.ul>
                )}
              </AnimatePresence>
            </div>
          </div>
          {inputValue.length >= 2 && suggestions.length === 0 && !loadingFood && (
            <p className="font-body text-xs text-dark/40 mt-2">No matches — try a different term</p>
          )}
          {inputValue.length < 2 && (
            <p className="font-body text-xs text-dark/40 mt-2">Type at least 2 characters to search 1,014 Indian foods</p>
          )}
        </div>

        {/* Popular dishes — change with meal type */}
        {inputValue.length < 2 && (
          <div className="mt-4">
            <p className="font-body text-xs text-dark/50 uppercase tracking-wide font-medium mb-2.5">
              Popular for {MEAL_TYPES.find(m => m.id === mealType)?.label}
            </p>
            <AnimatePresence mode="wait">
              <motion.div
                key={mealType}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.18 }}
                className="flex flex-wrap gap-2"
              >
                {(POPULAR_BY_MEAL[mealType] ?? []).map(dish => {
                  const alreadyAdded = mealItems.some(
                    i => i.displayName.toLowerCase() === dish.name.toLowerCase()
                  );
                  return (
                    <button
                      key={dish.name}
                      type="button"
                      disabled={alreadyAdded || loadingFood}
                      onClick={() => selectFood(dish.name)}
                      className={cn(
                        "px-3 py-1.5 rounded-full font-body text-sm font-medium border transition-all duration-200 cursor-pointer select-none",
                        alreadyAdded
                          ? "bg-primary/10 text-primary border-primary/30 cursor-default opacity-60"
                          : "bg-muted border-border/60 text-dark/70 hover:bg-primary/10 hover:text-primary hover:border-primary/30 active:scale-95"
                      )}
                    >
                      {alreadyAdded ? "✓ " : ""}{dish.label}
                    </button>
                  );
                })}
              </motion.div>
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Smart companion suggestions */}
      <AnimatePresence>
        {companions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-accent/5 border border-accent/20 rounded-2xl p-4">
              <p className="font-body text-xs text-accent font-semibold uppercase tracking-wide mb-2.5">
                You might also add:
              </p>
              <div className="flex flex-wrap gap-2">
                {companions.map(s => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => selectFood(s)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent/10 text-accent font-body text-sm font-medium hover:bg-accent/20 transition-colors cursor-pointer border border-accent/20"
                  >
                    <Plus className="w-3 h-3" />
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Meal cart */}
      <AnimatePresence>
        {mealItems.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden space-y-3"
          >
            <p className="font-body text-xs text-dark/50 uppercase tracking-wide font-medium">
              {mealItems.length} {mealItems.length === 1 ? "item" : "items"} in your{" "}
              {MEAL_TYPES.find(m => m.id === mealType)?.label.toLowerCase()}
            </p>

            {/* Food cards */}
            <div className="space-y-2">
              <AnimatePresence>
                {mealItems.map(item => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, y: -8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: 20, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="bg-card rounded-xl border border-border/50 px-4 py-3 flex items-center gap-3"
                  >
                    <span className="text-xl shrink-0">{CATEGORY_ICONS[item.category] ?? "🍽️"}</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-body text-sm font-semibold text-dark truncate">{item.displayName}</p>
                      <p className="font-body text-xs text-dark/40">
                        {Object.values(item.answers).join(" · ")}
                      </p>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <div className="text-right">
                        <p className="font-body text-sm font-bold text-primary">{item.computed.calories}</p>
                        <p className="font-body text-xs text-dark/40">kcal</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeItem(item.id)}
                        className="w-6 h-6 rounded-full hover:bg-red-50 flex items-center justify-center transition-colors cursor-pointer text-dark/30 hover:text-red-500"
                        aria-label={`Remove ${item.displayName}`}
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* Running total bar */}
            <div className="bg-dark rounded-2xl p-4">
              <div className="grid grid-cols-4 gap-2 text-center">
                {([
                  ["Calories", Math.round(total.calories), "kcal"],
                  ["Protein",  Math.round(total.protein * 10) / 10, "g"],
                  ["Carbs",    Math.round(total.carbs   * 10) / 10, "g"],
                  ["Fat",      Math.round(total.fat     * 10) / 10, "g"],
                ] as [string, number, string][]).map(([label, val, unit]) => (
                  <div key={label}>
                    <p className="font-heading text-lg font-bold text-white">{val}</p>
                    <p className="font-body text-xs text-white/40">{unit}</p>
                    <p className="font-body text-xs text-white/60">{label}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* CTA */}
      <Button
        size="lg"
        className="w-full"
        onClick={handleCalculate}
        disabled={mealItems.length === 0 || submitting}
      >
        {submitting ? (
          <><Loader2 className="w-4 h-4 animate-spin" />Calculating nutrition…</>
        ) : (
          <><Flame className="w-4 h-4" />
            {mealItems.length > 0
              ? `Get Nutrition Report — ${mealItems.length} item${mealItems.length > 1 ? "s" : ""}`
              : "Add foods to get started"}
          </>
        )}
      </Button>

      {mealItems.length === 0 && (
        <p className="text-center font-body text-xs text-dark/40">
          Search for foods above or use a quick template
        </p>
      )}
    </motion.div>
  );
}
