"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";
import { adminApi, type AdminReview } from "../../../services/api/admin.api";

type ReviewStatus = "approved" | "pending" | "flagged";

type Review = {
	id: string;
	product: string;
	productSku: string;
	customer: string;
	initials: string;
	rating: number;
	title: string;
	comment: string;
	date: string;
	status: ReviewStatus;
	verified: boolean;
	helpful: number;
	replies: number;
};

const titleCase = (value: string) => value[0].toUpperCase() + value.slice(1);

const starRow = (rating: number) => Array.from({ length: 5 }, (_, index) => (
	<span key={`${rating}-${index}`} className={index < rating ? "reviews-exact-star filled" : "reviews-exact-star"}>★</span>
));

const initialsOf = (name: string) => name.split(" ").filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase() || "?";

const formatDate = (value: string) => {
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return value;
	return date.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
};

const toReview = (item: AdminReview): Review => {
	const customer = item.customerName || "Unknown customer";
	return {
		id: item.id,
		product: item.productName || "Unknown product",
		productSku: item.productId,
		customer,
		initials: initialsOf(customer),
		rating: item.rating,
		title: item.title || "",
		comment: item.comment || "",
		date: formatDate(item.createdAt),
		status: (item.status as ReviewStatus) || "pending",
		verified: item.isVerifiedPurchase,
		helpful: item.helpfulCount,
		replies: item.replyCount,
	};
};

