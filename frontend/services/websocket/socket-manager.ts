import {
	subscribeToChat,
	subscribeToAdminChat,
	disposeChatSocket,
	disposeAdminChatSocket,
} from "./chat.socket";
import type { Cleanup } from "./chat.types";

export class SocketManager {
	disconnect(): void {
		disposeChatSocket();
		disposeAdminChatSocket();
	}
}

export { subscribeToChat, subscribeToAdminChat, disposeChatSocket, disposeAdminChatSocket };
export type { Cleanup };