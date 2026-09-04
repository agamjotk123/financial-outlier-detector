"use client";

import { useState } from "react";
import * as XLSX from "xlsx";

interface Anomaly {
  row: number;
  column: string;
  value: number;
  mean: string;
  zScore: string;
}

export default function Home() {
  const [data, setData] = useState<any[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [sensitivity, setSensitivity] = useState<number>(1.5);
  const [fileName, setFileName] = useState<string>("");

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    const reader = new FileReader();

    reader.onload = (evt) => {
      const bstr = evt.target?.result;
      const wb = XLSX.read(bstr, { type: "binary" });
      const wsname = wb.SheetNames[0];
      const ws = wb.Sheets[wsname];
      const parsedData = XLSX.utils.sheet_to_json<Record<string, any>>(ws);

      if (parsedData.length > 0) {
        setData(parsedData);
        setColumns(Object.keys(parsedData[0]));
        runAnomalyScan(parsedData, sensitivity);
      }
    };

    reader.readAsBinaryString(file);
  };

  const runAnomalyScan = (dataset: any[], threshold: number) => {
    if (!dataset.length) return;

    const detectedAnomalies: Anomaly[] = [];
    const keys = Object.keys(dataset[0]);

    keys.forEach((col) => {
      const values = dataset
        .map((row) => Number(row[col]))
        .filter((val) => !isNaN(val));

      if (values.length < 3) return;

      const mean = values.reduce((a, b) => a + b, 0) / values.length;
      const stdDev = Math.sqrt(
        values.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / values.length
      );

      if (stdDev === 0) return;

      dataset.forEach((row, idx) => {
        const val = Number(row[col]);
        if (!isNaN(val)) {
          const zScore = (val - mean) / stdDev;
          if (Math.abs(zScore) >= threshold) {
            detectedAnomalies.push({
              row: idx + 2,
              column: col,
              value: val,
              mean: mean.toFixed(2),
              zScore: zScore.toFixed(2),
            });
          }
        }
      });
    });

    setAnomalies(detectedAnomalies);
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <div className="max-w-5xl mx-auto space-y-6">
        <div>
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">
            ⚡ FinPulse Analytics
          </h1>
          <p className="text-slate-400 mt-1">
            Autonomous Financial Outlier & Anomaly Detection Platform
          </p>
        </div>

        <div className="bg-slate-900/80 border border-sky-500/20 rounded-xl p-6 shadow-xl backdrop-blur-md space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Upload Excel File (.xlsx or .xlsb)
            </label>
            <input
              type="file"
              accept=".xlsx, .xls, .xlsb"
              onChange={handleFileUpload}
              className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-sky-600 file:text-white hover:file:bg-sky-500 cursor-pointer"
            />
          </div>

          {data.length > 0 && (
            <div className="pt-4 border-t border-slate-800 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Sensitivity Threshold (Z-Score): {sensitivity}
                </label>
                <input
                  type="range"
                  min="1.0"
                  max="3.0"
                  step="0.1"
                  value={sensitivity}
                  onChange={(e) => {
                    const val = parseFloat(e.target.value);
                    setSensitivity(val);
                    runAnomalyScan(data, val);
                  }}
                  className="w-full accent-sky-500 cursor-pointer"
                />
              </div>

              <div className="grid grid-cols-3 gap-4 pt-2">
                <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                  <p className="text-xs text-slate-400">Total Rows</p>
                  <p className="text-2xl font-bold text-sky-400">{data.length}</p>
                </div>
                <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                  <p className="text-xs text-slate-400">Columns Scanned</p>
                  <p className="text-2xl font-bold text-sky-400">{columns.length}</p>
                </div>
                <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                  <p className="text-xs text-slate-400">Anomalies Detected</p>
                  <p className="text-2xl font-bold text-indigo-400">{anomalies.length}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {anomalies.length > 0 && (
          <div className="bg-slate-900/80 border border-sky-500/20 rounded-xl p-6 shadow-xl backdrop-blur-md">
            <h2 className="text-xl font-semibold text-sky-400 mb-4">
              📊 Detected Anomalies
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-800/80 text-slate-400 uppercase text-xs">
                  <tr>
                    <th className="px-4 py-3">Excel Row</th>
                    <th className="px-4 py-3">KPI Column</th>
                    <th className="px-4 py-3">Flagged Value</th>
                    <th className="px-4 py-3">Mean</th>
                    <th className="px-4 py-3">Z-Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {anomalies.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40">
                      <td className="px-4 py-3 font-mono">{item.row}</td>
                      <td className="px-4 py-3 text-sky-300">{item.column}</td>
                      <td className="px-4 py-3 font-semibold text-indigo-300">
                        {item.value}
                      </td>
                      <td className="px-4 py-3">{item.mean}</td>
                      <td className="px-4 py-3 font-mono text-amber-400">
                        {item.zScore}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}