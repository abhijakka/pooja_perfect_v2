import { graphqlClient } from "./client";
import type {
  ChatConversation,
  ChatMessage,
  Page,
} from "../../types/chat";

const conversationFields = `id subject status createdAt updatedAt`;
const messageFields = `id conversationId senderId messageType content isRead mine createdAt`;

export const chatApi = {
	startConversation(
		name?: string,
		email?: string,
		forceNew = false,
	): Promise<{ startConversation: ChatConversation }> {
		return graphqlClient<{ startConversation: ChatConversation }>(
			`mutation StartConversation($name: String, $email: String, $forceNew: Boolean) {
				startConversation(name: $name, email: $email, forceNew: $forceNew) {
					${conversationFields}
				}
			}`,
			{ name: name ?? null, email: email ?? null, forceNew },
		);
	},

	endConversation(
		conversationId: string,
	): Promise<{ endConversation: ChatConversation }> {
		return graphqlClient<{ endConversation: ChatConversation }>(
			`mutation EndConversation($conversationId: UUID!) {
				endConversation(conversationId: $conversationId) {
					${conversationFields}
				}
			}`,
			{ conversationId },
		);
	},

	activeConversation(): Promise<{ activeConversation: ChatConversation | null }> {
		return graphqlClient<{ activeConversation: ChatConversation | null }>(
			`query ActiveConversation {
				activeConversation {
					${conversationFields}
				}
			}`,
		);
	},

	conversation(
		conversationId: string,
	): Promise<{ conversation: ChatConversation | null }> {
		return graphqlClient<{ conversation: ChatConversation | null }>(
			`query Conversation($id: UUID!) {
				conversation(id: $id) {
					${conversationFields}
				}
			}`,
			{ id: conversationId },
		);
	},

	messages(
		conversationId: string,
		page = 1,
		pageSize = 50,
	): Promise<{ messages: Page<ChatMessage> }> {
		return graphqlClient<{ messages: Page<ChatMessage> }>(
			`query Messages($conversationId: UUID!, $page: Int!, $pageSize: Int!) {
				messages(conversationId: $conversationId, page: $page, pageSize: $pageSize) {
					items { ${messageFields} }
					pagination { page pageSize total totalPages hasNext hasPrevious }
				}
			}`,
			{ conversationId, page, pageSize },
		);
	},

	sendMessage(
		conversationId: string,
		content: string,
	): Promise<{ sendChatMessage: ChatMessage }> {
		return graphqlClient<{ sendChatMessage: ChatMessage }>(
			`mutation SendChatMessage($conversationId: UUID!, $content: String!) {
				sendChatMessage(conversationId: $conversationId, content: $content) {
					${messageFields}
				}
			}`,
			{ conversationId, content },
		);
	},
};