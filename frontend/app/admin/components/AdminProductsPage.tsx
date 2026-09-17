"use client";

import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { useFormik } from "formik";
import * as yup from "yup";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";
import { AdminProduct, adminApi } from "../../../services/api/admin.api";

type ProductStatus = "active" | "draft" | "out";
type ProductImage = {
  id?: string;
  url: string;
  altText?: string | null;
  displayOrder: number;
  isPrimary: boolean;
};
type Product = {
  id: string;
  name: string;
  slug: string;
  sku: string;
  category: string;
  categoryLabel: string;
  subcategory: string;
  description: string;
  price: string;
  mrp: string;
  stock: number;
  status: ProductStatus;
  featured: boolean;
  emoji: string;
  images: ProductImage[];
};
type ProductForm = {
  name: string;
  slug: string;
  sku: string;
  category: string;
  subcategory: string;
  description: string;
  price: string;
  mrp: string;
  discount: string;
  stock: string;
  lowStock: string;
  status: ProductStatus;
  weight: string;
  seoTitle: string;
  seoDescription: string;
  featured: boolean;
  images: ProductImage[];
  removedImages: string[];
};

const blankForm: ProductForm = {
  name: "",
  slug: "",
  sku: "",
  category: "",
  subcategory: "",
  description: "",
  price: "",
  mrp: "",
  discount: "",
  stock: "",
  lowStock: "10",
  status: "active",
  weight: "",
  seoTitle: "",
  seoDescription: "",
  featured: false,
  images: [],
  removedImages: [],
};
const statusText = (status: ProductStatus) =>
  status === "out" ? "Out of Stock" : status[0].toUpperCase() + status.slice(1);
const toProduct = (
  product: AdminProduct,
  categoryMap: Map<string, string>,
): Product => ({
  id: product.id,
  name: product.name,
  slug: product.slug,
  sku: product.sku,
  category: product.categoryId,
  categoryLabel: categoryMap.get(product.categoryId) ?? "Unassigned",
  subcategory: "",
  description: product.description ?? product.shortDescription ?? "",
  price: `₹${Number(product.discountPrice ?? product.price).toLocaleString("en-IN")}`,
  mrp: `₹${Number(product.originalPrice ?? product.price).toLocaleString("en-IN")}`,
  stock: product.stock,
  status: product.stock === 0 ? "out" : (product.status as ProductStatus),
  featured: product.isFeatured,
  emoji: "📦",
  images: (product.images ?? []).map((image) => ({
    id: image.id,
    url: image.url,
    altText: image.altText,
    displayOrder: image.displayOrder,
    isPrimary: image.isPrimary,
  })),
});

