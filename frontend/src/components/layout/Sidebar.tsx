import {
    PanelLeftClose,
    PanelLeftOpen,
    Plus,
    Search,
    MessageSquare,
    FileText,
} from "lucide-react";

interface SidebarProps {
    isOpen: boolean;
    onToggle: () => void;
    onNewChat: () => void;
}

export function Sidebar({
    isOpen,
    onToggle,
    onNewChat,
}: SidebarProps) {
    return (
        <aside
            className={`
                relative h-screen shrink-0 overflow-hidden
                border-r border-border-light dark:border-border-dark
                bg-canvas-light dark:bg-canvas-dark
                transition-[width,background-color,border-color]
                duration-300
                ease-in-out
                ${isOpen ? "w-[260px]" : "w-[56px]"}
            `}
        >
            {/* SIDEBAR CONTENT */}
            <div
                className={`
                    h-full w-[260px]
                    transition-opacity
                    duration-200
                    ${isOpen ? "opacity-100" : "opacity-0"}
                `}
            >
                {/* HEADER */}
                <div className="flex h-[64px] items-center justify-between px-4">
                    <div className="flex items-center gap-2.5">
                        <div className="h-7 w-7 shrink-0 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-400" />

                        <span className="text-sm font-semibold text-ink-light dark:text-ink-dark">
                            Multimodal{" "}
                            <span className="text-blue-500">
                                RAG
                            </span>
                        </span>
                    </div>

                    <button
                        onClick={onToggle}
                        className="
                            rounded-lg p-1.5
                            text-gray-500
                            transition-colors duration-200
                            hover:bg-gray-100
                            hover:text-gray-800
                            dark:text-gray-400
                            dark:hover:bg-[#1b1f28]
                            dark:hover:text-white
                        "
                        aria-label="Close sidebar"
                    >
                        <PanelLeftClose size={18} />
                    </button>
                </div>

                {/* NEW CHAT */}
                <div className="px-3 pt-2">
                    <button
                        onClick={onNewChat}
                        className="
                            flex h-10 w-full items-center gap-3
                            rounded-lg
                            border border-border-light
                            bg-transparent
                            px-3
                            text-sm font-medium
                            text-ink-light
                            transition-colors duration-200
                            hover:bg-gray-100
                            dark:border-border-dark
                            dark:text-ink-dark
                            dark:hover:bg-[#1a1e27]
                        "
                    >
                        <Plus size={18} />

                        <span>
                            New chat
                        </span>
                    </button>
                </div>

                {/* SEARCH */}
                <div className="px-3 pt-4">
                    <div
                        className="
                            flex h-10 items-center gap-2
                            rounded-lg
                            border border-border-light
                            px-3
                            transition-colors
                            dark:border-border-dark
                        "
                    >
                        <Search
                            size={17}
                            className="
                                shrink-0
                                text-gray-500
                                dark:text-gray-400
                            "
                        />

                        <input
                            type="text"
                            placeholder="Search chats..."
                            className="
                                w-full
                                bg-transparent
                                text-sm
                                text-ink-light
                                outline-none
                                placeholder:text-gray-500
                                dark:text-ink-dark
                            "
                        />
                    </div>
                </div>

                {/* RECENT CHATS */}
                <div className="px-3 pt-6">
                    <p
                        className="
                            mb-2 px-2
                            text-xs font-medium
                            text-gray-500
                            dark:text-gray-400
                        "
                    >
                        Recent chats
                    </p>

                    <div className="space-y-1">
                        <button
                            className="
                                flex h-9 w-full items-center gap-2
                                rounded-lg px-2
                                text-left text-sm
                                text-ink-light
                                transition-colors duration-150
                                hover:bg-gray-100
                                hover:text-blue-500
                                dark:text-ink-dark
                                dark:hover:bg-[#1a1e27]
                            "
                        >
                            <MessageSquare
                                size={16}
                                className="shrink-0"
                            />

                            <span className="truncate">
                                Meaning of preparation
                            </span>
                        </button>

                        <button
                            className="
                                flex h-9 w-full items-center gap-2
                                rounded-lg px-2
                                text-left text-sm
                                text-ink-light
                                transition-colors duration-150
                                hover:bg-gray-100
                                hover:text-blue-500
                                dark:text-ink-dark
                                dark:hover:bg-[#1a1e27]
                            "
                        >
                            <MessageSquare
                                size={16}
                                className="shrink-0"
                            />

                            <span className="truncate">
                                Best phones in India
                            </span>
                        </button>
                    </div>
                </div>

                {/* FILES */}
                <div className="px-3 pt-6">
                    <p
                        className="
                            mb-2 px-2
                            text-xs font-medium
                            text-gray-500
                            dark:text-gray-400
                        "
                    >
                        Files
                    </p>

                    <button
                        className="
                            flex h-9 w-full items-center gap-2
                            rounded-lg px-2
                            text-left text-sm
                            text-ink-light
                            transition-colors duration-150
                            hover:bg-gray-100
                            hover:text-blue-500
                            dark:text-ink-dark
                            dark:hover:bg-[#1a1e27]
                        "
                    >
                        <FileText
                            size={16}
                            className="shrink-0"
                        />

                        <span className="truncate">
                            architecture.pdf
                        </span>
                    </button>
                </div>
            </div>

            {/* COLLAPSED BUTTON */}
            {!isOpen && (
                <button
                    onClick={onToggle}
                    aria-label="Open sidebar"
                    className="
                        absolute left-1/2 top-4
                        -translate-x-1/2
                        rounded-lg
                        border border-border-light
                        bg-gray-50
                        p-1.5
                        text-gray-500
                        transition-colors duration-200
                        hover:bg-gray-100
                        hover:text-gray-800
                        dark:border-border-dark
                        dark:bg-[#151922]
                        dark:text-gray-400
                        dark:hover:bg-[#1c212c]
                        dark:hover:text-white
                    "
                >
                    <PanelLeftOpen size={18} />
                </button>
            )}
        </aside>
    );
}