import * as yup from "yup";

export const email = yup.string().matches(/^[^\s@]+@[^\s@]+\.[^\s@]+$/, "Enter a valid email address");
export const phone = yup.string().matches(/^[6-9]\d{9}$/, "Enter a valid 10-digit mobile number");
export const password = yup.string().min(8, "Password must contain at least 8 characters");
export const name = yup.string().min(2, "Enter at least 2 characters");