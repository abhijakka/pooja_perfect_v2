import { useChat as useChatContext } from "../context/ChatContext";

export function useChat() {
	return useChatContext();
}