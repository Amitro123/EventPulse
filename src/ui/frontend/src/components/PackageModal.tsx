import { X, Calendar, MapPin, Clock, ExternalLink, Hotel, Ticket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Event } from "./EventCard";

interface PackageModalProps {
  event: Event | null;
  packageData?: any; // Package data from API
  isLoading?: boolean;
  isOpen: boolean;
  onClose: () => void;
}

const PackageModal = ({ event, packageData, isLoading = false, isOpen, onClose }: PackageModalProps) => {
  if (!isOpen || !event) return null;

  const formatPrice = (min: number, max: number, currency: string) => {
    if (min === max) return `${currency}${min}`;
    return `${currency}${min} - ${currency}${max}`;
  };

  // Generate Booking.com affiliate URL (mock)
  const hotelUrl = `https://www.booking.com/searchresults.html?ss=${encodeURIComponent(event.city)}&checkin=${event.timestamp}&checkout=${event.timestamp}&aid=TEST_AID`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative glass-card max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-slide-up">
        {/* Close Button */}
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg hover:bg-secondary transition-colors z-50 bg-black/20 backdrop-blur-sm"
        >
          <X className="w-5 h-5 text-white" />
        </button>

        {/* Header Image */}
        <div className="relative h-56 overflow-hidden rounded-t-xl">
          <img
            src={event.image_url || "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800&q=80"}
            alt={event.text}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-card via-transparent to-transparent" />
        </div>

        {/* Content */}
        <div className="p-6">
          <h2 className="font-display text-2xl font-bold mb-2">{event.text}</h2>

          <div className="space-y-3 mb-6">
            <div className="flex items-center gap-3 text-muted-foreground">
              <Calendar className="w-5 h-5" />
              <span>{event.timestamp}</span>
              <Clock className="w-5 h-5 ml-2" />
              <span>TBD</span>
            </div>
            <div className="flex items-center gap-3 text-muted-foreground">
              <MapPin className="w-5 h-5" />
              <span>{event.venue_name}, {event.city}</span>
            </div>
          </div>

          {/* Package Options */}
          <div className="space-y-4">
            <h3 className="font-display font-semibold text-lg">Your Event Package</h3>

            {/* Tickets */}
            <div className="glass-card p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-orange-400 flex items-center justify-center">
                  <Ticket className="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                  <p className="font-semibold">Event Tickets</p>
                  <p className="text-sm text-muted-foreground">
                    {formatPrice(event.min_price, event.max_price, event.currency)}
                  </p>
                </div>
              </div>
              {/* Show ticket provider info if available */}
              {packageData?.tickets?.ticket_provider ? (
                <Button variant="gradient" size="sm" asChild disabled={!packageData.tickets.url}>
                  <a href={packageData.tickets.url || "#"} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="w-4 h-4" />
                    Buy Tickets
                    <span className="ml-2 text-xs opacity-75">
                      (Tickets via {packageData.tickets.ticket_provider === 'viagogo' ? 'Viagogo' :
                        packageData.tickets.ticket_provider === 'ticketmaster' ? 'Ticketmaster' :
                          packageData.tickets.ticket_provider})
                    </span>
                  </a>
                </Button>
              ) : packageData?.tickets?.url === null ? (
                <div className="text-sm text-muted-foreground">Tickets not available</div>
              ) : (
                <Button variant="gradient" size="sm" asChild>
                  <a href={event?.url || "#"} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="w-4 h-4" />
                    Buy Tickets
                  </a>
                </Button>
              )}
            </div>

            {/* Hotels */}
            <div className="glass-card p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent to-pink-500 flex items-center justify-center">
                  <Hotel className="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                  <p className="font-semibold">Nearby Hotels</p>
                  <p className="text-sm text-muted-foreground">
                    Hotels in {event.city}
                  </p>
                </div>
              </div>
              <Button variant="outline" size="sm" asChild>
                <a href={hotelUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4" />
                  Search Hotels
                </a>
              </Button>
            </div>
          </div>

          {/* CTA */}
          <div className="mt-6 pt-6 border-t border-border/50">
            <p className="text-sm text-muted-foreground text-center">
              Affiliate links help support EventPulse at no extra cost to you
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PackageModal;
