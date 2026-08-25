import { ChatMessage } from "@/lib/types";
import RetrievalTypeTag from "./RetrievalTypeTag";
import SourceList from "./SourceList";

export default function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
          isUser
            ? "rounded-br-sm bg-brand-600 text-white"
            : "rounded-bl-sm bg-white text-slate-800 ring-1 ring-slate-200"
        }`}
      >
        {message.pending ? (
          <span className="inline-flex items-center gap-1 text-slate-400">
            <Dot delay="0ms" />
            <Dot delay="150ms" />
            <Dot delay="300ms" />
          </span>
        ) : (
          <>
            {!isUser && message.retrievalType && (
              <div className="mb-1.5">
                <RetrievalTypeTag type={message.retrievalType} />
              </div>
            )}
            <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
            {!isUser && message.sources && <SourceList sources={message.sources} />}
          </>
        )}
      </div>
    </div>
  );
}

function Dot({ delay }: { delay: string }) {
  return (
    <span
      className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400"
      style={{ animationDelay: delay }}
    />
  );
}
