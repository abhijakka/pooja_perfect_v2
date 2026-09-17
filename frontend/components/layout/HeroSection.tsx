import { useEffect, useState } from "react";

type HeroSectionProps = {
  onExplore: () => void;
};

const heroImages = [
  "https://cdn.shopify.com/s/files/1/0901/3588/8184/files/LaxmiCharanDiyapair_2.png?v=1759706413&width=1200",
  "https://cdn.shopify.com/s/files/1/1857/6931/products/qFQv7mwH9F.jpg?v=1759383512",
  "https://cdn.shopify.com/s/files/1/0727/4210/9475/files/IMG_1294_1.jpg?v=1728298723&width=1200",
];

// Duplicate first image for smooth infinite carousel
const carouselImages = [...heroImages, heroImages[0]];

const heroTitle = "Woven for distinction.";

export function HeroSection({ onExplore }: HeroSectionProps) {
  const [activeImage, setActiveImage] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(true);

  // Start with one letter so it never becomes empty
  const [typedTitle, setTypedTitle] = useState("W");

  /* =========================
     TYPING ANIMATION
     ========================= */
  useEffect(() => {
    let characterIndex = 1;
    let isDeleting = false;
    let timeoutId: number;

    const type = () => {
      if (!isDeleting) {
        // Typing forward
        characterIndex++;

        setTypedTitle(heroTitle.slice(0, characterIndex));

        if (characterIndex >= heroTitle.length) {
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
          setTypedTitle(heroTitle.slice(0, 1));

          isDeleting = false;

          // Small pause before typing again
          timeoutId = window.setTimeout(type, 500);
          return;
        }

        setTypedTitle(heroTitle.slice(0, characterIndex));

        timeoutId = window.setTimeout(type, 50);
      }
    };

    timeoutId = window.setTimeout(type, 500);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, []);

  /* =========================
     IMAGE AUTO SLIDER
     ========================= */
  useEffect(() => {
    const timer = window.setInterval(() => {
      setActiveImage((current) => current + 1);
    }, 4000);

    return () => window.clearInterval(timer);
  }, []);

  /* =========================
     INFINITE SLIDER RESET
     ========================= */
  useEffect(() => {
    if (activeImage !== heroImages.length) return;

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
  }, [activeImage]);

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
            {carouselImages.map((image, index) => (
              <img
                key={`${image}-${index}`}
                className="hero-slide"
                src={image}
                alt="PoojaPoint collection highlight"
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
            SIGNATURE EDIT
          </span>

          {/* TYPING TITLE */}
          <h1 style={{ color: "whitesmoke" }}>
            {typedTitle}
            <span className="typing-cursor">|</span>
          </h1>

          <p style={{ color: "whitesmoke" }}>
            Curated craftsmanship in every ritual.
          </p>

          <button
            className="primary-button"
            onClick={onExplore}
          >
            Shop now
          </button>
        </div>

      </div>
    </section>
  );
}