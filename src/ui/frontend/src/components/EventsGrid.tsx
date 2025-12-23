import EventCard, { Event } from "./EventCard";

interface EventsGridProps {
  events: Event[];
  onViewPackage: (eventId: string) => void;
  title?: string;
  subtitle?: string;
}

const EventsGrid = ({ events, onViewPackage, title = "Featured Events", subtitle }: EventsGridProps) => {
  if (events.length === 0) {
    return (
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🎭</div>
            <h3 className="font-display text-2xl font-bold mb-2">No Events Found</h3>
            <p className="text-muted-foreground">Try adjusting your search or filters</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 relative">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-primary/5 rounded-full blur-3xl pointer-events-none" />

      <div className="container mx-auto px-4 relative">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between mb-12">
          <div>
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-2">
              {title.split(" ").map((word, i) => 
                i === title.split(" ").length - 1 ? (
                  <span key={i} className="gradient-text">{word}</span>
                ) : (
                  <span key={i}>{word} </span>
                )
              )}
            </h2>
            {subtitle && (
              <p className="text-muted-foreground">{subtitle}</p>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-4 md:mt-0">
            Showing {events.length} events
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {events.map((event) => (
            <EventCard key={event.id} event={event} onViewPackage={onViewPackage} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default EventsGrid;
