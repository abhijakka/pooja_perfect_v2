import { AdminOrderDetailPage } from "../../components/AdminOrderDetailPage";

type OrderDetailRouteProps = { params: Promise<{ orderId: string }> };

export default async function OrderDetailRoute({ params }: OrderDetailRouteProps) {
	const { orderId } = await params;
	return <AdminOrderDetailPage orderId={orderId} />;
}
