"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">
            ⚡ FinPulse Analytics
          </h1>
          <p className="text-slate-400 mt-1">
            Autonomous Financial Outlier & Anomaly Detection Platform
          </p>
        </div>

        {/* Upload Container */}
        <div className="bg-slate-900/80 border border-sky-500/20 rounded-xl p-6 shadow-xl backdrop-blur-md">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Upload Excel File (.xlsx or .xlsb)
          </label>
          <input
            type="file"
            accept=".xlsx, .xlsb"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-sky-600 file:text-white hover:file:bg-sky-500 cursor-pointer"
          />
        </div>
      </div>
    </main>
  );
}
