import { useState } from "react";
import { queryLLM } from "../services/api";

function ChatPanel() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: "human", message: input };
        setMessages(prev => [...prev, userMessage]);

        setInput("");
        try {
            const response = await queryLLM(input, messages);
            const llm_message = response.llm_response

            const llm_message_formatted = { role: "ai", message: llm_message };
            setMessages(prev => [...prev, llm_message_formatted]);

        } catch (error) {
            const errorMessage = { role: "ai", message: "Sorry, I am having trouble connecting. Please try again later." };
            setMessages(prev => [...prev, errorMessage]);
            console.error("Error sending message:", error);
        }
    }

    return (
        <div className="fixed bottom-4 right-4 z-50">
            {/* Chat panel (pops up above the button) */}
            {isOpen && (
                <div className="mb-3 w-80 max-w-[calc(100vw-2rem)] rounded-xl border border-gray-200 bg-white shadow-lg">
                    <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
                        <div className="text-sm font-medium text-gray-900">
                            BirdCall AI Chat
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="rounded-md px-2 py-1 text-xs text-gray-600 transition hover:bg-gray-100"
                        >
                            Close
                        </button>
                    </div>

                    <div className="max-h-80 overflow-y-auto px-4 py-3">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className="mb-2 rounded-md bg-gray-50 px-3 py-2 text-sm text-gray-800 ${msg.role}"
                            >
                                {msg.message}
                            </div>
                        ))}
                    </div>

                    <form
                        className="flex items-center gap-2 border-t border-gray-200 px-4 py-3"
                        onSubmit={handleSendMessage}
                    >
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your question"
                            className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        />
                        <button
                            type="submit"
                            className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-indigo-700"
                        >
                            Send
                        </button>
                    </form>
                </div>
            )}

            {/* Floating chat button */}
            <button
                onClick={() => setIsOpen(true)}
                className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-600 text-xs font-medium text-white shadow-md transition hover:bg-indigo-700"
                title="Open chat"
            >
                Chat
            </button>
        </div>
    );
}

export default ChatPanel;