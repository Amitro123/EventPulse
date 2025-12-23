import { Ticket } from "lucide-react";

const Navbar = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-orange-400 flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-transparent" />
              <Ticket className="w-5 h-5 text-primary-foreground rotate-[-15deg]" />
            </div>
            <span className="font-display font-bold text-xl">
              Secret<span className="gradient-text">Ticket</span>
            </span>
          </a>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-8">
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Events
            </a>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Artists
            </a>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Venues
            </a>
            <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              About
            </a>
          </div>

          {/* CTA */}
          <div className="flex items-center gap-4">
            <a href="#" className="hidden sm:block text-sm text-muted-foreground hover:text-foreground transition-colors">
              Sign In
            </a>
            <a
              href="#"
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-primary to-orange-400 text-sm font-medium text-primary-foreground hover:shadow-lg transition-all hover:-translate-y-0.5"
            >
              Get Started
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
