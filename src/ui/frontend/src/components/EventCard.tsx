import { Calendar, MapPin, Clock, ExternalLink, Package } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface Event {
  id: string;
  name: string;
  artist?: string;
  date: string;
  time: string;
  venue: string;
  city: string;
  category: string;
  minPrice: number;
  maxPrice: number;
  currency: string;
  image: string;
  ticketUrl?: string;
  provider?: string; // "viagogo" or "ticketmaster"
}

interface EventCardProps {
  event: Event;
  onViewPackage: (eventId: string) => void;
}

const EventCard = ({ event, onViewPackage }: EventCardProps) => {
  const formatPrice = (min: number, max: number, currency: string) => {
    if (min === max) return `${currency}${min}`;
    return `${currency}${min} - ${currency}${max}`;
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "music":
        return "from-primary to-orange-400";
      case "sports":
        return "from-emerald-500 to-teal-400";
      case "arts":
        return "from-accent to-pink-500";
      case "family":
        return "from-blue-500 to-cyan-400";
      default:
        return "from-primary to-orange-400";
    }
  };

  return (
    <div className="group glass-card overflow-hidden transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl">
      {/* Image */}
      <div className="relative h-48 overflow-hidden">
        {/* Source Badge */}
        {event.provider && (
          <div className="absolute top-2 right-2 z-10">
            <span className="px-2 py-1 text-xs font-medium rounded-full bg-black/60 backdrop-blur-sm text-white border border-white/20">
              Source: {event.provider === 'viagogo' ? 'Viagogo' : 'Ticketmaster'}
            </span>
          </div>
        )}
        <img
          src={event.image}
          alt={event.name}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-card via-transparent to-transparent" />

        {/* Category Badge */}
        <div
          className={cn(
            "absolute top-4 left-4 px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r text-primary-foreground",
            getCategoryColor(event.category)
          )}
        >
          {event.category.charAt(0).toUpperCase() + event.category.slice(1)}
        </div>

        {/* Price Badge */}
        <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-background/80 backdrop-blur-sm text-sm font-semibold">
          {formatPrice(event.minPrice, event.maxPrice, event.currency)}
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        <h3 className="font-display font-bold text-lg mb-1 line-clamp-1 group-hover:text-primary transition-colors">
          {event.name}
        </h3>
        {event.artist && (
          <p className="text-primary text-sm font-medium mb-3">{event.artist}</p>
        )}

        <div className="space-y-2 mb-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="w-4 h-4" />
            <span>{event.date}</span>
            <Clock className="w-4 h-4 ml-2" />
            <span>{event.time}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="w-4 h-4" />
            <span className="line-clamp-1">{event.venue}, {event.city}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button
            variant="gradient"
            size="sm"
            className="flex-1"
            onClick={() => onViewPackage(event.id)}
          >
            <Package className="w-4 h-4" />
            View Package
          </Button>
          {event.ticketUrl && (
            <Button
              variant="outline"
              size="sm"
              asChild
            >
              <a href={event.ticketUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4" />
              </a>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default EventCard;
