#!/usr/bin/env node
// End-to-end SEO check: crawls indexable public routes and validates the rendered HTML,
// plus /robots.txt and /sitemap.xml. Zero dependencies (Node 18+ global fetch).
// Usage: node scripts/seo-check.mjs [baseUrl]   (default http://localhost:3000)

const BASE = (process.env.SEO_BASE_URL ?? process.argv[2] ?? "http://localhost:3000").replace(/\/+$/, "");
const PLACEHOLDER = "poojapoint.example.com";

const PRODUCT_SLUGS = [
  "premium-brass-pooja-diya",
  "elegant-ganesha-idol",
  "traditional-pooja-thali-set",
  "lotus-decorative-diyas",
  "daily-pooja-essentials-kit",
  "premium-temple-decor-set",
  "divine-lotus-gift-set",
  "brass-temple-diya-set",
];
const CATEGORY_SLUGS = ["diya", "om", "flower", "lotus", "temple", "heart"];

const ROUTES = [
  "/",
  "/products",
  ...PRODUCT_SLUGS.map((s) => `/products/${s}`),
  ...CATEGORY_SLUGS.map((s) => `/categories/${s}`),
  "/search",
  "/subscriptions",
];
const JSONLD_ROUTES = new Set([
  ...PRODUCT_SLUGS.map((s) => `/products/${s}`),
  ...CATEGORY_SLUGS.map((s) => `/categories/${s}`),
]);

function newChecks() {
  const checks = [];
  return { checks, ok: (cond, label) => checks.push({ label, pass: !!cond }) };
}

// Extract a meta tag's content by name/property, regardless of attribute order.
function metaContent(html, attrName, attrValue) {
  const tag = html.match(new RegExp(`<meta[^>]+${attrName}=["']${attrValue}["'][^>]*>`, "i"))?.[0] ?? "";
  return tag.match(/content=["']([^"']*)["']/i)?.[1] ?? "";
}

async function checkPage(path) {
  const { checks, ok } = newChecks();
  let html = "";
  let status = 0;
  try {
    const res = await fetch(BASE + path);
    status = res.status;
    html = await res.text();
  } catch {
    html = "";
  }
  ok(status === 200, `status 200 (got ${status})`);
  ok((html.match(/<title[^>]*>([^<]*)<\/title>/i)?.[1] ?? "").trim().length > 0, "title present");
  ok(metaContent(html, "name", "description").length > 0, "meta description");
  const canonical = html.match(/<link[^>]+rel=["']canonical["'][^>]*>/i)?.[0]?.match(/href=["']([^"']*)["']/i)?.[1] ?? "";
  ok(canonical.startsWith(BASE), "canonical matches base");
  ok(metaContent(html, "property", "og:title").length > 0, "og:title");
  ok(metaContent(html, "property", "og:description").length > 0, "og:description");
  ok(metaContent(html, "property", "og:type").length > 0, "og:type");
  ok(metaContent(html, "property", "og:url").length > 0, "og:url");
  ok(/<html[^>]+lang=["'][^"']+["']/i.test(html), "html lang");
  ok(!html.includes(PLACEHOLDER), "no placeholder domain");
  if (JSONLD_ROUTES.has(path)) {
    ok(/<script[^>]+type=["']application\/ld\+json["']/i.test(html), "JSON-LD present");
  }
  return { path, checks };
}

async function checkRobots() {
  const { checks, ok } = newChecks();
  const res = await fetch(`${BASE}/robots.txt`);
  const text = await res.text();
  ok(res.status === 200, `status 200 (got ${res.status})`);
  ok(text.includes("Sitemap:"), "has Sitemap");
  ok(!text.includes(PLACEHOLDER), "no placeholder domain");
  ok(text.includes("Disallow: /admin"), "disallows /admin");
  return { path: "/robots.txt", checks };
}

async function checkSitemap() {
  const { checks, ok } = newChecks();
  const res = await fetch(`${BASE}/sitemap.xml`);
  const text = await res.text();
  ok(res.status === 200, `status 200 (got ${res.status})`);
  ok(text.includes("<urlset"), "is a urlset");
  const locs = [...text.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  ok(locs.length > 0, "has urls");
  ok(!text.includes(PLACEHOLDER), "no placeholder domain");
  const missing = ROUTES.filter((p) => !locs.some((l) => l.endsWith(p)));
  ok(missing.length === 0, `lists all routes${missing.length ? ` (missing: ${missing.join(", ")})` : ""}`);
  return { path: "/sitemap.xml", checks };
}

const results = await Promise.all([...ROUTES.map(checkPage), checkRobots(), checkSitemap()]);

let failedRoutes = 0;
let issueCount = 0;
for (const { path, checks } of results) {
  const failed = checks.filter((c) => !c.pass);
  if (failed.length) failedRoutes++;
  issueCount += failed.length;
  console.log(`${failed.length ? "FAIL" : "PASS"} ${path}${failed.length ? " — " + failed.map((f) => f.label).join("; ") : ""}`);
}
console.log(`\n${results.length - failedRoutes}/${results.length} passed, ${issueCount} issue(s).`);
process.exit(issueCount ? 1 : 0);