
import { useEffect, useState } from "react";
import {
  Wallet,
  Banknote,
  Receipt,
  Headset,
  ShieldCheck,
  RefreshCw,
  ArrowUpRight,
  ArrowDownLeft,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8000";
const ACCOUNT = "100001";

function App() {
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const [loading, setLoading] = useState(false);

  // Format currency in Indian Rupees
  const formatMoney = (value) =>
    Number(value ?? 0).toLocaleString("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    });

  // Display application messages
  const showMessage = (text, type = "error") => {
    setMessage(text);
    setMessageType(type);
  };

  // Fetch account balance
  const fetchAccount = async () => {
    try {
      const response = await fetch(`${API}/api/account/${ACCOUNT}`);

      if (!response.ok) {
        throw new Error("Account request failed");
      }

      const data = await response.json();

      if (data.balance === undefined || data.balance === null) {
        throw new Error("Balance field missing from API response");
      }

      setBalance(data.balance);
    } catch (error) {
      console.error("Account error:", error);
      showMessage("Cannot load account balance. Check the backend.");
    }
  };

  // Fetch transaction history
  const fetchTransactions = async () => {
    try {
      const response = await fetch(
        `${API}/api/account/${ACCOUNT}/transactions`
      );

      if (!response.ok) {
        throw new Error("Transaction request failed");
      }

      const data = await response.json();

      const records = Array.isArray(data)
        ? data
        : Array.isArray(data.transactions)
          ? data.transactions
          : [];

      setTransactions(records);
    } catch (error) {
      console.error("Transaction error:", error);
      setTransactions([]);
    }
  };

  // Load account information when application starts
  useEffect(() => {
    fetchAccount();
    fetchTransactions();
  }, []);

  // Withdraw cash
  const withdrawCash = async () => {
    const value = Number(amount);

    if (!amount.trim() || !Number.isFinite(value) || value <= 0) {
      showMessage("Please enter a valid withdrawal amount.");
      return;
    }

    setLoading(true);
    setMessage("");
    setMessageType("");

    try {
      const response = await fetch(`${API}/api/withdraw`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          account_number: ACCOUNT,
          amount: value,
        }),
      });

      const responseText = await response.text();

      let data = {};

      try {
        data = responseText ? JSON.parse(responseText) : {};
      } catch {
        data = {
          detail: responseText || "Unexpected server response.",
        };
      }

      if (!response.ok) {
        let errorMessage = "Withdrawal failed.";

        if (typeof data.detail === "string") {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          errorMessage = data.detail
            .map((error) => error.msg || "Invalid input")
            .join(", ");
        } else if (typeof data.message === "string") {
          errorMessage = data.message;
        }

        showMessage(errorMessage, "error");
        return;
      }

      showMessage(
        `Withdrawal successful! ${
          data.remaining_balance !== undefined
            ? `Remaining balance: ${formatMoney(data.remaining_balance)}`
            : "Your account has been updated."
        }`,
        "success"
      );

      setAmount("");

      await fetchAccount();
      await fetchTransactions();
    } catch (error) {
      console.error("Withdrawal error:", error);

      showMessage(
        "Unable to connect to ATM server. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  // Refresh account balance
  const handleRefreshBalance = async () => {
    try {
      const response = await fetch(`${API}/api/account/${ACCOUNT}`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Unable to fetch balance");
      }

      const data = await response.json();
      setBalance(data.balance);

      showMessage(
        `Your current balance is ${formatMoney(data.balance)}`,
        "success"
      );
    } catch (error) {
      console.error("Balance refresh error:", error);
      showMessage(
        error.message || "Unable to refresh balance.",
        "error"
      );
    }
  };

  // Refresh transaction history
  const handleRefreshTransactions = async () => {
    try {
      const response = await fetch(
        `${API}/api/account/${ACCOUNT}/transactions`
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Unable to fetch transactions");
      }

      const data = await response.json();

      const records = Array.isArray(data)
        ? data
        : Array.isArray(data.transactions)
          ? data.transactions
          : [];

      setTransactions(records);

      showMessage(
        `Transaction history refreshed. ${records.length} transaction(s) found.`,
        "success"
      );
    } catch (error) {
      console.error("Transaction refresh error:", error);
      showMessage(
        error.message || "Unable to refresh transactions.",
        "error"
      );
    }
  };

  return (
    <div className="app">

      {/* Navigation Bar */}
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">
            <Wallet />
          </div>

          <div>
            <h2>NEXT-GEN ATM</h2>
            <p>INTELLIGENT BANKING ECOSYSTEM</p>
          </div>
        </div>

        <div className="secure">
          <ShieldCheck size={17} />
          Secure Demo Environment
        </div>
      </header>

      <main className="container">

        {/* Welcome Section */}
        <section className="welcome">
          <div>
            <p className="eyebrow">CUSTOMER DASHBOARD</p>
            <h1>Welcome back, Demo Customer!</h1>
            <p>Manage your banking activities from one place.</p>
          </div>

          <div className="account-tag">
            Account: {ACCOUNT}
          </div>
        </section>

        {/* Account Balance */}
        <section className="balance-card">
          <div>
            <p>AVAILABLE ACCOUNT BALANCE</p>

            <h1>
              {balance === null
                ? "Loading..."
                : formatMoney(balance)}
            </h1>

            <span>Indian Rupee · INR</span>
          </div>

          <div className="balance-icon">
            <Wallet size={34} />
          </div>
        </section>

        {/* ATM Services */}
        <section className="section">
          <h2>ATM Services</h2>

          <p className="section-subtitle">
            Choose a banking service to continue.
          </p>

          <div className="services">

            {/* Cash Withdrawal */}
            <div className="service-card">
              <div className="service-icon blue">
                <Banknote />
              </div>

              <h3>Cash Withdrawal</h3>

              <p>Withdraw money from your demo account.</p>

              <input
                type="number"
                min="1"
                placeholder="Enter amount in ₹"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />

              <div className="quick-amounts">
                {[500, 1000, 2000, 5000].map((value) => (
                  <button
                    type="button"
                    key={value}
                    onClick={() => setAmount(String(value))}
                  >
                    ₹{value}
                  </button>
                ))}
              </div>

              <button
                className="primary-button"
                type="button"
                onClick={withdrawCash}
                disabled={loading}
              >
                {loading ? "Processing..." : "Withdraw Cash"}
                <ArrowUpRight size={17} />
              </button>

              {/* Withdrawal feedback */}
              {message && (
                <div
                  className={`message ${
                    messageType === "success"
                      ? "message-success"
                      : "message-error"
                  }`}
                  role="alert"
                >
                  {messageType === "success" ? (
                    <CheckCircle size={18} />
                  ) : (
                    <AlertCircle size={18} />
                  )}

                  <span>{message}</span>
                </div>
              )}
            </div>

            {/* Check Balance */}
            <div className="service-card">
              <div className="service-icon green">
                <Wallet />
              </div>

              <h3>Check Balance</h3>

              <p>View your latest available account balance.</p>

              <button
                className="secondary-button"
                type="button"
                onClick={handleRefreshBalance}
              >
                Refresh Balance
                <RefreshCw size={16} />
              </button>
            </div>

            {/* Transaction History */}
            <div className="service-card">
              <div className="service-icon purple">
                <Receipt />
              </div>

              <h3>Transaction History</h3>

              <p>Review your recent ATM transactions.</p>

              <button
                className="secondary-button"
                type="button"
                onClick={handleRefreshTransactions}
              >
                Refresh History
                <RefreshCw size={16} />
              </button>
            </div>

            {/* AI Customer Support */}
            <div className="service-card">
              <div className="service-icon orange">
                <Headset />
              </div>

              <h3>AI Customer Support</h3>

              <p>Get assistance with ATM errors and complaints.</p>

              <a
                className="secondary-button support-link"
                href="#support"
              >
                Get Support
                <ArrowUpRight size={16} />
              </a>
            </div>

          </div>
        </section>

        {/* Recent Transactions */}
        <section className="section">
          <div className="section-heading">
            <div>
              <h2>Recent Transactions</h2>

              <p className="section-subtitle">
                Your account activity
              </p>
            </div>

            <button
              className="text-button"
              type="button"
              onClick={handleRefreshTransactions}
            >
              Refresh
            </button>
          </div>

          <div className="transaction-list">
            {transactions.length === 0 ? (
              <p className="empty">
                No transactions available yet.
              </p>
            ) : (
              transactions.map((item, index) => (
                <div
                  className="transaction"
                  key={item.id ?? index}
                >
                  <div className="transaction-icon">
                    <ArrowDownLeft />
                  </div>

                  <div className="transaction-info">
                    <strong>
                      {item.type ?? "ATM Transaction"}
                    </strong>

                    <span>
                      {item.timestamp
                        ? new Date(item.timestamp).toLocaleString()
                        : "Date unavailable"}
                    </span>
                  </div>

                  <div className="transaction-amount">
                    <strong>
                      {formatMoney(item.amount)}
                    </strong>

                    <span>
                      {item.status ?? "Completed"}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Customer Support */}
        <section className="support-banner" id="support">
          <div>
            <Headset size={28} />

            <div>
              <h3>Need assistance?</h3>

              <p>
                Intelligent ATM customer support is coming next.
              </p>
            </div>
          </div>

          <span>
            Copilot Studio integration planned
          </span>
        </section>

        {/* Footer */}
        <footer>
          <span>
            © 2026 Next-Gen AI ATM Ecosystem
          </span>

          <span>
            <ShieldCheck size={14} />
            Educational demo · No real banking
          </span>
        </footer>

      </main>
    </div>
  );
}

export default App;
