import { Search, MapPin, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import heroImage from "@/assets/hero-concert.jpg";

interface HeroSectionProps {
  onSearch: (query: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  isLoading?: boolean;
  resultCount?: number;
}

const HeroSection = ({ onSearch, searchQuery, onSearchChange, isLoading = false, resultCount }: HeroSectionProps) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchQuery);
  };

  return (
    <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0">
        <img
          src={heroImage}
          alt="Concert crowd with vibrant stage lighting"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-background/40" />
        <div className="absolute inset-0 bg-hero-pattern" />
      </div>

      {/* Floating Orbs */}
      <div className="absolute top-20 left-10 w-64 h-64 bg-primary/20 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/15 rounded-full blur-3xl animate-float" style={{ animationDelay: "-3s" }} />

      <div className="relative z-10 container mx-auto px-4 text-center">
        {/* Badge */}
        <div className="animate-slide-up inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/80 backdrop-blur-sm border border-border/50 mb-8">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span className="text-sm text-muted-foreground">Discover Live Events Near You</span>
        </div>

        {/* Main Heading */}
        <h1 className="animate-slide-up-delay-1 font-display text-5xl md:text-7xl lg:text-8xl font-bold mb-6 tracking-tight">
          Feel The
          <span className="gradient-text"> Pulse</span>
          <br />
          Of Live Events
        </h1>

        <p className="animate-slide-up-delay-2 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
          Find concerts, sports events, and experiences. Get tickets and nearby hotels in one seamless package.
        </p>

        {/* Search Form */}
        <form onSubmit={handleSubmit} className="animate-slide-up-delay-3 max-w-3xl mx-auto mb-12">
          <div className="glass-card p-2 flex flex-col md:flex-row gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                placeholder="Search artists, events, or venues..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className="pl-12 bg-transparent border-0 focus:ring-0"
              />
            </div>
            <div className="hidden md:flex items-center gap-2 px-4 border-l border-border/50">
              <MapPin className="w-5 h-5 text-muted-foreground" />
              <span className="text-muted-foreground">All Locations</span>
            </div>
            <Button type="submit" variant="hero" size="lg" disabled={isLoading}>
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
              {isLoading ? "Searching..." : "Search Events"}
            </Button>
          </div>

          {/* Result Count Subtitle */}
          {!isLoading && searchQuery && resultCount !== undefined && (
            <div className="mt-4 animate-fade-in text-muted-foreground font-medium">
              {resultCount === 0
                ? `No events found for "${searchQuery}"`
                : `Found ${resultCount} events for "${searchQuery}"`}
            </div>
          )}
        </form>

        {/* Quick Stats */}
        <div className="animate-slide-up-delay-3 mt-8 flex flex-wrap justify-center gap-8 md:gap-16">
          <div className="text-center">
            <div className="text-3xl md:text-4xl font-bold gradient-text">10K+</div>
            <div className="text-sm text-muted-foreground">Live Events</div>
          </div>
          <div className="text-center">
            <div className="text-3xl md:text-4xl font-bold gradient-text">500+</div>
            <div className="text-sm text-muted-foreground">Cities</div>
          </div>
          <div className="text-center">
            <div className="text-3xl md:text-4xl font-bold gradient-text">1M+</div>
            <div className="text-sm text-muted-foreground">Happy Fans</div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 rounded-full border-2 border-muted-foreground/30 flex items-start justify-center p-2">
          <div className="w-1.5 h-3 rounded-full bg-primary animate-pulse" />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
