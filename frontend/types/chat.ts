export type ChatMessage = {
  id: string;
  conversationId: string;
  senderId: string | null;
  messageType: string;
  content: string;
  isRead: boolean;
  mine: boolean;
  createdAt: string | null;
};

export type ChatConversation = {
  id: string;
  subject: string | null;
  status: string;
  createdAt: string | null;
  updatedAt: string | null;
};

export type GuestProfile = { name: string; email: string };

export type UiChatMessage = {
  id: string;
  author: "admin" | "customer";
  text: string;
  time: string;
};

export type Page<T> = { items: T[]; pagination: Pagination };
export type Pagination = {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
};

export type AdminChatConversation = {
  id: string;
  customerId: string | null;
  customerName: string | null;
  customerEmail: string | null;
  status: string;
  lastMessage: string | null;
  unreadCount: number;
  createdAt: string;
  updatedAt: string;
};

export type AdminChatMessage = {
  id: string;
  conversationId: string;
  senderId: string | null;
  messageType: string;
  content: string;
  isRead: boolean;
  createdAt: string;
};