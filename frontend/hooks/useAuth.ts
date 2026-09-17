import { useAppSelector } from "../store/hooks";

export function useAuth() {
	const { user, isAuthenticated, isReady } = useAppSelector((state) => state.auth);
	return { user, isAuthenticated, isReady };
}
