import { useEffect, useState } from "react";

export type HeroSlide = {
  title: string;
  subtitle: string;
  badge: string;
  accent: string;
  ctaLabel: string;
  ctaUrl?: string;
  mediaUrl?: string;
  mediaType?: "image" | "video";
  altText?: string;
};

type HeroSectionProps = {
  onExplore: () => void;
  slides?: HeroSlide[];
};

const fallbackImages = [
  "https://cdn.shopify.com/s/files/1/0901/3588/8184/files/LaxmiCharanDiyapair_2.png?v=1759706413&width=1200",
  "https://cdn.shopify.com/s/files/1/1857/6931/products/qFQv7mwH9F.jpg?v=1759383512",
  "https://cdn.shopify.com/s/files/1/0727/4210/9475/files/IMG_1294_1.jpg?v=1728298723&width=1200",
];

const defaultSlides: HeroSlide[] = [
  {
    title: "Woven for distinction.",
    subtitle: "Curated craftsmanship in every ritual.",
    badge: "SIGNATURE EDIT",
    accent: "rose",
    ctaLabel: "Shop now",
    ctaUrl: "#products",
  },
  {
    title: "Sacred essentials, delivered daily.",
    subtitle: "Ritual-ready pooja kits and décor for your home.",
    badge: "NEW ARRIVALS",
    accent: "gold",
    ctaLabel: "Shop now",
    ctaUrl: "#products",
  },
  {
    title: "Festive décor for every home.",
    subtitle: "Handcrafted idols, diyas and temple décor.",
    badge: "BESTSELLERS",
    accent: "sage",
    ctaLabel: "Shop now",
    ctaUrl: "#products",
  },
];

function mediaFor(slide: HeroSlide, index: number): string {
  return (
    slide.mediaUrl ||
    fallbackImages[index % fallbackImages.length]
  );
}

// Duplicate first slide for smooth infinite carousel
function buildCarousel(slides: HeroSlide[]) {
  return [...slides, slides[0]];
}

export function HeroSection({
  onExplore,
  slides = defaultSlides,
}: HeroSectionProps) {
  const [activeImage, setActiveImage] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(true);

  const carousel = buildCarousel(slides);
  const current = slides[Math.min(activeImage, slides.length - 1)] ?? slides[0];
  const activeTitle = current?.title ?? "";

  // Start with one letter so it never becomes empty
  const [typedTitle, setTypedTitle] = useState(activeTitle.slice(0, 1) || " ");

  /* =========================
     TYPING ANIMATION
     ========================= */
  useEffect(() => {
    if (!activeTitle) return;
    let characterIndex = activeTitle.slice(0, 1).length;
    let isDeleting = false;
    let timeoutId: number;

    const type = () => {
      if (!isDeleting) {
        // Typing forward
        characterIndex++;

        setTypedTitle(activeTitle.slice(0, characterIndex));

        if (characterIndex >= activeTitle.length) {
          isDeleting = true;

          // Pause after full text
          timeoutId = window.setTimeout(type, 2000);
          return;
        }

        timeoutId = window.setTimeout(type, 85);
      } else {
        // Deleting backward
        characterIndex--;

        // Never delete below 1 character
        if (characterIndex <= 1) {
          characterIndex = 1;
          setTypedTitle(activeTitle.slice(0, 1));

          isDeleting = false;

          // Small pause before typing again
          timeoutId = window.setTimeout(type, 500);
          return;
        }

        setTypedTitle(activeTitle.slice(0, characterIndex));

        timeoutId = window.setTimeout(type, 50);
      }
    };

    timeoutId = window.setTimeout(type, 500);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [activeTitle]);

  /* =========================
     IMAGE AUTO SLIDER
     ========================= */
  useEffect(() => {
    const timer = window.setInterval(() => {
      setActiveImage((currentIndex) => currentIndex + 1);
    }, 4000);

    return () => window.clearInterval(timer);
  }, []);

  /* =========================
     INFINITE SLIDER RESET
     ========================= */
  useEffect(() => {
    if (activeImage !== slides.length) return;

    const resetTimer = window.setTimeout(() => {
      setIsTransitioning(false);
      setActiveImage(0);

      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          setIsTransitioning(true);
        });
      });
    }, 800);

    return () => window.clearTimeout(resetTimer);
  }, [activeImage, slides.length]);

  return (
    <section className="hero">
      <div className="hero-card hero-fashion-card">

        {/* IMAGE SLIDER */}
        <div
          className="hero-slider"
          aria-label="PoojaPoint collection highlights"
        >
          <div
            style={{
              display: "flex",
              width: "100%",
              height: "100%",
              transform: `translateX(-${activeImage * 100}%)`,
              transition: isTransitioning
                ? "transform 800ms ease"
                : "none",
            }}
          >
            {carousel.map((slide, index) => (
              <img
                key={index}
                className="hero-slide"
                src={mediaFor(slide, index)}
                alt={slide.altText || `${slide.title} PoojaPoint highlight`}
                style={{
                  position: "static",
                  width: "100%",
                  height: "100%",
                  flex: "0 0 100%",
                  opacity: 1,
                  transform: "none",
                  objectFit: "cover",
                }}
              />
            ))}
          </div>
        </div>

        {/* OVERLAY */}
        <div className="hero-overlay" />

        {/* CONTENT */}
        <div className="hero-content">
          <span className="hero-badge">
            <i style={{ backgroundColor: "red" }} />
            {current?.badge || "SIGNATURE EDIT"}
          </span>

          {/* TYPING TITLE */}
          <h1 style={{ color: "whitesmoke" }}>
            {typedTitle}
            <span className="typing-cursor">|</span>
          </h1>

          <p style={{ color: "whitesmoke" }}>
            {current?.subtitle || "Curated craftsmanship in every ritual."}
          </p>

          <button
            className="primary-button"
            onClick={onExplore}
          >
            {current?.ctaLabel || "Shop now"}
          </button>
        </div>

      </div>
    </section>
  );
}