import { useAppSelector } from "../store/hooks";

export function useSubscription() {
	const subscriptions = useAppSelector((state) => state.subscription.subscriptions);
	return { subscriptions };
}
