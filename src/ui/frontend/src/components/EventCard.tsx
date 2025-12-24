import { Calendar, MapPin, Clock, ExternalLink, Package } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface Event {
  id: string;
  text: string; // Backend sends 'text', mapped to name in UI
  venue_name: string;
  city: string;
  date: string; // timestamp in backend
  timestamp: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  currency?: string;
  image_url?: string;
  url?: string; // ticket url
  provider?: string; // "viagogo" or "ticketmaster"
  ticket_provider?: string; // "ticketmaster", "viagogo", etc.
  has_tickets?: boolean;
}

interface EventCardProps {
  event: Event;
  onViewPackage: (eventId: string) => void;
}

const EventCard = ({ event, onViewPackage }: EventCardProps) => {
  const formatPrice = (min?: number, max?: number, currency?: string, hasTickets?: boolean) => {
    if (!min || !currency) {
      if (hasTickets) return "Prices available on Ticketmaster";
      return "Price not available";
    }
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
        <img
          src={event.image_url || "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800&q=80"}
          alt={event.text}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-60 transition-opacity group-hover:opacity-40" />

        <div className="absolute top-2 left-2">
          <div className={`px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r ${getCategoryColor(event.category || 'music')} text-white shadow-lg`}>
            {event.category || 'Event'}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-5 flex flex-col h-[calc(100%-12rem)]">
        <div className="mb-4">
          <h3 className="font-display font-bold text-xl leading-tight mb-2 line-clamp-2 group-hover:text-primary transition-colors">
            {event.text}
          </h3>
          {/* Backend doesn't always separate artist, so we rely on text */}
        </div>

        <div className="space-y-2 mb-auto">
          <div className="flex items-center text-sm text-muted-foreground">
            <Calendar className="w-4 h-4 mr-2 text-primary" />
            <span className="truncate">{event.timestamp}</span>
          </div>
          <div className="flex items-center text-sm text-muted-foreground">
            <Clock className="w-4 h-4 mr-2 text-primary" />
            <span className="truncate">TBD</span>
          </div>
          <div className="flex items-center text-sm text-muted-foreground">
            <MapPin className="w-4 h-4 mr-2 text-primary" />
            <span className="truncate">{event.venue_name}, {event.city}</span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-border/50 space-y-3">
          {/* Price Line - Fixed height and font size */}
          <div className="h-6 flex items-center">
            <span className="text-sm font-medium text-foreground/80">
              {formatPrice(event.min_price, event.max_price, event.currency, event.has_tickets)}
            </span>
          </div>

          {/* Buttons Row */}
          <div className="flex items-center gap-2">
            <Button
              variant="gradient"
              size="sm"
              className="flex-1"
              onClick={(e) => {
                e.stopPropagation();
                onViewPackage(event.id);
              }}
            >
              <Package className="w-4 h-4 mr-2" />
              View Package
            </Button>

            {event.ticket_provider === 'ticketmaster' && event.url && event.url.toLowerCase().includes('ticketmaster') && (
              <Button
                variant="outline"
                size="sm"
                asChild
                onClick={(e) => e.stopPropagation()}
                className="flex-1"
              >
                <a href={event.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Direct
                </a>
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventCard;
