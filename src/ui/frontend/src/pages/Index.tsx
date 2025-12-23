import { useState } from "react";
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

  // Debounce search query could be added here for optimization, but for now passing directly
  const { data: events, isLoading, error } = useSearchEvents(searchQuery, selectedCategory);

  // Fetch package data when an event is selected
  const { data: packageData, isLoading: isPackageLoading } = useEventPackage(
    selectedEvent?.id,
    isPackageModalOpen
  );

  const handleSearch = (query: string) => {
    setSearchQuery(query);
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
      />

      <CategoryFilters
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
      />

      {error ? (
        <div className="container mx-auto px-4 py-8 text-center text-red-500">
          Error fetching events: {(error as Error).message}
        </div>
      ) : isLoading ? (
        <div className="container mx-auto px-4 py-8 text-center">
          Loading events...
        </div>
      ) : (
        <EventsGrid
          events={events || []}
          onViewPackage={handleViewPackage}
          title={searchQuery ? `Results for "${searchQuery}"` : "Featured Events"}
          subtitle={searchQuery ? "found matching events" : "Discover the hottest events happening near you"}
        />
      )}

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
