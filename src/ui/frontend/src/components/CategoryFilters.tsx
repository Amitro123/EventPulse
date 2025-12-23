import { Music, Trophy, Palette, Users, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface Category {
  id: string;
  name: string;
  icon: LucideIcon;
  count: number;
  color: string;
}

const categories: Category[] = [
  { id: "music", name: "Concerts & Music", icon: Music, count: 4250, color: "from-primary to-orange-400" },
  { id: "sports", name: "Sports", icon: Trophy, count: 2180, color: "from-emerald-500 to-teal-400" },
  { id: "arts", name: "Arts & Theater", icon: Palette, count: 1340, color: "from-accent to-pink-500" },
  { id: "family", name: "Family Events", icon: Users, count: 890, color: "from-blue-500 to-cyan-400" },
];

interface CategoryFiltersProps {
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
}

const CategoryFilters = ({ selectedCategory, onCategoryChange }: CategoryFiltersProps) => {
  return (
    <section className="py-16 relative">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">
            Browse by <span className="gradient-text">Category</span>
          </h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Explore thousands of events across different categories
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          {categories.map((category) => {
            const Icon = category.icon;
            const isSelected = selectedCategory === category.id;

            return (
              <button
                key={category.id}
                onClick={() => onCategoryChange(isSelected ? null : category.id)}
                className={cn(
                  "group glass-card p-6 md:p-8 text-left transition-all duration-300 hover:-translate-y-2",
                  isSelected && "ring-2 ring-primary bg-primary/10"
                )}
              >
                <div
                  className={cn(
                    "w-14 h-14 rounded-xl flex items-center justify-center mb-4 transition-all duration-300",
                    `bg-gradient-to-br ${category.color}`,
                    "group-hover:scale-110 group-hover:shadow-lg"
                  )}
                >
                  <Icon className="w-7 h-7 text-primary-foreground" />
                </div>
                <h3 className="font-display font-semibold text-lg mb-1">{category.name}</h3>
                <p className="text-sm text-muted-foreground">
                  {category.count.toLocaleString()} events
                </p>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default CategoryFilters;