export function AdminProductsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<
    Array<{ id: string; name: string; slug: string }>
  >([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [status, setStatus] = useState("all");
  const [selected, setSelected] = useState<string[]>([]);
  const [editing, setEditing] = useState("");
  const [modal, setModal] = useState<"form" | "delete" | "" | "view">("");
  const [target, setTarget] = useState<Product | null>(null);
  const [toast, setToast] = useState("");
  const [generatedDescription, setGeneratedDescription] = useState(false);
  const [generatedSeo, setGeneratedSeo] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [totalProducts, setTotalProducts] = useState(0);
  useEffect(() => {
    Promise.all([
      adminApi.listCategories(true),
      adminApi.listProducts({ page: 1, pageSize: 100 }),
    ])
      .then(([categoriesResult, productsResult]) => {
        const allCategories = categoriesResult.categories ?? [];
        setCategories(
          allCategories.map((item) => ({
            id: item.id,
            name: item.name,
            slug: item.slug,
          })),
        );
        const categoryMap = new Map(
          allCategories.map((item) => [item.id, item.name]),
        );
        setProducts(
          productsResult.products.items.map((product) =>
            toProduct(product, categoryMap),
          ),
        );
        setTotalProducts(productsResult.products.pagination.total);
      })
      .catch(() => {
        setError("Unable to load products and categories");
        setCategories([]);
        setProducts([]);
      })
      .finally(() => setLoading(false));
  }, []);
  const filtered = useMemo(
    () =>
      products.filter((product) => {
        const term = query.trim().toLowerCase();
        return (
          (!term ||
            `${product.name} ${product.sku} ${product.slug}`
              .toLowerCase()
              .includes(term)) &&
          (category === "all" || product.category === category) &&
          (status === "all" || product.status === status)
        );
      }),
    [products, query, category, status],
  );
  const stats = useMemo(
    () => ({
      total: totalProducts,
      active: products.filter((product) => product.status === "active").length,
      low: products.filter((product) => product.stock > 0 && product.stock < 20)
        .length,
      out: products.filter((product) => product.stock === 0).length,
    }),
    [products, totalProducts],
  );
  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2300);
  };
  const formik = useFormik<ProductForm>({
    initialValues: blankForm,
    validationSchema: yup.object({
      name: yup.string().required("Enter a product name"),
      slug: yup.string().required("Enter a slug"),
      sku: yup.string().required("Enter a SKU"),
      category: yup.string().required("Select a category"),
      price: yup.string().required("Enter a selling price"),
      stock: yup.string().required("Enter stock quantity"),
    }),
    onSubmit: async (values) => {
      const data = {
        name: values.name,
        slug: values.slug,
        sku: values.sku,
        categoryId: values.category,
        description: values.description,
        price: Number(values.price),
        originalPrice: values.mrp ? Number(values.mrp) : Number(values.price),
        stock: Number(values.stock),
        status: values.status,
        isFeatured: values.featured,
      };
      try {
        let savedProduct: AdminProduct;
        if (editing) {
          const result = await adminApi.updateProduct(editing, data);
          savedProduct = result.updateProduct;
        } else {
          const result = await adminApi.createProduct(data);
          savedProduct = result.createProduct;
        }
        const productId = savedProduct.id;
        // Upload newly added images (no id yet) to Cloudinary.
        for (const image of values.images.filter((item) => !item.id)) {
          await adminApi.uploadProductImage(
            productId,
            image.url,
            null,
            image.displayOrder,
            image.isPrimary,
          );
        }
        // Remove images the user deleted.
        for (const imageId of values.removedImages) {
          await adminApi.removeProductImage(imageId);
        }
        // Refetch so the saved product includes its fresh image list.
        const refreshed = (await adminApi.getProduct(productId)).product;
        const categoryMap = new Map(
          categories.map((item) => [item.id, item.name]),
        );
        const saved = toProduct(refreshed, categoryMap);
        setProducts((current) =>
          editing
            ? current.map((product) =>
                product.id === saved.id ? saved : product,
              )
            : [saved, ...current],
        );
        setModal("");
        notify("Product saved successfully");
      } catch (error) {
        notify(
          error instanceof Error ? error.message : "Product could not be saved",
        );
      }
    },
  });
  const form = formik.values;
  const setField = (
    key: keyof ProductForm,
    value: string | boolean | ProductImage[] | string[],
  ) => formik.setFieldValue(key, value);
  const create = () => {
    setEditing("");
    setGeneratedDescription(false);
    setGeneratedSeo(false);
    formik.resetForm({ values: { ...blankForm } });
    setModal("form");
  };
  const edit = (product: Product) => {
    setEditing(product.id);
    setGeneratedDescription(false);
    setGeneratedSeo(false);
    formik.setValues({
      ...blankForm,
      name: product.name,
      slug: product.slug,
      sku: product.sku,
      category: product.category,
      subcategory: product.subcategory,
      description: product.description,
      price: product.price.replace(/[₹,]/g, ""),
      mrp: product.mrp.replace(/[₹,]/g, ""),
      stock: String(product.stock),
      status: product.status,
      featured: product.featured,
      images: product.images.map((image) => ({ ...image })),
      removedImages: [],
      seoTitle: `${product.name} | PoojaPoint`,
    });
    setModal("form");
  };
  const addImages = async (event: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    const current = form.images;
    const remaining = 4 - current.length;
    const toAdd = files.slice(0, remaining);
    const newImages: ProductImage[] = await Promise.all(
      toAdd.map((file, index) =>
        new Promise<ProductImage>((resolve) => {
          const reader = new FileReader();
          reader.onload = () =>
            resolve({
              url: reader.result as string,
              displayOrder: current.length + index,
              isPrimary: current.length === 0 && index === 0,
            });
          reader.readAsDataURL(file);
        }),
      ),
    );
    setField("images", [...current, ...newImages]);
    event.target.value = "";
  };
  const removeImage = (index: number) => {
    const image = form.images[index];
    const next = form.images.filter((_, item) => item !== index);
    if (image.isPrimary && next.length) {
      next[0] = { ...next[0], isPrimary: true };
    }
    if (image.id) {
      setField("removedImages", [...form.removedImages, image.id]);
    }
    setField("images", next);
  };
  const setPrimary = (index: number) => {
    setField(
      "images",
      form.images.map((image, item) => ({
        ...image,
        isPrimary: item === index,
      })),
    );
  };
  const generateDescription = () => {
    const name = form.name || "This pooja product";
    const categoryName =
      categories.find((item) => item.id === form.category)?.name ??
      "devotional";
    setField(
      "description",
      `${name} is a thoughtfully crafted ${categoryName.toLowerCase()} essential for daily worship and festive rituals. Made for beautiful presentation and dependable use, it brings a refined touch to every sacred moment.`,
    );
    setGeneratedDescription(true);
  };
  const generateSeo = () => {
    const name = form.name || "PoojaPoint product";
    setField("seoTitle", `${name} | PoojaPoint`);
    setField(
      "seoDescription",
      `Shop ${name} at PoojaPoint. Discover quality devotional essentials with trusted service and convenient delivery.`,
    );
    setGeneratedSeo(true);
  };
  const undoDescription = () => {
    setField("description", "");
    setGeneratedDescription(false);
  };
  const undoSeo = () => {
    setField("seoTitle", "");
    setField("seoDescription", "");
    setGeneratedSeo(false);
  };
  const previewImage = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) formik.setFieldValue("image", URL.createObjectURL(file));
  };
  const exportProducts = () => {
    const csv = [
      "Name,SKU,Category,Price,Stock,Status",
      ...filtered.map(
        (item) =>
          `${item.name},${item.sku},${item.categoryLabel},${item.price},${item.stock},${item.status}`,
      ),
    ].join("\n");
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    link.download = "poojapoint-products.csv";
    link.click();
    notify("Preparing product export...");
  };
  const bulkAction = async (nextStatus: ProductStatus) => {
    try {
      const results = await Promise.all(
        selected.map((id) => adminApi.changeProductStatus(id, nextStatus)),
      );
      const categoryMap = new Map(
        categories.map((item) => [item.id, item.name]),
      );
      const changed = new Map(
        results.map((result) => [
          result.changeProductStatus.id,
          toProduct(result.changeProductStatus, categoryMap),
        ]),
      );
      setProducts((current) =>
        current.map((product) => changed.get(product.id) ?? product),
      );
      notify(`${selected.length} products changed to ${nextStatus}`);
      setSelected([]);
    } catch {
      notify("Product status could not be changed");
    }
  };
  const toggleSelected = (id: string) =>
    setSelected((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id],
    );

  return (
    <div className="admin-dashboard">
      <AdminIconSprite />
      <AdminSidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activeHref="/admin/products"
      />
      <main className="admin-main">
        <AdminHeader
          onMenu={() => setSidebarOpen(true)}
          query={query}
          onQuery={setQuery}
          title="Products"
          subtitle="Manage your PoojaPoint product catalog"
        />
        <div className="admin-content">
          <div className="products-exact-page">
            <div className="products-exact-top">
              <div>
                <div className="products-exact-heading">Product Catalog</div>
                <div className="products-exact-description">
                  Create, edit and manage every product in your store.
                </div>
              </div>
              <button
                className="products-exact-primary"
                type="button"
                onClick={create}
              >
                <AdminIcon name="plus" />
                Add Product
              </button>
            </div>
            <section className="products-exact-stats">
              {[
                ["products", "Total Products", String(stats.total)],
                ["products", "Active Products", String(stats.active)],
                ["products", "Low Stock", String(stats.low)],
                ["orders", "Out of Stock", String(stats.out)],
              ].map(([icon, name, value]) => (
                <div className="products-exact-stat" key={name}>
                  <div className="products-exact-stat-icon">
                    <AdminIcon name={icon as "products" | "orders"} />
                  </div>
                  <div>
                    <div className="products-exact-stat-label">{name}</div>
                    <div className="products-exact-stat-value">{value}</div>
                  </div>
                </div>
              ))}
            </section>
            {error && <div className="admin-error-state">{error}</div>}
            <section className="products-exact-panel">
              <div className="products-exact-toolbar">
                <div className="products-exact-toolbar-left">
                  <label className="products-exact-search">
                    <AdminIcon name="search" />
                    <input
                      type="search"
                      value={query}
                      onChange={(event) => setQuery(event.target.value)}
                      placeholder="Search product or SKU..."
                    />
                  </label>
                  <select
                    className="products-exact-select"
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                  >
                    <option value="all">All Categories</option>
                    {categories.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                  <select
                    className="products-exact-select"
                    value={status}
                    onChange={(event) => setStatus(event.target.value)}
                  >
                    <option value="all">All Status</option>
                    <option value="active">Active</option>
                    <option value="draft">Draft</option>
                    <option value="out">Out of Stock</option>
                  </select>
                </div>
                <div className="products-exact-toolbar-right">
                  <button
                    className="products-exact-tool"
                    type="button"
                    onClick={exportProducts}
                  >
                    <AdminIcon name="download" />
                    Export
                  </button>
                  <button
                    className="products-exact-tool"
                    type="button"
                    onClick={() => {
                      setQuery("");
                      setCategory("all");
                      setStatus("all");
                      notify("Filters cleared");
                    }}
                  >
                    Reset
                  </button>
                </div>
              </div>
              {selected.length > 0 && (
                <div className="products-exact-bulk">
                  <strong>{selected.length} selected</strong>
                  <div>
                    <button type="button" onClick={() => bulkAction("active")}>
                      Activate
                    </button>
                    <button type="button" onClick={() => bulkAction("draft")}>
                      Draft
                    </button>
                    <button type="button" onClick={() => setSelected([])}>
                      Clear
                    </button>
                  </div>
                </div>
              )}
              <div className="products-exact-table-wrap">
                <table className="products-exact-table">
                  <thead>
                    <tr>
                      <th>
                        <input
                          type="checkbox"
                          checked={
                            filtered.length > 0 &&
                            filtered.every((item) => selected.includes(item.id))
                          }
                          onChange={(event) =>
                            setSelected(
                              event.target.checked
                                ? filtered.map((item) => item.id)
                                : [],
                            )
                          }
                        />
                      </th>
                      {[
                        "Product",
                        "Category",
                        "Price",
                        "Stock",
                        "Status",
                        "Featured",
                        "Actions",
                      ].map((heading) => (
                        <th key={heading}>{heading}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((product) => (
                      <tr key={product.id}>
                        <td>
                          <input
                            type="checkbox"
                            checked={selected.includes(product.id)}
                            onChange={() => toggleSelected(product.id)}
                          />
                        </td>
                        <td>
                          <div className="products-exact-product">
                            <div className="products-exact-image">
                              {product.image ? (
                                <img src={product.image} alt="" />
                              ) : (
                                <span>{product.emoji}</span>
                              )}
                            </div>
                            <div>
                              <div className="products-exact-name">
                                {product.name}
                              </div>
                              <div className="products-exact-sku">
                                SKU: {product.sku}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="products-exact-category">
                            {product.categoryLabel}
                          </div>
                          <div className="products-exact-sub">
                            {product.subcategory}
                          </div>
                        </td>
                        <td>
                          <div className="products-exact-price">
                            {product.price}
                          </div>
                          <div className="products-exact-old">
                            {product.mrp}
                          </div>
                        </td>
                        <td>
                          <div
                            className={`products-exact-stock ${product.stock === 0 ? "out" : product.stock < 20 ? "low" : "good"}`}
                          >
                            {product.stock}
                          </div>
                          <div className="products-exact-sub">
                            {product.stock === 0
                              ? "Out of stock"
                              : product.stock < 20
                                ? "Low stock"
                                : "In stock"}
                          </div>
                        </td>
                        <td>
                          <span
                            className={`products-exact-status ${product.status}`}
                          >
                            {statusText(product.status)}
                          </span>
                        </td>
                        <td>
                          <button
                            className={`products-exact-toggle ${product.featured ? "active" : ""}`}
                            type="button"
                            aria-label={`Toggle featured for ${product.name}`}
                            onClick={async () => {
                              try {
                                const result = await adminApi.setProductFeatured(product.id, !product.featured);
                                const categoryMap = new Map(categories.map((item) => [item.id, item.name]));
                                const updated = toProduct(result.setProductFeatured, categoryMap);
                                setProducts((current) => current.map((item) => item.id === updated.id ? updated : item));
                                notify(product.featured ? "Removed from featured" : "Product featured");
                              } catch (toggleError) {
                                notify(toggleError instanceof Error ? toggleError.message : "Unable to update featured status");
                              }
                            }}
                          />
                        </td>
                        <td>
                          <div className="products-exact-actions">
                            <button
                              type="button"
                              aria-label={`View ${product.name}`}
                              onClick={() => {
                                setTarget(product);
                                setModal("view");
                              }}
                            >
                              <AdminIcon name="eye" />
                            </button>
                            <button
                              type="button"
                              aria-label={`Edit ${product.name}`}
                              onClick={() => edit(product)}
                            >
                              <AdminIcon name="edit" />
                            </button>
                            <button
                              type="button"
                              aria-label={`Duplicate ${product.name}`}
                              onClick={async () => {
                                try {
                                  const result = await adminApi.createProduct({
                                    categoryId: product.category,
                                    name: `${product.name} Copy`,
                                    slug: `${product.slug}-copy-${Date.now()}`,
                                    sku: `${product.sku}-COPY-${Date.now()}`,
                                    description: product.description || null,
                                    price: Number(product.price.replace(/[₹,]/g, "")),
                                    originalPrice: Number(product.mrp.replace(/[₹,]/g, "")),
                                    stock: product.stock,
                                    status: "draft",
                                    isFeatured: false,
                                  });
                                  const categoryMap = new Map(categories.map((item) => [item.id, item.name]));
                                  setProducts((current) => [toProduct(result.createProduct, categoryMap), ...current]);
                                  setTotalProducts((current) => current + 1);
                                  notify(`${product.name} duplicated successfully`);
                                } catch (duplicateError) {
                                  notify(duplicateError instanceof Error ? duplicateError.message : "Unable to duplicate product");
                                }
                              }}
                            >
                              <AdminIcon name="copy" />
                            </button>
                            <button
                              className="delete"
                              type="button"
                              aria-label={`Delete ${product.name}`}
                              onClick={() => {
                                setTarget(product);
                                setModal("delete");
                              }}
                            >
                              <AdminIcon name="trash" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {loading && <div className="admin-empty-state">Loading products...</div>}
                {!loading && !filtered.length && (
                  <div className="admin-empty-state">
                    No products match the selected filters.
                  </div>
                )}
              </div>
              <div className="products-exact-pagination">
                <span>
                  Showing {filtered.length ? 1 : 0}–{filtered.length} of {totalProducts} products
                </span>
              </div>
            </section>
          </div>
        </div>
      </main>
      {modal === "form" && (
        <div className="products-exact-modal-overlay" role="presentation">
          <div className="products-exact-modal">
            <div className="products-exact-modal-header">
              <div>
                <div className="products-exact-modal-title">
                  {editing ? "Edit Product" : "Add Product"}
                </div>
                <div className="products-exact-modal-subtitle">
                  Create or update your store product
                </div>
              </div>
              <button type="button" onClick={() => setModal("")}>
                <AdminIcon name="close" />
              </button>
            </div>
            <form onSubmit={formik.handleSubmit} noValidate>
              <div className="products-exact-modal-body">
                <div className="products-exact-form-grid">
                  <div className="products-exact-form-group full">
                    <label>Product Images (up to 4)</label>
                    <div className="products-exact-images">
                      {form.images.map((image, index) => (
                        <div
                          className={`products-exact-image-item ${image.isPrimary ? "primary" : ""}`}
                          key={`${image.id ?? "new"}-${index}`}
                        >
                          <img src={image.url} alt="" />
                          <div className="products-exact-image-actions">
                            <button
                              type="button"
                              title="Set as primary image"
                              aria-label="Set as primary image"
                              onClick={() => setPrimary(index)}
                            >
                              <AdminIcon name="check" />
                            </button>
                            <button
                              className="delete"
                              type="button"
                              title="Remove image"
                              aria-label="Remove image"
                              onClick={() => removeImage(index)}
                            >
                              <AdminIcon name="trash" />
                            </button>
                          </div>
                          {image.isPrimary && (
                            <span className="products-exact-image-badge">
                              Primary
                            </span>
                          )}
                        </div>
                      ))}
                      {form.images.length < 4 && (
                        <label className="products-exact-upload">
                          <AdminIcon name="upload" />
                          <strong>Add Image</strong>
                          <span>
                            {4 - form.images.length} more allowed · PNG, JPG or
                            WEBP
                          </span>
                          <input
                            type="file"
                            accept="image/*"
                            multiple
                            onChange={addImages}
                          />
                        </label>
                      )}
                    </div>
                  </div>
                  {[
                    ["name", "Product Name", "e.g. Premium Brass Diya"],
                    ["slug", "Slug", "premium-brass-diya"],
                    ["sku", "SKU", "PP-DIYA-001"],
                    ["subcategory", "Sub Category", "Traditional"],
                    ["price", "Selling Price", "549"],
                    ["mrp", "MRP", "699"],
                    ["discount", "Discount %", "21"],
                    ["stock", "Stock Quantity", "100"],
                    ["lowStock", "Low Stock Alert", "10"],
                    ["weight", "Weight", "e.g. 250g"],
                    [
                      "seoTitle",
                      "SEO Title",
                      "Premium Brass Diya | PoojaPoint",
                    ],
                  ].map(([key, name, placeholder]) => (
                    <div className="products-exact-form-group" key={key}>
                      <label>
                        {name}
                        {["name", "slug", "sku", "price", "stock"].includes(key) && (
                          <span> *</span>
                        )}
                      </label>
                      <input
                        required={["name", "slug", "sku", "price", "stock"].includes(
                          key,
                        )}
                        value={form[key as keyof ProductForm] as string}
                        onChange={(event) =>
                          setField(key as keyof ProductForm, event.target.value)
                        }
                        placeholder={placeholder}
                      />
                      {Boolean(
                        formik.touched[key as keyof ProductForm] &&
                          formik.errors[key as keyof ProductForm],
                      ) && (
                        <small className="form-error">
                          {String(formik.errors[key as keyof ProductForm])}
                        </small>
                      )}
                    </div>
                  ))}
                  <div className="products-exact-form-group">
                    <label>
                      Category <span>*</span>
                    </label>
                    <select
                      required
                      value={form.category}
                      onChange={(event) =>
                        setField("category", event.target.value)
                      }
                    >
                      <option value="">Select Category</option>
                      {categories.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.name}
                        </option>
                      ))}
                    </select>
                    {formik.touched.category && formik.errors.category && (
                      <small className="form-error">
                        {formik.errors.category}
                      </small>
                    )}
                  </div>
                  <div className="products-exact-form-group">
                    <label>Status</label>
                    <select
                      value={form.status}
                      onChange={(event) =>
                        setField("status", event.target.value)
                      }
                    >
                      <option value="active">Active</option>
                      <option value="draft">Draft</option>
                      <option value="out">Out of Stock</option>
                    </select>
                  </div>
                  {[
                    [
                      "description",
                      "Description",
                      "Write a beautiful product description...",
                    ],
                    [
                      "seoDescription",
                      "SEO Description",
                      "SEO description for Google...",
                    ],
                  ].map(([key, name, placeholder]) => (
                    <div className="products-exact-form-group full" key={key}>
                      <label>{name}</label>
                      <textarea
                        value={form[key as keyof ProductForm] as string}
                        onChange={(event) =>
                          setField(key as keyof ProductForm, event.target.value)
                        }
                        placeholder={placeholder}
                      />
                      <div className="products-exact-ai-actions">
                        <button
                          type="button"
                          onClick={
                            key === "description"
                              ? generateDescription
                              : generateSeo
                          }
                        >
                          <AdminIcon name="ai" />
                          AI Generate Text
                        </button>
                        {(key === "description"
                          ? generatedDescription
                          : generatedSeo) && (
                          <button
                            className="undo"
                            type="button"
                            onClick={
                              key === "description" ? undoDescription : undoSeo
                            }
                          >
                            <AdminIcon name="arrow-left" />
                            Undo
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                  <label className="products-exact-check full">
                    <input
                      type="checkbox"
                      checked={form.featured}
                      onChange={(event) =>
                        setField("featured", event.target.checked)
                      }
                    />
                    Show this product as a featured product
                  </label>
                </div>
              </div>
              <div className="products-exact-modal-footer">
                <button type="button" onClick={() => setModal("")}>
                  Cancel
                </button>
                <button className="primary" type="submit">
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {modal === "delete" && (
        <div className="products-exact-modal-overlay">
          <div className="products-exact-modal small">
            <div className="products-exact-modal-header">
              <div className="products-exact-modal-title">Delete Product?</div>
              <button type="button" onClick={() => setModal("")}>
                <AdminIcon name="close" />
              </button>
            </div>
            <div className="products-exact-modal-body">
              <p className="products-exact-delete-message">
                This action will remove the product from your catalog. You can
                instead move it to draft if you may need it later.
              </p>
              <div className="products-exact-delete-name">{target?.name}</div>
            </div>
            <div className="products-exact-modal-footer">
              <button type="button" onClick={() => setModal("")}>
                Cancel
              </button>
              <button
                className="danger"
                type="button"
                onClick={async () => {
                  if (!target) return;
                  try {
                    await adminApi.deleteProduct(target.id);
                    setProducts((current) => current.filter((item) => item.id !== target.id));
                    setTotalProducts((current) => Math.max(0, current - 1));
                    setModal("");
                    notify(`${target.name} deleted`);
                  } catch (deleteError) {
                    notify(deleteError instanceof Error ? deleteError.message : "Unable to delete product");
                  }
                }}
              >
                Delete Product
              </button>
            </div>
          </div>
        </div>
      )}
      {modal === "view" && target && (
        <div className="products-exact-modal-overlay">
          <div className="products-exact-modal small">
            <div className="products-exact-modal-header">
              <div className="products-exact-modal-title">Product Details</div>
              <button type="button" onClick={() => setModal("")}>
                <AdminIcon name="close" />
              </button>
            </div>
            <div className="products-exact-modal-body">
              <div className="products-exact-view-image">
                {target.images[0] ? (
                  <img src={target.images[0].url} alt="" />
                ) : (
                  target.emoji
                )}
              </div>
              {target.images.length > 1 && (
                <div className="products-exact-view-thumbs">
                  {target.images.map((image) => (
                    <img
                      key={image.id ?? image.url}
                      src={image.url}
                      alt=""
                      className={image.isPrimary ? "primary" : ""}
                    />
                  ))}
                </div>
              )}
              <h3>{target.name}</h3>
              <p>
                {target.categoryLabel} · {target.sku}
              </p>
              <strong>{target.price}</strong>
              <p>{target.stock} units in stock</p>
            </div>
          </div>
        </div>
      )}
      {toast && <div className="coupon-exact-toast show">{toast}</div>}
    </div>
  );
}
