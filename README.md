# 🍽️ TableChain — Modern Restaurant Table Booking with MetaMask

**Reserve Your Table. Secure Your Booking On-Chain.**

TableChain is a fine-dining restaurant reservation platform that merges traditional hospitality table management with cryptocurrency booking fee escrow via **MetaMask** on the **Ethereum Sepolia Testnet**.

---

## 🌟 Key Features

1. **Restaurant Discovery & Exploration**:
   - Live search by restaurant name, cuisine, and location.
   - Filter chips by cuisine (Steakhouse & Grill, Thai Contemporary, Japanese Kaiseki & Sushi, French Contemporary), price, and ratings.
   - Real-time display of average price per person, booking fees in ETH & THB, and available seating time slots.

2. **Curated Fine-Dining Showcase**:
   - **Maison Grill** (Steakhouse, Chiang Mai Old City, 4.8 ⭐, 800 THB/person, 0.002 ETH fee)
   - **Nara Dining** (Thai Contemporary, Nimman, 4.7 ⭐, 600 THB/person, 0.0015 ETH fee)
   - **Sakura House** (Japanese Kaiseki & Sushi, Riverside, 4.9 ⭐, 1,000 THB/person, 0.0025 ETH fee)
   - **L'Atelier Gourmet** (French Contemporary, Wat Ket, 4.8 ⭐, 1,200 THB/person, 0.003 ETH fee)

3. **Interactive Restaurant Detail & Sticky Booking Panel**:
   - High-definition photo galleries, descriptions, facilities tags, and signature menu previews with prices.
   - Transparent booking fee policies and 4-hour cancellation refund policy.
   - Dynamic booking panel: date picker, guest count (1–8+), time slots (`17:00`, `17:30`, `18:00`, `18:30`, `19:00`, `19:30`, `20:00`), table preference, and live fee calculator.

4. **MetaMask Wallet Integration**:
   - Detects `window.ethereum` and requests account connection.
   - Shortened wallet address display (`0x71C4...A89F`).
   - Network validation for **Ethereum Sepolia Testnet** (Chain ID: `11155111` / `0xaa36a7`) with automated network switching.
   - Graceful fallback: If MetaMask is not installed or test ETH is unavailable, an interactive **Demo Wallet Simulator** allows full end-to-end evaluation without spending any cryptocurrency.

5. **Multi-Step Blockchain Payment Flow**:
   - Displays clear Reservation Summary and Blockchain Payment specifications before triggering the wallet.
   - Realistic transaction loading state progression:
     1. `Connecting Wallet...`
     2. `Waiting for MetaMask Confirmation...`
     3. `Processing Blockchain Payment...`
     4. `Confirming Transaction on Sepolia...`
     5. `Booking Confirmed!`
   - Captures on-chain transaction hash, updates booking status to **Confirmed**, and records the record in the database.

6. **Booking Confirmation & Check-In**:
   - Unique alphanumeric booking ID (e.g. `TC-20261010-00125`).
   - Direct clickable link to **Sepolia Etherscan** (`https://sepolia.etherscan.io/tx/...`).
   - Built-in dynamic **Arrival QR Code Pass** for host stand verification.

7. **Customer Dashboard ("My Reservations")**:
   - Segmented tabs: **Upcoming**, **Completed**, **Cancelled**.
   - View details, transaction hashes, and smart contract cancellation/refund option.

8. **Restaurant Admin Dashboard**:
   - Real-time KPIs: Today's Bookings, Confirmed Bookings, Pending Payments, Total Revenue (ETH & THB), Available Tables.
   - Reservation management table with admin actions: **Confirm Arrival**, **Mark Completed**, **Cancel Reservation**, **Mark No-show**, **View Blockchain Tx**.
   - **Table Management**: Table Number, Capacity, Status (`Available`, `Reserved`, `Occupied`, `Cleaning`, `Unavailable`) with **double-booking prevention logic**.

9. **Solidity Smart Contract (`contracts/TableChainBooking.sol`)**:
   - Solidity `^0.8.20` escrow and payment contract.
   - Function: `payBookingFee(string bookingId, address payable restaurantWallet)`
   - Emits event: `BookingPaid(string bookingId, address indexed customerWallet, address indexed restaurantWallet, uint256 amount, uint256 timestamp)`
   - Built-in live On-Chain Event Feed explorer view in the application.

---

## 🎨 Luxury Fine-Dining Design System

- **Palette**: Dark Obsidian (`#0D0D0F`, `#151518`), Warm Cream (`#F8F5EE`, `#ECE7DC`), Subtle Gold & Champagne accents (`#C5A880`, `#E5C378`, `#8F764D`).
- **Typography**: Editorial serif headings (*Cormorant Garamond*, *Cinzel*) paired with clean modern sans-serif body (*Plus Jakarta Sans*).
- **Aesthetic**: Premium Michelin / OpenTable / Resy hospitality style with non-intrusive Web3 payment integration.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Tailwind CSS (Modern CDN), Lucide Icons, Ethers.js v6, QRCode.js, Canvas-Confetti.
- **Backend**: Python 3 standard library (`http.server`, `sqlite3`, `json`, `urllib`). No third-party pip dependencies required.
- **Database**: SQLite (`tablechain.db`) with tables: `users`, `restaurants`, `tables`, `reservations`.
- **Blockchain**: Solidity `^0.8.20`, MetaMask (`window.ethereum`), Ethereum Sepolia Testnet.

---

## 🚀 Quick Start Guide

### 1. Launch the Server

Run the startup script:

```bash
cd /Users/pitchayapa/Downloads/tablechain
./start.sh
```

Or run directly with Python:

```bash
python3 server.py
```

### 2. Open in Your Browser

Open your browser (e.g. Chrome or Brave with MetaMask installed):

👉 **http://localhost:3000**

*(You can also open `public/index.html` directly in your browser — TableChain includes an integrated client-side data persistence engine).*

---

## 🧪 Demonstration & Presentation Steps

1. **Landing Page**: View the hero section, stats, and the 4-step "How It Works" workflow.
2. **Connect MetaMask**: Click **Connect MetaMask** in the navbar to connect your wallet on Sepolia. (Or click **Use Demo Wallet** if presenting without MetaMask).
3. **Browse & Select**: Go to **Restaurants**, filter by "Steakhouse" or "Japanese", and select **Maison Grill**.
4. **Choose Reservation**: Pick date, guests (e.g. 4 Guests), time (`19:00`), enter diner name, and click **Continue to Payment**.
5. **Pay with MetaMask**: Click **Pay Booking Fee with MetaMask**. Watch the interactive multi-step blockchain confirmation.
6. **Confirmation Page**: View the unique Booking Reference (`TC-YYYYMMDD-XXXXX`), payment status ("Blockchain Payment Confirmed"), Sepolia transaction hash, and the scannable arrival QR pass.
7. **Customer Dashboard**: Click **My Reservations** to inspect upcoming bookings.
8. **Admin Portal**: Click **Admin** in the navbar to see live KPI statistics, change reservation statuses to "Completed", or toggle table statuses in the **Table Management** section.
9. **Smart Contract**: Click **Contract** to inspect the Solidity contract and the real-time `BookingPaid` event log.
