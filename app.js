import React, { useState } from "react";
import "/fonts/BitcountGridSingle.ttf";


function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleScan = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      // Call your Flask backend API endpoint for scanning
      const response = await fetch("/api/scan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`Scan failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data.vulnerabilities);
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>VulnX - Website Vulnerability Scanner</h1>
      <form onSubmit={handleScan} style={styles.form}>
        <input
          type="text"
          placeholder="Enter website URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={styles.input}
          required
        />
        <button type="submit" style={styles.button} disabled={loading}>
          {loading ? "Scanning..." : "Scan"}
        </button>
      </form>

      {error && <p style={styles.error}>{error}</p>}

      {result && (
        <div style={styles.results}>
          <h2>Scan Results</h2>
          {result.length === 0 ? (
            <p>No vulnerabilities found.</p>
          ) : (
            result.map((vuln, index) => (
              <div key={index} style={styles.vulnerability}>
                <strong>{vuln.type}</strong> at <code>{vuln.url}</code>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 600,
    margin: "40px auto",
    backgroundColor: "#fff",
    padding: 20,
    borderRadius: 8,
    boxShadow: "0 2px 9px #ccc",
    fontFamily: "Arial, sans-serif",
  },
  heading: {
    textAlign: "center",
  },
  form: {
    display: "flex",
    marginBottom: 20,
  },
  input: {
    flexGrow: 1,
    padding: 10,
    fontSize: 16,
    borderRadius: 4,
    border: "1px solid #ccc",
    marginRight: 8,
  },
  button: {
    padding: "10px 20px",
    backgroundColor: "#3f51b5",
    color: "#fff",
    border: "none",
    borderRadius: 4,
    cursor: "pointer",
  },
  results: {
    marginTop: 20,
  },
  vulnerability: {
    backgroundColor: "#ffeaea",
    color: "#d32f2f",
    padding: 10,
    marginBottom: 8,
    borderLeft: "4px solid #d32f2f",
  },
  error: {
    color: "red",
    marginTop: 10,
  },
};
// New, enhanced variants for smoother, more dynamic transitions
const pageVariants = {
  // Start state: slightly scaled down, fully transparent, slightly below position
  hidden: { 
    opacity: 0, 
    y: 20, 
    scale: 0.98,
  },
  // Enter state: full opacity, original position and scale
  enter: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: { 
      duration: 0.7, 
      ease: [0.6, -0.05, 0.01, 0.99], // A custom, "springy" easing curve
    } 
  },
  // Exit state: fades out and moves slightly up
  exit: { 
    opacity: 0, 
    y: -10, 
    scale: 0.99,
    transition: { 
      duration: 0.5, 
      ease: "easeInOut",
    } 
  },
};

// Variants for staggering internal content (like on the Home page)
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delayChildren: 0.2, // Delay before the first child starts
      staggerChildren: 0.15, // Delay between each child
    },
  },
};

const itemVariants = {
  hidden: { y: 30, opacity: 0, filter: 'blur(3px)' },
  visible: { y: 0, opacity: 1, filter: 'blur(0px)' },
};
export default App;

