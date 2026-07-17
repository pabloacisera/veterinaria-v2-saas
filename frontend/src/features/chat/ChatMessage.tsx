import type { ChatMessage as ChatMessageType } from "@/entities/chat/types";

interface ChatMessageProps {
  message: ChatMessageType;
  isStreaming?: boolean;
}

function renderMarkdown(text: string): string {
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  html = html
    .replace(/### (.+)/g, "<h3 class='text-base font-bold mt-3 mb-1'>$1</h3>")
    .replace(/## (.+)/g, "<h2 class='text-lg font-bold mt-4 mb-2'>$1</h2>")
    .replace(/# (.+)/g, "<h1 class='text-xl font-bold mt-4 mb-2'>$1</h1>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code class='bg-gray-100 px-1 py-0.5 rounded text-sm font-mono'>$1</code>")
    .replace(/^- (.+)/gm, "<li class='ml-4 list-disc'>$1</li>")
    .replace(/\n{2,}/g, "</p><p class='mb-2'>")
    .replace(/\n/g, "<br/>");

  return `<p class='mb-2'>${html}</p>`;
}

export function ChatMessage({ message, isStreaming }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-primary-600 text-white rounded-br-md"
            : "bg-gray-100 text-gray-900 rounded-bl-md"
        }`}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div
            className="text-sm prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{
              __html: renderMarkdown(message.content),
            }}
          />
        )}
        {isStreaming && (
          <span className="inline-block w-2 h-4 bg-gray-500 animate-pulse ml-1" />
        )}
      </div>
    </div>
  );
}
