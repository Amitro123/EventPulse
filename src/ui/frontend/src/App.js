import React, { useState, useCallback } from 'react';

// Package Modal Component
function PackageModal({ event, onClose }) {
    const [packageData, setPackageData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    React.useEffect(() => {
        const fetchPackage = async () => {
            try {
                const response = await fetch(`/api/events/${event.id}/package`);
                if (!response.ok) throw new Error('Failed to load package');
                const data = await response.json();
                setPackageData(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchPackage();
    }, [event.id]);

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>×</button>

                <h2 className="modal-title">📦 Event Package</h2>
                <h3 className="modal-event-name">{event.text}</h3>

                {loading && (
                    <div className="modal-loading">
                        <span className="loading-spinner-inline"></span>
                        Loading package...
                    </div>
                )}

                {error && (
                    <div className="modal-error">⚠️ {error}</div>
                )}

                {packageData && (
                    <div className="package-sections">
                        <div className="package-section">
                            <h4>🎟️ Tickets</h4>
                            <p>Get your tickets for this event</p>
                            <a
                                href={packageData.tickets.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="package-btn tickets-btn"
                            >
                                Open Tickets
                            </a>
                        </div>

                        <div className="package-section">
                            <h4>🏨 Hotels</h4>
                            <p>
                                Find hotels in {packageData.hotels.city}<br />
                                <span className="hotel-dates">
                                    Check-in: {packageData.hotels.check_in} → Check-out: {packageData.hotels.check_out}
                                </span>
                            </p>
                            <a
                                href={packageData.hotels.affiliate_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="package-btn hotels-btn"
                            >
                                Search Hotels
                            </a>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

// Event Card Component
function EventCard({ event }) {
    const [showPackage, setShowPackage] = useState(false);

    return (
        <>
            <div className="event-card">
                <img
                    src={event.image_url || `https://via.placeholder.com/400x200?text=${encodeURIComponent(event.text)}`}
                    alt={event.text}
                    className="event-image"
                    onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/400x200?text=Event';
                    }}
                />
                <div className="event-content">
                    <span className="event-category">{event.category || 'Event'}</span>
                    <h3 className="event-title">{event.text}</h3>
                    <div className="event-details">
                        <div className="event-detail">
                            <span className="event-detail-icon">📍</span>
                            <span>{event.venue_name}</span>
                        </div>
                        <div className="event-detail">
                            <span className="event-detail-icon">🏙️</span>
                            <span>{event.city}</span>
                        </div>
                        <div className="event-detail">
                            <span className="event-detail-icon">📅</span>
                            <span>{new Date(event.timestamp).toLocaleDateString('en-US', {
                                weekday: 'short',
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric'
                            })}</span>
                        </div>
                    </div>
                    {event.price_range && (
                        <div className="event-price">{event.price_range}</div>
                    )}
                    <div className="event-buttons">
                        <a
                            href={event.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="book-btn"
                        >
                            🎟️ Buy Tickets
                        </a>
                        <button
                            className="package-view-btn"
                            onClick={() => setShowPackage(true)}
                        >
                            📦 View Package
                        </button>
                    </div>
                </div>
            </div>
            {showPackage && (
                <PackageModal event={event} onClose={() => setShowPackage(false)} />
            )}
        </>
    );
}


// Main App Component
function App() {
    // Search mode: 'date' or 'artist'
    const [searchMode, setSearchMode] = useState('date');

    // Date search fields
    const [date, setDate] = useState(() => {
        const d = new Date();
        d.setDate(d.getDate() + 7);
        return d.toISOString().split('T')[0];
    });
    const [city, setCity] = useState('');
    const [category, setCategory] = useState('');

    // Artist search fields
    const [artist, setArtist] = useState('');
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [countryCode, setCountryCode] = useState('US');

    // Common state
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searched, setSearched] = useState(false);

    const searchByDate = useCallback(async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSearched(true);

        try {
            const params = new URLSearchParams({ date, limit: 20 });
            if (city) params.append('city', city);
            if (category) params.append('category', category);

            const response = await fetch(`/api/events?${params}`);

            if (!response.ok) {
                throw new Error('Failed to fetch events');
            }

            const data = await response.json();
            setEvents(data);
        } catch (err) {
            setError(err.message);
            setEvents([]);
        } finally {
            setLoading(false);
        }
    }, [date, city, category]);

    const searchByArtist = useCallback(async (e) => {
        e.preventDefault();
        if (!artist.trim()) {
            setError('Please enter an artist name');
            return;
        }

        setLoading(true);
        setError(null);
        setSearched(true);

        try {
            const params = new URLSearchParams({ artist, limit: 20 });
            if (dateFrom) params.append('date_from', dateFrom);
            if (dateTo) params.append('date_to', dateTo);
            if (countryCode) params.append('country_code', countryCode);

            const response = await fetch(`/api/events/by-artist?${params}`);

            if (!response.ok) {
                throw new Error('Failed to fetch events');
            }

            const data = await response.json();
            setEvents(data);
        } catch (err) {
            setError(err.message);
            setEvents([]);
        } finally {
            setLoading(false);
        }
    }, [artist, dateFrom, dateTo, countryCode]);

    const handleModeChange = (mode) => {
        setSearchMode(mode);
        setEvents([]);
        setSearched(false);
        setError(null);
    };

    return (
        <div className="app">
            <header className="header">
                <div className="header-content">
                    <div className="logo">
                        <span className="logo-icon">⚡</span>
                        <span>EventPulse</span>
                    </div>
                </div>
            </header>

            <main className="main-content">
                <section className="hero">
                    <h1>Discover Amazing Events</h1>
                    <p>Find concerts, sports events, and more. Book your experience today!</p>
                </section>

                {/* Search Mode Tabs */}
                <div className="search-tabs">
                    <button
                        className={`search-tab ${searchMode === 'date' ? 'active' : ''}`}
                        onClick={() => handleModeChange('date')}
                    >
                        📅 Search by Date
                    </button>
                    <button
                        className={`search-tab ${searchMode === 'artist' ? 'active' : ''}`}
                        onClick={() => handleModeChange('artist')}
                    >
                        🎤 Search by Artist
                    </button>
                </div>

                {/* Date Search Form */}
                {searchMode === 'date' && (
                    <form className="search-form" onSubmit={searchByDate}>
                        <div className="search-grid">
                            <div className="form-group">
                                <label htmlFor="date">Event Date *</label>
                                <input
                                    id="date"
                                    type="date"
                                    value={date}
                                    onChange={(e) => setDate(e.target.value)}
                                    min={new Date().toISOString().split('T')[0]}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="city">City (optional)</label>
                                <input
                                    id="city"
                                    type="text"
                                    value={city}
                                    onChange={(e) => setCity(e.target.value)}
                                    placeholder="e.g., Tel Aviv, New York"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="category">Category (optional)</label>
                                <select
                                    id="category"
                                    value={category}
                                    onChange={(e) => setCategory(e.target.value)}
                                >
                                    <option value="">All Categories</option>
                                    <option value="music">🎵 Music</option>
                                    <option value="sports">⚽ Sports</option>
                                    <option value="arts">🎭 Arts & Theater</option>
                                    <option value="family">👨‍👩‍👧‍👦 Family</option>
                                </select>
                            </div>
                        </div>

                        <button type="submit" className="search-btn" disabled={loading}>
                            {loading ? (
                                <>
                                    <span className="loading-spinner-inline"></span>
                                    Searching...
                                </>
                            ) : (
                                <>
                                    🔍 Search Events
                                </>
                            )}
                        </button>
                    </form>
                )}

                {/* Artist Search Form */}
                {searchMode === 'artist' && (
                    <form className="search-form" onSubmit={searchByArtist}>
                        <div className="search-grid">
                            <div className="form-group form-group-wide">
                                <label htmlFor="artist">Artist / Performer *</label>
                                <input
                                    id="artist"
                                    type="text"
                                    value={artist}
                                    onChange={(e) => setArtist(e.target.value)}
                                    placeholder="e.g., Coldplay, Taylor Swift, Ed Sheeran"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="dateFrom">From Date (optional)</label>
                                <input
                                    id="dateFrom"
                                    type="date"
                                    value={dateFrom}
                                    onChange={(e) => setDateFrom(e.target.value)}
                                    min={new Date().toISOString().split('T')[0]}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="dateTo">To Date (optional)</label>
                                <input
                                    id="dateTo"
                                    type="date"
                                    value={dateTo}
                                    onChange={(e) => setDateTo(e.target.value)}
                                    min={dateFrom || new Date().toISOString().split('T')[0]}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="countryCode">Country</label>
                                <select
                                    id="countryCode"
                                    value={countryCode}
                                    onChange={(e) => setCountryCode(e.target.value)}
                                >
                                    <option value="US">🇺🇸 United States</option>
                                    <option value="GB">🇬🇧 United Kingdom</option>
                                    <option value="CA">🇨🇦 Canada</option>
                                    <option value="AU">🇦🇺 Australia</option>
                                    <option value="DE">🇩🇪 Germany</option>
                                    <option value="FR">🇫🇷 France</option>
                                    <option value="IL">🇮🇱 Israel</option>
                                    <option value="ES">🇪🇸 Spain</option>
                                    <option value="IT">🇮🇹 Italy</option>
                                    <option value="NL">🇳🇱 Netherlands</option>
                                </select>
                            </div>
                        </div>

                        <button type="submit" className="search-btn" disabled={loading}>
                            {loading ? (
                                <>
                                    <span className="loading-spinner-inline"></span>
                                    Searching...
                                </>
                            ) : (
                                <>
                                    🎤 Find Artist Events
                                </>
                            )}
                        </button>
                    </form>
                )}

                {error && (
                    <div className="error">
                        ⚠️ {error}
                    </div>
                )}

                {loading && (
                    <div className="loading">
                        <div className="loading-spinner"></div>
                        <p>Finding amazing events for you...</p>
                    </div>
                )}

                {!loading && searched && events.length === 0 && !error && (
                    <div className="empty-state">
                        <div className="empty-state-icon">🎪</div>
                        <h3>No events found</h3>
                        <p>Try adjusting your search criteria or selecting a different date.</p>
                    </div>
                )}

                {!loading && events.length > 0 && (
                    <section className="events-section">
                        <h2>🎉 {events.length} Events Found</h2>
                        <div className="events-grid">
                            {events.map((event) => (
                                <EventCard key={event.id} event={event} />
                            ))}
                        </div>
                    </section>
                )}
            </main>

            <footer className="footer">
                <p>© 2024 EventPulse - Event Discovery Platform</p>
            </footer>
        </div>
    );
}

export default App;

