import { create } from "zustand";

interface TerminalState {
  selectedSymbol: string;
  setSelectedSymbol: (symbol: string) => void;
  isCommandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;
  toggleCommandPalette: () => void;
  liveQuotes: Record<string, any>;
  setLiveQuote: (symbol: string, quote: any) => void;
  executionMode: "PAPER" | "LIVE";
  setExecutionMode: (mode: "PAPER" | "LIVE") => void;
}

export const useTerminalStore = create<TerminalState>((set) => ({
  selectedSymbol: "AAPL",
  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol.toUpperCase() }),
  isCommandPaletteOpen: false,
  setCommandPaletteOpen: (open) => set({ isCommandPaletteOpen: open }),
  toggleCommandPalette: () => set((state) => ({ isCommandPaletteOpen: !state.isCommandPaletteOpen })),
  liveQuotes: {},
  setLiveQuote: (symbol, quote) =>
    set((state) => ({
      liveQuotes: { ...state.liveQuotes, [symbol]: quote },
    })),
  executionMode: "PAPER",
  setExecutionMode: (mode) => set({ executionMode: mode }),
}));
