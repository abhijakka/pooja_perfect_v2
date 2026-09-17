"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useChat } from "../../../hooks/useChat";

export default function ChatPage() {
  const { openChat } = useChat();
  useEffect(() => {
    openChat();
  }, [openChat]);
  return <main className="chat-page"><h1>Chat with PoojaPoint Support</h1><p>Our support team is ready to help with products, orders, payments and delivery.</p><Link href="/" className="primary-button">Continue Shopping</Link></main>;
}
