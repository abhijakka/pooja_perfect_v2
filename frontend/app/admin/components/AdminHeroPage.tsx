"use client";

import { ChangeEvent, useEffect, useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";
import { AdminHero, adminApi } from "../../../services/api/admin.api";

const MAX_HEROES = 4;
const MAX_HEROES_MESSAGE =
  "Maximum 4 Hero sections are allowed. Please update or delete an existing Hero before adding another.";

type HeroDraft = {
  title: string;
  subtitle: string;
  badge: string;
  accent: string;
  ctaLabel: string;
  ctaLink: string;
  displayOrder: number;
  seoTitle: string;
  seoDescription: string;
  altText: string;
};

const blankDraft: HeroDraft = {
  title: "",
  subtitle: "",
  badge: "",
  accent: "rose",
  ctaLabel: "Shop now",
  ctaLink: "/collections/all",
  displayOrder: 0,
  seoTitle: "",
  seoDescription: "",
  altText: "",
};

function primaryImage(hero: AdminHero | undefined) {
  const image =
    hero?.images.find((item) => item.isPrimary) ?? hero?.images[0];
  return image;
}

function heroToDraft(hero: AdminHero): HeroDraft {
  const image = primaryImage(hero);
  return {
    title: hero.title ?? "",
    subtitle: hero.subtitle ?? "",
    badge: hero.badge ?? "",
    accent: hero.accent ?? "rose",
    ctaLabel: hero.ctaLabel ?? "Shop now",
    ctaLink: hero.ctaLink ?? "",
    displayOrder: hero.displayOrder ?? 0,
    seoTitle: hero.seoTitle ?? "",
    seoDescription: hero.seoDescription ?? "",
    altText: image?.altText ?? "",
  };
}

export function AdminHeroPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [heroes, setHeroes] = useState<AdminHero[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [draft, setDraft] = useState<HeroDraft>(blankDraft);
  const [toast, setToast] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2400);
  };

  const replaceHero = (updated: AdminHero) =>
    setHeroes((current) =>
      current.map((hero) => (hero.id === updated.id ? updated : hero)),
    );

  useEffect(() => {
    let active = true;
    adminApi
      .listHeroes()
      .then(({ heroes: data }) => {
        if (!active) return;
        setHeroes(data ?? []);
        if (data?.length) {
          setSelectedId(data[0].id);
          setDraft(heroToDraft(data[0]));
        }
      })
      .catch((loadError) => {
        if (!active) return;
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Unable to load hero sections",
        );
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const selected = heroes.find((hero) => hero.id === selectedId);
  const selectedImage = primaryImage(selected);
  const selectedIndex = heroes.findIndex((hero) => hero.id === selectedId);
  const atLimit = heroes.length >= MAX_HEROES;

  const selectHero = (id: string) => {
    const hero = heroes.find((item) => item.id === id);
    setSelectedId(id);
    setDraft(hero ? heroToDraft(hero) : blankDraft);
  };

  const updateDraft = (field: keyof HeroDraft, value: string | number) =>
    setDraft((current) => ({ ...current, [field]: value }));

  const saveSelected = async () => {
    const hero = selected;
    if (!hero) return;
    if (!draft.title.trim()) {
      notify("Hero title is required");
      return;
    }
    setSaving(true);
    try {
      const result = await adminApi.updateHero(hero.id, {
        title: draft.title,
        subtitle: draft.subtitle || null,
        badge: draft.badge || null,
        accent: draft.accent || null,
        ctaLabel: draft.ctaLabel || null,
        ctaLink: draft.ctaLink || null,
        displayOrder: Number(draft.displayOrder) || 0,
        seoTitle: draft.seoTitle || null,
        seoDescription: draft.seoDescription || null,
      });
      replaceHero(result.updateHero);
      notify("Hero updated successfully");
    } catch (saveError) {
      notify(
        saveError instanceof Error
          ? saveError.message
          : "Hero could not be saved",
      );
    } finally {
      setSaving(false);
    }
  };

  const addSlide = async () => {
    if (atLimit) {
      notify(MAX_HEROES_MESSAGE);
      return;
    }
    try {
      const result = await adminApi.createHero({
        title: "New Hero Slide",
        displayOrder: heroes.length,
      });
      const created = result.createHero;
      setHeroes((current) => [...current, created]);
      setSelectedId(created.id);
      setDraft(heroToDraft(created));
      notify("New slide created");
    } catch (createError) {
      notify(
        createError instanceof Error
          ? createError.message
          : "Slide could not be created",
      );
    }
  };

  const handleMediaUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    const hero = selected;
    if (!hero) return;
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async () => {
      try {
        const result = await adminApi.uploadHeroImage(
          hero.id,
          reader.result as string,
          draft.altText || `${draft.title || hero.title} promotional media`,
          true,
        );
        replaceHero(result.uploadHeroImage);
        notify(`${file.name} uploaded`);
      } catch (uploadError) {
        notify(
          uploadError instanceof Error
            ? uploadError.message
            : "Image could not be uploaded",
        );
      }
    };
    reader.readAsDataURL(file);
  };

  const removeImage = async () => {
    const image = selectedImage;
    if (!image) return;
    try {
      const result = await adminApi.removeHeroImage(image.id);
      const hero = selected;
      if (hero && result.removeHeroImage.success) {
        replaceHero({
          ...hero,
          images: hero.images.filter((item) => item.id !== image.id),
        });
        notify("Hero image removed");
      }
    } catch (removeError) {
      notify(
        removeError instanceof Error
          ? removeError.message
          : "Image could not be removed",
      );
    }
  };

  const deleteSelected = async () => {
    const hero = selected;
    if (!hero) return;
    try {
      const result = await adminApi.deleteHero(hero.id);
      if (!result.deleteHero.success) return;
      setHeroes((current) => current.filter((item) => item.id !== hero.id));
      const remaining = heroes.filter((item) => item.id !== hero.id);
      if (remaining.length) {
        setSelectedId(remaining[0].id);
        setDraft(heroToDraft(remaining[0]));
      } else {
        setSelectedId("");
        setDraft(blankDraft);
      }
      setConfirmDelete(false);
      notify("Hero deleted successfully");
    } catch (deleteError) {
      notify(
        deleteError instanceof Error
          ? deleteError.message
          : "Hero could not be deleted",
      );
    }
  };

  const toggleActive = async () => {
    const hero = selected;
    if (!hero) return;
    try {
      const result = await adminApi.setHeroActive(hero.id, !hero.isActive);
      replaceHero({ ...hero, isActive: result.setHeroActive.isActive });
      notify(
        result.setHeroActive.isActive
          ? "Hero activated"
          : "Hero deactivated",
      );
    } catch (toggleError) {
      notify(
        toggleError instanceof Error
          ? toggleError.message
          : "Unable to update hero status",
      );
    }
  };

  return (
    <div className="admin-dashboard">
      <AdminIconSprite />
      <AdminSidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activeHref="/admin/hero"
      />
      <main className="admin-main">
        <AdminHeader
          onMenu={() => setSidebarOpen(true)}
          query=""
          onQuery={() => {}}
          title="Hero Section"
          subtitle="Customize the storefront banner and promotional content"
        />
        <div className="admin-content">
          <div className="hero-exact-page">
            <div className="hero-exact-top">
              <div>
                <div className="hero-exact-heading">Hero Section</div>
                <div className="hero-exact-description">
                  Manage promotional banners that appear on the storefront
                  landing section. Up to {MAX_HEROES} slides can be live at a
                  time.
                </div>
              </div>
              <button
                className="hero-exact-primary"
                type="button"
                disabled={saving || !selected}
                onClick={saveSelected}
              >
                {saving ? "Saving..." : "Save changes"}
              </button>
            </div>

            <section className="hero-exact-grid">
              <div className="hero-exact-panel">
                <div className="hero-exact-card-header">
                  <span>Slides ({heroes.length}/{MAX_HEROES})</span>
                  <button
                    type="button"
                    disabled={atLimit}
                    onClick={addSlide}
                    title={atLimit ? MAX_HEROES_MESSAGE : "Add a new slide"}
                  >
                    Add slide
                  </button>
                </div>
                <div className="hero-exact-slide-list">
                  {heroes.map((hero, index) => (
                    <button
                      type="button"
                      key={hero.id}
                      className={`hero-exact-slide ${selectedId === hero.id ? "active" : ""}`}
                      onClick={() => selectHero(hero.id)}
                    >
                      <div className="hero-exact-slide-badge">
                        {hero.badge || "No badge"}
                      </div>
                      <div className="hero-exact-slide-title">
                        {hero.title}
                      </div>
                      <div className="hero-exact-slide-meta">
                        Slide {index + 1} ·{" "}
                        {hero.isActive ? "Live" : "Inactive"}
                      </div>
                    </button>
                  ))}
                  {!loading && !heroes.length && (
                    <div className="admin-empty-state">
                      No hero slides yet. Add your first slide below.
                    </div>
                  )}
                  {atLimit && (
                    <div className="hero-exact-limit-note">
                      {MAX_HEROES_MESSAGE}
                    </div>
                  )}
                </div>
              </div>

              <div className="hero-exact-panel">
                {selected ? (
                  <>
                    <div className="hero-exact-card-header">
                      <span>Slide editor</span>
                      <span className={`hero-exact-status ${selected.isActive ? "" : "inactive"}`}>
                        {selected.isActive ? "Live" : "Inactive"}
                      </span>
                    </div>
                    <div className="hero-exact-form">
                      <label>
                        <span>Badge</span>
                        <input
                          value={draft.badge}
                          onChange={(event) =>
                            updateDraft("badge", event.target.value)
                          }
                        />
                      </label>
                      <label>
                        <span>Title</span>
                        <input
                          value={draft.title}
                          onChange={(event) =>
                            updateDraft("title", event.target.value)
                          }
                        />
                      </label>
                      <label>
                        <span>Subtitle</span>
                        <textarea
                          value={draft.subtitle}
                          onChange={(event) =>
                            updateDraft("subtitle", event.target.value)
                          }
                          rows={4}
                        />
                      </label>
                      <label>
                        <span>Button text</span>
                        <input
                          value={draft.ctaLabel}
                          onChange={(event) =>
                            updateDraft("ctaLabel", event.target.value)
                          }
                        />
                      </label>
                      <label>
                        <span>Button link</span>
                        <input
                          value={draft.ctaLink}
                          onChange={(event) =>
                            updateDraft("ctaLink", event.target.value)
                          }
                        />
                      </label>
                      <label>
                        <span>Display order</span>
                        <input
                          type="number"
                          min={0}
                          value={draft.displayOrder}
                          onChange={(event) =>
                            updateDraft(
                              "displayOrder",
                              Number(event.target.value),
                            )
                          }
                        />
                      </label>
                      <label>
                        <span>Accent</span>
                        <select
                          value={draft.accent}
                          onChange={(event) =>
                            updateDraft("accent", event.target.value)
                          }
                        >
                          <option value="rose">Rose</option>
                          <option value="gold">Gold</option>
                          <option value="sage">Sage</option>
                        </select>
                      </label>
                      <div className="hero-exact-media-box">
                        <div className="hero-exact-media-header">
                          <span>Media upload</span>
                          <label
                            className="hero-exact-upload-button"
                            htmlFor={`hero-media-${selected.id}`}
                          >
                            Choose image
                          </label>
                        </div>
                        <input
                          id={`hero-media-${selected.id}`}
                          type="file"
                          accept="image/*"
                          onChange={handleMediaUpload}
                        />
                        <div className="hero-exact-media-preview">
                          {selectedImage ? (
                            <img
                              src={selectedImage.url}
                              alt={selectedImage.altText || selected.title}
                              style={{
                                objectFit: "cover",
                                objectPosition: `${selectedImage.cropX ?? 50}% ${selectedImage.cropY ?? 50}%`,
                                transform: `scale(${(selectedImage.cropZoom ?? 100) / 100})`,
                              }}
                            />
                          ) : (
                            <div className="hero-exact-media-placeholder">
                              <AdminIcon name="image" />
                              No media selected
                            </div>
                          )}
                        </div>
                        {selectedImage && (
                          <button
                            type="button"
                            className="hero-exact-remove-media"
                            onClick={removeImage}
                          >
                            Remove image
                          </button>
                        )}
                      </div>
                      <div className="hero-exact-seo-box">
                        <div className="hero-exact-section-label">SEO details</div>
                        <label>
                          <span>Alt text</span>
                          <input
                            value={draft.altText}
                            onChange={(event) =>
                              updateDraft("altText", event.target.value)
                            }
                          />
                        </label>
                        <label>
                          <span>SEO title</span>
                          <input
                            value={draft.seoTitle}
                            onChange={(event) =>
                              updateDraft("seoTitle", event.target.value)
                            }
                          />
                        </label>
                        <label>
                          <span>SEO description</span>
                          <textarea
                            value={draft.seoDescription}
                            onChange={(event) =>
                              updateDraft("seoDescription", event.target.value)
                            }
                            rows={3}
                          />
                        </label>
                      </div>
                      <div className="hero-exact-actions">
                        <button type="button" onClick={toggleActive}>
                          {selected.isActive ? "Deactivate slide" : "Activate slide"}
                        </button>
                        <button
                          className="danger"
                          type="button"
                          onClick={() => setConfirmDelete(true)}
                        >
                          Delete slide
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="hero-exact-empty">
                    {loading
                      ? "Loading hero sections..."
                      : error || "Select or add a slide to start editing."}
                  </div>
                )}
              </div>
            </section>

            <section className="hero-exact-preview">
              <div className={`hero-exact-banner hero-accent-${draft.accent}`}>
                <div className="hero-exact-banner-content">
                  <span className="hero-exact-banner-badge">
                    {draft.badge || "New"}
                  </span>
                  <h3>{draft.title || "Your hero title"}</h3>
                  <p>{draft.subtitle}</p>
                  <button type="button">{draft.ctaLabel}</button>
                </div>
                <div className="hero-exact-banner-art">
                  <div className="hero-exact-orb orb-one" />
                  <div className="hero-exact-orb orb-two" />
                  {selectedImage ? (
                    <div className="hero-exact-media-stage">
                      <img
                        src={selectedImage.url}
                        alt={selectedImage.altText || draft.title}
                        style={{
                          objectFit: "cover",
                          objectPosition: `${selectedImage.cropX ?? 50}% ${selectedImage.cropY ?? 50}%`,
                          transform: `scale(${(selectedImage.cropZoom ?? 100) / 100})`,
                        }}
                      />
                    </div>
                  ) : (
                    <div className="hero-exact-product-card">
                      <AdminIcon name="products" />
                    </div>
                  )}
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>

      {confirmDelete && (
        <div className="products-exact-modal-overlay">
          <div className="products-exact-modal small">
            <div className="products-exact-modal-header">
              <div className="products-exact-modal-title">Delete slide?</div>
              <button type="button" onClick={() => setConfirmDelete(false)}>
                <AdminIcon name="close" />
              </button>
            </div>
            <div className="products-exact-modal-body">
              <p className="products-exact-delete-message">
                This will remove the hero slide from the storefront. A freed
                slot becomes available for a new slide.
              </p>
              <div className="products-exact-delete-name">{selected?.title}</div>
            </div>
            <div className="products-exact-modal-footer">
              <button type="button" onClick={() => setConfirmDelete(false)}>
                Cancel
              </button>
              <button
                className="danger"
                type="button"
                onClick={deleteSelected}
              >
                Delete slide
              </button>
            </div>
          </div>
        </div>
      )}

      {toast && <div className="coupon-exact-toast show">{toast}</div>}
    </div>
  );
}