import { adminGraphqlClient } from "./client";

export type Page<T> = { items: T[]; pagination: Pagination };
export type Pagination = { page: number; pageSize: number; total: number; totalPages: number; hasNext: boolean; hasPrevious: boolean };
export type AdminProduct = { id: string; categoryId: string; name: string; slug: string; sku: string; shortDescription?: string | null; description?: string | null; price: number; originalPrice?: number | null; discountPrice?: number | null; stock: number; status: string; isActive: boolean; isFeatured: boolean; averageRating: number; reviewCount: number; createdAt: string; updatedAt: string };
export type AdminCategory = { id: string; parentId?: string | null; name: string; slug: string; description?: string | null; imageUrl?: string | null; emoji?: string | null; seoTitle?: string | null; seoDescription?: string | null; displayOrder: number; isActive: boolean; isFeatured: boolean; createdAt: string; updatedAt: string };
export type AdminOrder = Record<string, unknown>;
export type AdminCustomer = Record<string, unknown>;
export type AdminCoupon = Record<string, unknown>;
export type AdminReview = { id: string; productId: string; userId: string; rating: number; title?: string | null; comment?: string | null; status: string; isVerifiedPurchase: boolean; helpfulCount: number; replyCount: number; createdAt: string; updatedAt: string; productName?: string | null; customerName?: string | null };
export type Dashboard = {
	totalOrders: number;
	totalCustomers: number;
	totalProducts: number;
	revenue: number;
	averageOrderValue: number;
	conversionRate: number;
	refundAmount: number;
	revenueGrowth: number;
	sales: Array<{ period: string; value: number }>;
	categories: Array<{ categoryId: string; name: string; count: number; sales: number }>;
	recentOrders: Array<{ orderId: string; customerName: string; customerEmail: string; amount: number; paymentMethod: string; status: string }>;
	stockAlerts: Array<{ productId: string; productName: string; sku: string; quantity: number }>;
};
export type MutationResult = { success: boolean; message: string };
export type AdminAnalytics = { startDate: string; endDate: string; revenue: number; orderCount: number; customerCount: number; categoryRevenue: Array<{ categoryName: string; revenue: number; percentage: number }>; topProducts: Array<{ productName: string; unitsSold: number; revenue: number }>; paymentBreakdown: Array<{ paymentMethod: string; count: number; amount: number }> };
export type AdminReport = { name: string; generatedAt: string; data: unknown[] };
export type AdminHero = { id: string; title: string; subtitle?: string | null; badge?: string | null; accent?: string | null; ctaLabel?: string | null; ctaLink?: string | null; displayOrder: number; seoTitle?: string | null; seoDescription?: string | null; isActive: boolean; images: Array<{ id: string; url: string; altText?: string | null; mediaType: string; displayOrder: number; isPrimary: boolean; cropX: number; cropY: number; cropZoom: number }> };
export type AdminSetting = { id: string; key: string; value: unknown; isPublic: boolean };
export type AdminIpPolicy = { id: string; ipAddress: string; status: string; location?: string | null; region?: string | null; note?: string | null; createdAt?: string | null; updatedAt?: string | null };
export type AdminActivityLog = { id: string; actorId?: string | null; action: string; level: string; resource?: string | null; resourceId?: string | null; ipAddress?: string | null; userAgent?: string | null; metadataJson?: unknown; details?: string | null; status?: string | null; createdAt: string; updatedAt: string };
export type AdminWishlistOverview = { itemCount: number; wishlistCount: number; productCount: number; potentialRevenue: number };

const productFields = `id categoryId name slug sku shortDescription description price originalPrice discountPrice stock status isActive isFeatured averageRating reviewCount createdAt updatedAt`;
const categoryFields = `id parentId name slug description imageUrl emoji seoTitle seoDescription displayOrder isActive isFeatured createdAt updatedAt`;
const reviewFields = `id productId userId rating title comment status isVerifiedPurchase helpfulCount replyCount createdAt updatedAt productName customerName`;
const activityLogFields = `id actorId action level resource resourceId ipAddress userAgent metadataJson details status createdAt updatedAt`;

const request = <T>(query: string, variables: Record<string, unknown> = {}, token?: string) => adminGraphqlClient<T>(query, variables, token);

