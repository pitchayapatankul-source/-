#!/bin/bash
# TableChain Startup Script
echo "================================================="
echo "   TABLECHAIN - Fine Dining Table Booking Web3   "
echo "================================================="

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "1. Checking Python environment..."
python3 --version

echo "2. Initializing SQLite Database..."
python3 database.py

echo "3. Starting TableChain Server on http://localhost:3000..."
echo "Open http://localhost:3000 in your browser with MetaMask extension installed."
echo "Demo Mode enabled — No real cryptocurrency required."
python3 server.py
