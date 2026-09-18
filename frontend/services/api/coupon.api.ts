import { graphqlClient } from "./client";

export type CouponDiscount = {
	code: string;
	name?: string | null;
	couponType: string;
	value: number;
	minimumOrderAmount?: number | null;
	maximumDiscount?: number | null;
	discount: number;
};

const couponFields = `code name couponType value minimumOrderAmount maximumDiscount discount`;

export const couponApi = {
	apply: (code: string, subtotal: number) =>
		graphqlClient<{ applyCoupon: CouponDiscount | null }>(
			`query ApplyCoupon($code: String!, $subtotal: Decimal!) {
				applyCoupon(code: $code, subtotal: $subtotal) { ${couponFields} }
			}`,
			{ code, subtotal },
		),
};