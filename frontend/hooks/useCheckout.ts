import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { setSubmitting } from "../store/slices/checkoutSlice";

export function useCheckout() {
	const dispatch = useAppDispatch();
	const isSubmitting = useAppSelector((state) => state.checkout.isSubmitting);

	const submit = useCallback(async () => {
		dispatch(setSubmitting(true));
		await new Promise((resolve) => setTimeout(resolve, 1000));
		dispatch(setSubmitting(false));
	}, [dispatch]);

	return { isSubmitting, submit };
}
