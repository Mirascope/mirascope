import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { setConfig } from "@/lib/agent";

export function SettingsBar() {
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState(false);
  const [url, setUrl] = useState(() =>
    typeof window !== "undefined"
      ? localStorage.getItem("admin:agentUrl") ?? "/api/agent"
      : "/api/agent",
  );
  const [token, setToken] = useState(() =>
    typeof window !== "undefined"
      ? localStorage.getItem("admin:agentToken") ?? ""
      : "",
  );

  function apply() {
    setConfig(url || "/api/agent", token || undefined);
    qc.invalidateQueries();
    setExpanded(false);
  }

  return (
    <div className="bg-gray-900/50 border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-6 py-2 flex items-center justify-between">
        <div className="flex items-center gap-3 text-sm text-gray-400">
          <span className="font-mono">{url}</span>
          {token && (
            <span className="text-xs bg-gray-800 px-2 py-0.5 rounded">🔑 token set</span>
          )}
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          {expanded ? "Close" : "Configure"}
        </button>
      </div>
      {expanded && (
        <div className="max-w-7xl mx-auto px-6 pb-3 flex gap-3 items-end">
          <div className="flex-1">
            <label className="text-xs text-gray-500 block mb-1">Agent URL</label>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="/api/agent or http://192.168.1.x:8787"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-gray-600"
            />
          </div>
          <div className="w-64">
            <label className="text-xs text-gray-500 block mb-1">Bearer Token</label>
            <input
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="optional"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 placeholder:text-gray-600 focus:outline-none focus:border-gray-600"
            />
          </div>
          <button onClick={apply} className="px-4 py-1.5 bg-sky-600 hover:bg-sky-500 text-white text-sm rounded-lg transition-colors">
            Apply
          </button>
        </div>
      )}
    </div>
  );
}
