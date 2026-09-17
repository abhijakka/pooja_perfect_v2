"use client";

import { useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";

type HeroSlide = {
	id: string;
	title: string;
	subtitle: string;
	cta: string;
	badge: string;
	accent: string;
	mediaType: "image" | "video";
	mediaUrl: string;
	altText: string;
	seoTitle: string;
	seoDescription: string;
	cropX: number;
	cropY: number;
	cropZoom: number;
};

const initialSlides: HeroSlide[] = [
	{ id: "slide-1", title: "Festival Essentials for Every Ritual", subtitle: "Curated pooja kits, brass idols, and temple-ready décor for your everyday devotion.", cta: "Shop collection", badge: "New Arrivals", accent: "rose", mediaType: "image", mediaUrl: "", altText: "Pooja collection banner showing sacred brass essentials", seoTitle: "Festival essentials for pooja rituals", seoDescription: "Shop handcrafted pooja essentials and festive décor for rituals, gifting and sacred home styling.", cropX: 50, cropY: 50, cropZoom: 100 },
	{ id: "slide-2", title: "Bring Home Sacred Beauty", subtitle: "Celebrate auspicious moments with handcrafted décor and gifting picks designed for your home.", cta: "Browse décor", badge: "Best Seller", accent: "gold", mediaType: "image", mediaUrl: "", altText: "Sacred home décor and festive gifting picks", seoTitle: "Sacred décor for auspicious occasions", seoDescription: "Explore elegant home décor and temple-inspired products for festive gifting and spiritual occasions.", cropX: 50, cropY: 50, cropZoom: 100 },
	{ id: "slide-3", title: "Pure Essentials for Daily Worship", subtitle: "Trusted essentials for vibrant rituals and serene routines that honor tradition with ease.", cta: "View essentials", badge: "Trending", accent: "sage", mediaType: "video", mediaUrl: "", altText: "Daily worship essentials video for pooja routines", seoTitle: "Daily worship essentials", seoDescription: "Discover quiet, quality essentials for joyful daily worship and mindful rituals at home.", cropX: 50, cropY: 50, cropZoom: 100 },
];

export function AdminHeroPage() {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [slides, setSlides] = useState(initialSlides);
	const [selectedSlide, setSelectedSlide] = useState(initialSlides[0].id);
	const [toast, setToast] = useState("");

	const notify = (message: string) => {
		setToast(message);
		window.setTimeout(() => setToast(""), 2200);
	};

	const selected = slides.find((slide) => slide.id === selectedSlide) ?? slides[0];

	const updateSlideField = (field: keyof HeroSlide, value: string) => {
		setSlides((current) => current.map((slide) => slide.id === selectedSlide ? { ...slide, [field]: value } : slide));
	};

	const handleMediaUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
		const file = event.target.files?.[0];
		if (!file) return;
		const url = URL.createObjectURL(file);
		setSlides((current) => current.map((slide) => slide.id === selectedSlide ? {
			...slide,
			mediaType: file.type.startsWith("video/") ? "video" : "image",
			mediaUrl: url,
			altText: slide.altText || `${slide.title} promotional media`,
			cropX: 50,
			cropY: 50,
			cropZoom: 100,
		} : slide));
		notify(`${file.name} added to slide preview`);
	};

	return <div className="admin-dashboard">
		<AdminIconSprite />
		<AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} activeHref="/admin/hero" />
		<main className="admin-main">
			<AdminHeader onMenu={() => setSidebarOpen(true)} query="" onQuery={() => {}} title="Hero Section" subtitle="Customize the storefront banner and promotional content" />
			<div className="admin-content">
				<div className="hero-exact-page">
					<div className="hero-exact-top">
						<div>
							<div className="hero-exact-heading">Hero Section</div>
							<div className="hero-exact-description">Manage promotional banners that appear on the storefront landing section.</div>
						</div>
						<button className="hero-exact-primary" type="button" onClick={() => notify("Hero settings saved")}>Save changes</button>
					</div>

					<section className="hero-exact-grid">
						<div className="hero-exact-panel">
							<div className="hero-exact-card-header">
								<span>Slides</span>
								<button type="button" onClick={() => notify("New slide created")}>Add slide</button>
							</div>
							<div className="hero-exact-slide-list">
								{slides.map((slide, index) => <button type="button" key={slide.id} className={`hero-exact-slide ${selectedSlide === slide.id ? "active" : ""}`} onClick={() => setSelectedSlide(slide.id)}>
									<div className="hero-exact-slide-badge">{slide.badge}</div>
									<div className="hero-exact-slide-title">{slide.title}</div>
									<div className="hero-exact-slide-meta">Slide {index + 1}</div>
								</button>)}
							</div>
						</div>

						<div className="hero-exact-panel">
							<div className="hero-exact-card-header"><span>Slide editor</span><span className="hero-exact-status">Live</span></div>
							<div className="hero-exact-form">
								<label>
									<span>Badge</span>
									<input value={selected.badge} onChange={(event) => updateSlideField("badge", event.target.value)} />
								</label>
								<label>
									<span>Title</span>
									<input value={selected.title} onChange={(event) => updateSlideField("title", event.target.value)} />
								</label>
								<label>
									<span>Subtitle</span>
									<textarea value={selected.subtitle} onChange={(event) => updateSlideField("subtitle", event.target.value)} rows={4} />
								</label>
								<label>
									<span>Button text</span>
									<input value={selected.cta} onChange={(event) => updateSlideField("cta", event.target.value)} />
								</label>
								<label>
									<span>Accent</span>
									<select value={selected.accent} onChange={(event) => updateSlideField("accent", event.target.value)}>
										<option value="rose">Rose</option>
										<option value="gold">Gold</option>
										<option value="sage">Sage</option>
									</select>
								</label>
								<div className="hero-exact-media-box">
									<div className="hero-exact-media-header">
										<span>Media upload</span>
										<label className="hero-exact-upload-button" htmlFor={`hero-media-${selected.id}`}>
											Choose file
										</label>
									</div>
									<input id={`hero-media-${selected.id}`} type="file" accept="image/*,video/*" onChange={handleMediaUpload} />
									<div className="hero-exact-media-preview">
										{selected.mediaUrl ? (
											selected.mediaType === "video" ? <video src={selected.mediaUrl} controls playsInline /> : <img src={selected.mediaUrl} alt={selected.altText || selected.title} style={{ objectFit: "cover", objectPosition: `${selected.cropX}% ${selected.cropY}%`, transform: `scale(${selected.cropZoom / 100})` }} />
										) : <div className="hero-exact-media-placeholder"><AdminIcon name="image" />No media selected</div>}
									</div>
									<div className="hero-exact-crop-box">
										<div className="hero-exact-section-label">Crop controls</div>
										<label>
											<span>Zoom</span>
											<input type="range" min="80" max="180" value={selected.cropZoom} onChange={(event) => updateSlideField("cropZoom", event.target.value)} />
										</label>
										<label>
											<span>Horizontal</span>
											<input type="range" min="0" max="100" value={selected.cropX} onChange={(event) => updateSlideField("cropX", event.target.value)} />
										</label>
										<label>
											<span>Vertical</span>
											<input type="range" min="0" max="100" value={selected.cropY} onChange={(event) => updateSlideField("cropY", event.target.value)} />
										</label>
									</div>
								</div>
								<div className="hero-exact-seo-box">
									<div className="hero-exact-section-label">SEO details</div>
									<label>
										<span>Alt text</span>
										<input value={selected.altText} onChange={(event) => updateSlideField("altText", event.target.value)} />
									</label>
									<label>
										<span>SEO title</span>
										<input value={selected.seoTitle} onChange={(event) => updateSlideField("seoTitle", event.target.value)} />
									</label>
									<label>
										<span>SEO description</span>
										<textarea value={selected.seoDescription} onChange={(event) => updateSlideField("seoDescription", event.target.value)} rows={3} />
									</label>
								</div>
							</div>
						</div>
					</section>

					<section className="hero-exact-preview">
						<div className={`hero-exact-banner hero-accent-${selected.accent}`}>
							<div className="hero-exact-banner-content">
								<span className="hero-exact-banner-badge">{selected.badge}</span>
								<h3>{selected.title}</h3>
								<p>{selected.subtitle}</p>
								<button type="button">{selected.cta}</button>
							</div>
							<div className="hero-exact-banner-art">
								<div className="hero-exact-orb orb-one" /><div className="hero-exact-orb orb-two" />
								{selected.mediaUrl ? (
									<div className="hero-exact-media-stage">
										{selected.mediaType === "video" ? <video src={selected.mediaUrl} controls playsInline /> : <img src={selected.mediaUrl} alt={selected.altText || selected.title} style={{ objectFit: "cover", objectPosition: `${selected.cropX}% ${selected.cropY}%`, transform: `scale(${selected.cropZoom / 100})` }} />}
									</div>
								) : <div className="hero-exact-product-card"><AdminIcon name="products" /></div>}
							</div>
						</div>
					</section>
				</div>
			</div>
		</main>
		{toast && <div className="coupon-exact-toast show">{toast}</div>}
	</div>;
}
