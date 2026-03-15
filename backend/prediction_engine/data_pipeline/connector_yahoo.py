# Yahoo Finance connector
"""Yahoo Finance data connector using yfinance.

Provides OHLCV data for NSE tickers by appending the `.NS` suffix
expected by Yahoo Finance.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

try:
    import yfinance as yf
except ImportError:
    yf = None
    logger.warning("yfinance not installed – YahooConnector will not work")


class YahooConnector:
    """Fetches OHLCV data from Yahoo Finance."""

    REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]
    MIN_ROWS = 50  # Minimum number of rows expected

    def __init__(self, nse_suffix: str = ".NS") -> None:
        self._suffix = nse_suffix

    def _yahoo_ticker(self, ticker: str) -> str:
        """Append exchange suffix if not already present."""
        if not ticker.endswith(self._suffix):
            return f"{ticker}{self._suffix}"
        return ticker

    def fetch(
        self,
        ticker: str,
        start: str | datetime,
        end: str | datetime,
    ) -> pd.DataFrame:
        """Download OHLCV data for a single ticker.

        Returns empty DataFrame if no valid data is found.
        """
        if yf is None:
            raise RuntimeError("yfinance is not installed")

        yahoo_sym = self._yahoo_ticker(ticker)
        logger.info("Fetching %s (%s) from %s to %s", ticker, yahoo_sym, start, end)

        # Convert datetime to YYYY-MM-DD strings
        if isinstance(start, datetime):
            start = start.strftime("%Y-%m-%d")
        if isinstance(end, datetime):
            end = end.strftime("%Y-%m-%d")

        try:
            df = yf.download(
                yahoo_sym,
                start=start,
                end=end,
                progress=False,
                auto_adjust=True,  # avoid future warning
            )
        except Exception as e:
            logger.warning("Failed to download %s: %s", ticker, e)
            return pd.DataFrame(columns=["Date"] + self.REQUIRED_COLUMNS)

        if df.empty:
            logger.warning("No data returned for %s", ticker)
            return pd.DataFrame(columns=["Date"] + self.REQUIRED_COLUMNS)

        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Ensure required columns exist
        missing_cols = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
        if missing_cols:
            logger.warning("Missing columns %s for %s", missing_cols, ticker)
            return pd.DataFrame(columns=["Date"] + self.REQUIRED_COLUMNS)

        df = df.reset_index()
        df = df.rename(columns={"index": "Date"} if "Date" not in df.columns else {})

        # Filter only required columns
        df = df[["Date"] + self.REQUIRED_COLUMNS]

        # Validate numeric columns
        for col in self.REQUIRED_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Drop rows with NaN values
        df = df.dropna()

        # Check minimum rows
        if len(df) < self.MIN_ROWS:
            logger.warning(
                "Not enough valid data for %s (%d rows, expected >= %d)",
                ticker,
                len(df),
                self.MIN_ROWS,
            )
            return pd.DataFrame(columns=["Date"] + self.REQUIRED_COLUMNS)

        return df

    def fetch_to_csv(
        self,
        ticker: str,
        start: str | datetime,
        end: str | datetime,
        output_dir: str | Path,
    ) -> Path | None:
        """Fetch data and persist as CSV.

        Returns the path of the written file, or None if no valid data.
        """
        df = self.fetch(ticker, start, end)
        if df.empty:
            logger.warning("Skipping CSV for %s due to insufficient data", ticker)
            return None

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{ticker}.csv"
        df.to_csv(path, index=False)
        logger.info("Saved %d rows → %s", len(df), path)
        return path