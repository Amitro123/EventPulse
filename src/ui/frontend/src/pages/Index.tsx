import { useState, useRef, useEffect } from "react";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import CategoryFilters from "@/components/CategoryFilters";
import EventsGrid from "@/components/EventsGrid";
import PackageModal from "@/components/PackageModal";
import Footer from "@/components/Footer";
import { useSearchEvents, useEventPackage } from "@/hooks/useEvents";
import { Event } from "@/components/EventCard";

const Index = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isPackageModalOpen, setIsPackageModalOpen] = useState(false);
  const [shouldScroll, setShouldScroll] = useState(false);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Debounce search query could be added here for optimization, but for now passing directly
  const { events, isLoading, error, hasMore, loadMore } = useSearchEvents(searchQuery, selectedCategory);

  // Auto-scroll to results when they load after an explicit search
  useEffect(() => {
    if (shouldScroll && !isLoading && events && events.length > 0) {
      // Small timeout to ensure DOM is ready
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        setShouldScroll(false);
      }, 100);
    }
  }, [events, isLoading, shouldScroll]);

  // Fetch package data when an event is selected
  const { data: packageData, isLoading: isPackageLoading } = useEventPackage(
    selectedEvent?.id,
    isPackageModalOpen
  );

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setShouldScroll(true);
  };

  const handleViewPackage = (eventId: string) => {
    const event = events?.find((e) => e.id === eventId);
    if (event) {
      setSelectedEvent(event);
      setIsPackageModalOpen(true);
    }
  };

  const handleClosePackage = () => {
    setIsPackageModalOpen(false);
    setSelectedEvent(null);
  };

  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <HeroSection
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSearch={handleSearch}
        isLoading={isLoading}
        resultCount={events?.length}
      />

      <div ref={resultsRef} className="scroll-mt-20">
        <CategoryFilters
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
        />

        {error ? (
          <div className="container mx-auto px-4 py-8 text-center text-red-500">
            Error fetching events: {(error as Error).message}
          </div>
        ) : isLoading ? (
          <div className="container mx-auto px-4 py-16 text-center">
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
              <p className="text-lg text-muted-foreground animate-pulse">Finding the best events for you...</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-8 pb-12">
            <EventsGrid
              events={events || []}
              onViewPackage={handleViewPackage}
              title={searchQuery ? `Results for "${searchQuery}"` : "Featured Events"}
              subtitle={searchQuery ? "found matching events" : "Discover the hottest events happening near you"}
            />

            {hasMore && (
              <button
                onClick={() => loadMore()}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-full font-medium hover:bg-primary/90 transition-colors"
              >
                Load More Events
              </button>
            )}
          </div>
        )}
      </div>

      <Footer />

      <PackageModal
        event={selectedEvent}
        packageData={packageData}
        isLoading={isPackageLoading}
        isOpen={isPackageModalOpen}
        onClose={handleClosePackage}
      />
    </main>
  );
};



export default Index;