export function AdminReviewsPage() {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [reviews, setReviews] = useState<Review[]>([]);
	const [loading, setLoading] = useState(true);
	const [page, setPage] = useState(1);
	const [total, setTotal] = useState(0);
	const [query, setQuery] = useState("");
	const [debouncedQuery, setDebouncedQuery] = useState("");
	const [status, setStatus] = useState("all");
	const [rating, setRating] = useState("all");
	const [toast, setToast] = useState("");

	useEffect(() => {
		const timer = window.setTimeout(() => setDebouncedQuery(query), 350);
		return () => window.clearTimeout(timer);
	}, [query]);

	const load = useCallback(async (nextPage: number, nextStatus: string, nextQuery: string) => {
		setLoading(true);
		try {
			const { reviews: result } = await adminApi.listReviews({
				page: nextPage,
				pageSize: 20,
				status: nextStatus === "all" ? undefined : nextStatus,
				search: nextQuery || undefined,
			});
			setReviews(result.items.map(toReview));
			setTotal(result.pagination.total);
			setPage(nextPage);
		} catch {
			setReviews([]);
			setTotal(0);
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		load(1, status, debouncedQuery);
	}, [load, status, debouncedQuery]);

	const filtered = useMemo(() => reviews.filter((review) => rating === "all" || review.rating >= Number(rating)), [rating, reviews]);

	const notify = (message: string) => {
		setToast(message);
		window.setTimeout(() => setToast(""), 2300);
	};

	const setReviewStatus = async (id: string, nextStatus: ReviewStatus) => {
		try {
			await adminApi.moderateReview(id, nextStatus);
			setReviews((current) => current.map((review) => review.id === id ? { ...review, status: nextStatus } : review));
			notify(`Review marked as ${nextStatus}`);
		} catch {
			notify("Failed to update review status");
		}
	};

	const deleteReview = async (id: string) => {
		const review = reviews.find((item) => item.id === id);
		try {
			await adminApi.deleteReview(id);
			setReviews((current) => current.filter((item) => item.id !== id));
			if (review) notify(`${review.customer}'s review removed`);
		} catch {
			notify("Failed to delete review");
		}
	};

	const reset = () => {
		setQuery("");
		setStatus("all");
		setRating("all");
		notify("Filters cleared");
	};

	const exportReviews = () => {
		const csv = ["Product,SKU,Customer,Rating,Title,Comment,Status,Date", ...filtered.map((review) => `"${review.product}","${review.productSku}","${review.customer}",${review.rating},"${review.title}","${review.comment}","${review.status}","${review.date}"`)].join("\n");
		const link = document.createElement("a");
		link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
		link.download = "poojapoint-reviews.csv";
		link.click();
		notify("Preparing review export...");
	};

	const totalPages = Math.max(1, Math.ceil(total / 20));
	const avgRating = reviews.length ? (reviews.reduce((sum, item) => sum + item.rating, 0) / reviews.length).toFixed(1) : "0.0";

	return <div className="admin-dashboard">
		<AdminIconSprite />
		<AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} activeHref="/admin/reviews" />
		<main className="admin-main">
			<AdminHeader onMenu={() => setSidebarOpen(true)} query={query} onQuery={setQuery} title="Reviews" subtitle="Customer feedback and product ratings" />
			<div className="admin-content">
				<div className="reviews-exact-page">
					<div className="reviews-exact-top">
						<div>
							<div className="reviews-exact-heading">Product Reviews</div>
							<div className="reviews-exact-description">Monitor product feedback, highlight loyalty and resolve customer concerns quickly.</div>
						</div>
						<button className="reviews-exact-primary" type="button" onClick={exportReviews}>Export Reviews</button>
					</div>

					<section className="reviews-exact-stats">
						{[
							["products", "Total Reviews", String(total)],
							["check", "Approved", String(reviews.filter((review) => review.status === "approved").length)],
							["customers", "Pending", String(reviews.filter((review) => review.status === "pending").length)],
							["trend", "Avg. Rating", `${avgRating} / 5`],
						].map(([icon, name, value]) => <div className="reviews-exact-stat" key={name}><div className="reviews-exact-stat-icon"><AdminIcon name={icon as "products" | "check" | "customers" | "trend"} /></div><div><div className="reviews-exact-stat-label">{name}</div><div className="reviews-exact-stat-value">{value}</div></div></div>)}
					</section>

					<section className="reviews-exact-panel">
						<div className="reviews-exact-toolbar">
							<div className="reviews-exact-toolbar-left">
								<label className="reviews-exact-search">
									<AdminIcon name="search" />
									<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search product or customer..." />
								</label>
								<select className="reviews-exact-select" value={status} onChange={(event) => setStatus(event.target.value)}>
									<option value="all">All Status</option>
									<option value="approved">Approved</option>
									<option value="pending">Pending</option>
									<option value="flagged">Flagged</option>
								</select>
								<select className="reviews-exact-select" value={rating} onChange={(event) => setRating(event.target.value)}>
									<option value="all">All Ratings</option>
									<option value="5">5★ & above</option>
									<option value="4">4★ & above</option>
									<option value="3">3★ & above</option>
								</select>
							</div>
							<div className="reviews-exact-toolbar-right">
								<button className="reviews-exact-tool" type="button" onClick={reset}>Reset</button>
							</div>
						</div>

						<div className="reviews-exact-table-wrap">
							<table className="reviews-exact-table">
								<thead>
									<tr>
										<th>Product</th>
										<th>Customer</th>
										<th>Rating</th>
										<th>Review</th>
										<th>Date</th>
										<th>Status</th>
										<th>Actions</th>
									</tr>
								</thead>
								<tbody>
									{filtered.map((review) => <tr key={review.id}>
										<td>
											<div className="reviews-exact-product">
												<div className="reviews-exact-product-icon">🪔</div>
												<div>
													<div className="reviews-exact-name">{review.product}</div>
													<div className="reviews-exact-sub">{review.productSku}</div>
												</div>
											</div>
										</td>
										<td>
											<div className="reviews-exact-customer">
												<div className="reviews-exact-avatar">{review.initials}</div>
												<div>
													<div className="reviews-exact-name">{review.customer}</div>
													<div className="reviews-exact-sub">{review.verified ? "Verified buyer" : "Guest buyer"}</div>
												</div>
											</div>
										</td>
										<td>
											<div className="reviews-exact-rating">{starRow(review.rating)}</div>
											<div className="reviews-exact-sub">{review.rating}.0 / 5</div>
										</td>
										<td>
											<div className="reviews-exact-review-title">{review.title}</div>
											<div className="reviews-exact-review-copy">{review.comment}</div>
										</td>
										<td>
											<div className="reviews-exact-date">{review.date}</div>
											<div className="reviews-exact-sub">{review.helpful} helpful · {review.replies} replies</div>
										</td>
										<td><span className={`reviews-exact-status ${review.status}`}>{titleCase(review.status)}</span></td>
										<td>
											<div className="reviews-exact-actions">
												<button type="button" aria-label={`Approve ${review.customer}`} onClick={() => setReviewStatus(review.id, "approved")}><AdminIcon name="check" /></button>
												<button type="button" aria-label={`Flag ${review.customer}`} onClick={() => setReviewStatus(review.id, "flagged")}><AdminIcon name="alert" /></button>
												<button className="danger" type="button" aria-label={`Delete ${review.customer}`} onClick={() => deleteReview(review.id)}><AdminIcon name="trash" /></button>
											</div>
										</td>
									</tr>)}
								</tbody>
							</table>
							{loading && <div className="admin-empty-state">Loading reviews...</div>}
							{!loading && !filtered.length && <div className="admin-empty-state">No reviews match the selected filters.</div>}
						</div>

						<div className="reviews-exact-pagination">
							<span>Showing {filtered.length} of {total} reviews</span>
							<div>
								<button type="button" disabled={page <= 1} onClick={() => load(page - 1, status, debouncedQuery)}>‹</button>
								{Array.from({ length: totalPages }, (_, index) => index + 1).map((item) => <button className={item === page ? "active" : ""} type="button" key={item} onClick={() => load(item, status, debouncedQuery)}>{item}</button>)}
								<button type="button" disabled={page >= totalPages} onClick={() => load(page + 1, status, debouncedQuery)}>›</button>
							</div>
						</div>
					</section>
				</div>
			</div>
		</main>
		{toast && <div className="coupon-exact-toast show">{toast}</div>}
	</div>;
}