export const adminApi = {
	getAnalytics: (startDate: string, endDate: string) => request<{ analytics: AdminAnalytics }>(`query Analytics($startDate: Date!, $endDate: Date!) { analytics(startDate: $startDate, endDate: $endDate) { startDate endDate revenue orderCount customerCount categoryRevenue { categoryName revenue percentage } topProducts { productName unitsSold revenue } paymentBreakdown { paymentMethod count amount } } }`, { startDate, endDate }),
	getReport: (reportType: string, fromDate?: string, toDate?: string) => request<{ report: AdminReport }>(`query Report($reportType: String!, $fromDate: Date, $toDate: Date) { report(reportType: $reportType, fromDate: $fromDate, toDate: $toDate) { name generatedAt data } }`, { reportType, fromDate, toDate }),
	listHeroes: () => request<{ heroes: AdminHero[] }>(`query { heroes { id title subtitle badge accent ctaLabel ctaLink displayOrder seoTitle seoDescription isActive images { id url altText mediaType displayOrder isPrimary cropX cropY cropZoom } } }`),
	listSettings: () => request<{ settings: AdminSetting[] }>(`query { settings { id key value isPublic } }`),
	listIpPolicies: () => request<{ ipPolicies: AdminIpPolicy[] }>(`query { ipPolicies { id ipAddress status location region note createdAt updatedAt } }`),
	listWishlistSummary: () => request<{ wishlistOverview: AdminWishlistOverview; topWishlistProducts: Array<{ productId: string; productName: string; wishlistCount: number; price: number }> }>(`query { wishlistOverview { itemCount wishlistCount productCount potentialRevenue } topWishlistProducts { productId productName wishlistCount price } }`),
	upsertSetting: (key: string, value: unknown, isPublic = false) => request<{ upsertSetting: AdminSetting }>(`mutation UpsertSetting($key: String!, $value: JSON!, $isPublic: Boolean!) { upsertSetting(key: $key, value: $value, isPublic: $isPublic) { id key value isPublic } }`, { key, value, isPublic }),
	setHeroActive: (id: string, isActive: boolean) => request<{ setHeroActive: AdminHero }>(`mutation SetHeroActive($id: UUID!, $isActive: Boolean!) { setHeroActive(id: $id, isActive: $isActive) { id isActive } }`, { id, isActive }),
	createIpPolicy: (ipAddress: string, status: string, location?: string, region?: string, note?: string) => request<{ createIpPolicy: AdminIpPolicy }>(`mutation CreateIpPolicy($ipAddress: String!, $status: String!, $location: String, $region: String, $note: String) { createIpPolicy(ipAddress: $ipAddress, status: $status, location: $location, region: $region, note: $note) { id ipAddress status location region note createdAt updatedAt } }`, { ipAddress, status, location, region, note }),
	updateIpPolicy: (id: string, status: string, note?: string) => request<{ updateIpPolicy: AdminIpPolicy }>(`mutation UpdateIpPolicy($id: UUID!, $status: String!, $note: String) { updateIpPolicy(id: $id, status: $status, note: $note) { id ipAddress status location region note createdAt updatedAt } }`, { id, status, note }),
	deleteIpPolicy: (id: string) => request<{ deleteIpPolicy: MutationResult }>(`mutation DeleteIpPolicy($id: UUID!) { deleteIpPolicy(id: $id) { success message } }`, { id }),
	listActivityLogs: (variables: { page?: number; pageSize?: number; level?: string; resource?: string; search?: string } = {}, token?: string) => request<{ activityLogs: Page<AdminActivityLog> }>(`query ActivityLogs($page: Int, $pageSize: Int, $level: String, $resource: String, $search: String) { activityLogs(page: $page, pageSize: $pageSize, level: $level, resource: $resource, search: $search) { items { ${activityLogFields} } pagination { page pageSize total totalPages hasNext hasPrevious } } }`, variables, token),
	getActivityLog: (id: string, token?: string) => request<{ activityLog: AdminActivityLog }>(`query ActivityLog($id: UUID!) { activityLog(id: $id) { ${activityLogFields} } }`, { id }, token),
	createActivityLog: (data: Record<string, unknown>, token?: string) => request<{ createActivityLog: AdminActivityLog }>(`mutation CreateActivityLog($data: ActivityLogInput!) { createActivityLog(data: $data) { ${activityLogFields} } }`, { data }, token),
	updateActivityLog: (id: string, data: Record<string, unknown>, token?: string) => request<{ updateActivityLog: AdminActivityLog }>(`mutation UpdateActivityLog($id: UUID!, $data: ActivityLogUpdateInput!) { updateActivityLog(id: $id, data: $data) { ${activityLogFields} } }`, { id, data }, token),
	deleteActivityLog: (id: string, token?: string) => request<{ deleteActivityLog: MutationResult }>(`mutation DeleteActivityLog($id: UUID!) { deleteActivityLog(id: $id) { success message } }`, { id }, token),
	clearActivityLogs: (token?: string) => request<{ clearActivityLogs: MutationResult }>(`mutation { clearActivityLogs { success message } }`, {}, token),
	getDashboard: (token?: string) => request<{ dashboard: Dashboard }>(`query { dashboard { totalOrders totalCustomers totalProducts revenue averageOrderValue conversionRate refundAmount revenueGrowth sales { period value } categories { categoryId name count sales } recentOrders { orderId customerName customerEmail amount paymentMethod status } stockAlerts { productId productName sku quantity } } }`, {}, token),
	listProducts: (variables: { page?: number; pageSize?: number; search?: string; categoryId?: string; status?: string } = {}, token?: string) => request<{ products: Page<AdminProduct> }>(`query Products($page: Int, $pageSize: Int, $search: String, $categoryId: UUID, $status: String) { products(page: $page, pageSize: $pageSize, search: $search, categoryId: $categoryId, status: $status) { items { ${productFields} } pagination { page pageSize total totalPages hasNext hasPrevious } } }`, variables, token),
	getProduct: (id: string, token?: string) => request<{ product: AdminProduct }>(`query Product($id: UUID!) { product(id: $id) { ${productFields} } }`, { id }, token),
	listCategories: (includeInactive = false, token?: string) => request<{ categories: AdminCategory[] }>(`query Categories($includeInactive: Boolean) { categories(includeInactive: $includeInactive) { ${categoryFields} } }`, { includeInactive }, token),
	listOrders: (variables: { page?: number; pageSize?: number; status?: string; search?: string } = {}, token?: string) => request<{ orders: Page<AdminOrder> }>(`query Orders($page: Int, $pageSize: Int, $status: String, $search: String) { orders(page: $page, pageSize: $pageSize, status: $status, search: $search) { items { id status } pagination { page pageSize total totalPages hasNext hasPrevious } } }`, variables, token),
	listCustomers: (variables: { page?: number; pageSize?: number; search?: string; status?: string } = {}, token?: string) => request<{ customers: Page<AdminCustomer> }>(`query Customers($page: Int, $pageSize: Int, $search: String, $status: String) { customers(page: $page, pageSize: $pageSize, search: $search, status: $status) { items { id } pagination { page pageSize total totalPages hasNext hasPrevious } } }`, variables, token),
	listCoupons: (variables: { page?: number; pageSize?: number; search?: string; isActive?: boolean } = {}, token?: string) => request<{ coupons: Page<AdminCoupon> }>(`query Coupons($page: Int, $pageSize: Int, $search: String, $isActive: Boolean) { coupons(page: $page, pageSize: $pageSize, search: $search, isActive: $isActive) { items { id } pagination { page pageSize total totalPages hasNext hasPrevious } } }`, variables, token),
	listReviews: (variables: { page?: number; pageSize?: number; status?: string; search?: string; productId?: string } = {}, token?: string) => request<{ reviews: Page<AdminReview> }>(`query Reviews($page: Int, $pageSize: Int, $status: String, $search: String, $productId: UUID) { reviews(page: $page, pageSize: $pageSize, status: $status, search: $search, productId: $productId) { items { ${reviewFields} } pagination { page pageSize total totalPages hasNext hasPrevious } } }`, variables, token),
	createProduct: (data: Record<string, unknown>, token?: string) => request<{ createProduct: AdminProduct }>(`mutation CreateProduct($data: ProductInput!) { createProduct(data: $data) { ${productFields} } }`, { data }, token),
	updateProduct: (id: string, data: Record<string, unknown>, token?: string) => request<{ updateProduct: AdminProduct }>(`mutation UpdateProduct($id: UUID!, $data: ProductUpdateInput!) { updateProduct(id: $id, data: $data) { ${productFields} } }`, { id, data }, token),
	deleteProduct: (id: string, token?: string) => request<{ deleteProduct: MutationResult }>(`mutation DeleteProduct($id: UUID!) { deleteProduct(id: $id) { success message } }`, { id }, token),
	changeProductStatus: (id: string, status: string, token?: string) => request<{ changeProductStatus: AdminProduct }>(`mutation ChangeProductStatus($id: UUID!, $status: String!) { changeProductStatus(id: $id, status: $status) { ${productFields} } }`, { id, status }, token),
	setProductFeatured: (id: string, isFeatured: boolean, token?: string) => request<{ setProductFeatured: AdminProduct }>(`mutation SetProductFeatured($id: UUID!, $isFeatured: Boolean!) { setProductFeatured(id: $id, isFeatured: $isFeatured) { ${productFields} } }`, { id, isFeatured }, token),
	updateProductStock: (id: string, stock: number, token?: string) => request<{ updateProductStock: AdminProduct }>(`mutation UpdateProductStock($id: UUID!, $stock: Int!) { updateProductStock(id: $id, stock: $stock) { ${productFields} } }`, { id, stock }, token),
	createCategory: (data: Record<string, unknown>, token?: string) => request<{ createCategory: AdminCategory }>(`mutation CreateCategory($data: CategoryInput!) { createCategory(data: $data) { ${categoryFields} } }`, { data }, token),
	updateCategory: (id: string, data: Record<string, unknown>, token?: string) => request<{ updateCategory: AdminCategory }>(`mutation UpdateCategory($id: UUID!, $data: CategoryUpdateInput!) { updateCategory(id: $id, data: $data) { ${categoryFields} } }`, { id, data }, token),
	deleteCategory: (id: string, token?: string) => request<{ deleteCategory: MutationResult }>(`mutation DeleteCategory($id: UUID!) { deleteCategory(id: $id) { success message } }`, { id }, token),
	setCategoryActive: (id: string, isActive: boolean, token?: string) => request<{ setCategoryActive: AdminCategory }>(`mutation SetCategoryActive($id: UUID!, $isActive: Boolean!) { setCategoryActive(id: $id, isActive: $isActive) { ${categoryFields} } }`, { id, isActive }, token),
	setCategoryFeatured: (id: string, isFeatured: boolean, token?: string) => request<{ setCategoryFeatured: AdminCategory }>(`mutation SetCategoryFeatured($id: UUID!, $isFeatured: Boolean!) { setCategoryFeatured(id: $id, isFeatured: $isFeatured) { ${categoryFields} } }`, { id, isFeatured }, token),
	updateOrderStatus: (id: string, status: string, note?: string, token?: string) => request<{ updateOrderStatus: AdminOrder }>(`mutation UpdateOrderStatus($id: UUID!, $status: String!, $note: String) { updateOrderStatus(id: $id, status: $status, note: $note) { id status } }`, { id, status, note }, token),
	setCustomerStatus: (id: string, status: string, token?: string) => request<{ setCustomerStatus: AdminCustomer }>(`mutation SetCustomerStatus($id: UUID!, $status: String!) { setCustomerStatus(id: $id, status: $status) { id } }`, { id, status }, token),
	setCouponActive: (id: string, isActive: boolean, token?: string) => request<{ setCouponActive: AdminCoupon }>(`mutation SetCouponActive($id: UUID!, $isActive: Boolean!) { setCouponActive(id: $id, isActive: $isActive) { id } }`, { id, isActive }, token),
	moderateReview: (id: string, status: string, token?: string) => request<{ moderateReview: AdminReview }>(`mutation ModerateReview($id: UUID!, $status: String!) { moderateReview(id: $id, status: $status) { ${reviewFields} } }`, { id, status }, token),
	deleteReview: (id: string, token?: string) => request<{ deleteReview: MutationResult }>(`mutation DeleteReview($id: UUID!) { deleteReview(id: $id) { success message } }`, { id }, token),
};
