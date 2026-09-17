export type Customer = {
  id: string;
  name: string;
  email: string;
  role_name?: "customer" | "admin";
};
