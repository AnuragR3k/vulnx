import React, { useState, useEffect, useRef } from "react";
import logo from "./assets/V-removebg-preview.png";
import "./index.css";





function Background3D() {
  const canvasRef = useRef(null);
  const animRef = useRef(0);
  const starsRef = useRef([]);

  useEffect(() => {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '0';
    canvas.style.pointerEvents = 'none';
    document.body.appendChild(canvas);
    canvasRef.current = canvas;

    const ctx = canvas.getContext('2d');
    let w = canvas.width = window.innerWidth;
    let h = canvas.height = window.innerHeight;

    const numStars = Math.min(250, Math.floor((w * h) / 8000));

    function initStars() {
      const stars = [];
      for (let i = 0; i < numStars; i++) {
        stars.push({
          x: (Math.random() * 5 - 1) * w,
          y: (Math.random() * 5 - 1) * h,
          z: Math.random() * 1000 + 100,
          r: Math.random() * 1.5 + 0.3
        });
      }
      starsRef.current = stars;
    }

    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
      initStars();
    }

    function draw() {
      const gradient = ctx.createLinearGradient(0, 0, 0, h);
      gradient.addColorStop(0, '#0a0a0d');
      gradient.addColorStop(0.5, '#0f0f1a');
      gradient.addColorStop(1, '#1a1a2e');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, w, h);

      const cx = w / 2;
      const cy = h / 2;
      ctx.fillStyle = '#7aa2ff';
      for (const s of starsRef.current) {
        s.z -= 1;
        if (s.z <= 1) {
          s.x = (Math.random() * 3 - 1) * w;
          s.y = (Math.random() * 3 - 1) * h;
          s.z = 1000;
        }
        const k = 500 / s.z;
        const px = cx + s.x * k * 0.002;
        const py = cy + s.y * k * 0.002;
        const pr = s.r * k * 0.05;
        if (px < 0 || px > w || py < 0 || py > h) continue;
        ctx.beginPath();
        ctx.arc(px, py, pr, 0, Math.PI * 2);
        ctx.fill();
      }
      animRef.current = requestAnimationFrame(draw);
    }

    initStars();
    draw();
    window.addEventListener('resize', resize);
    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener('resize', resize);
      if (canvas && canvas.parentNode) canvas.parentNode.removeChild(canvas);
    };
  }, []);

  return null;
}

// Navigation Bar Component
function Navbar({ currentNav, setNav }) {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 100);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      {/* Single stretching transparent box */}
      <div style={{
        position: 'fixed',
        top: 20,
        left: isScrolled ? '50%' : '80px',
        right: isScrolled ? 'auto' : '80px',
        transform: isScrolled ? 'translateX(-50%)' : 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: isScrolled ? 'center' : 'space-between',
        background: 'rgba(21, 21, 21, 0.7)',
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)', // Safari support
        borderRadius: '10px',
        padding: '10px 20px',
        border: '1px solid rgba(48, 79, 254, 0.3)',
        zIndex: 1001,
        transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
        boxShadow: isScrolled 
          ? '0 4px 12px rgba(0, 0, 0, 0.3)' 
          : '0 2px 8px rgba(0, 0, 0, 0.2)',
        minHeight: '60px',
      }}>
        
        {/* Logo - fades out when scrolled */}
        <img 
          src={logo}
          alt="VulnX Logo" 
          style={{
            width: isScrolled ? 0 : '40px',
            height: isScrolled ? 0 : '40px',
            cursor: 'pointer',
            filter: 'drop-shadow(0 2px 8px rgba(48, 79, 254, 0.4))',
            opacity: isScrolled ? 0 : 1,
            marginRight: isScrolled ? 0 : '16px',
            marginTop: '-3px',
            marginBottom: '3px',
            transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
            pointerEvents: isScrolled ? 'none' : 'auto',
            overflow: 'hidden',
            display: 'block',
          }}
          onClick={() => setNav("home")}
        />
        
        {/* Navigation Links - always visible */}
        <div style={{
          display: 'flex',
          gap: '4px',
          alignItems: 'center',
        }}>
          <button 
            style={{...navStyles.navLink, ...(currentNav === "home" ? navStyles.navLinkActive : {})}}
            onClick={() => setNav("home")}
          >
            Home
          </button>
          <button 
            style={{...navStyles.navLink, ...(currentNav === "scan" ? navStyles.navLinkActive : {})}}
            onClick={() => setNav("scan")}
          >
            Scan
          </button>
          <button 
            style={{...navStyles.navLink, ...(currentNav === "tips" ? navStyles.navLinkActive : {})}}
            onClick={() => setNav("tips")}
          >
            Tips
          </button>
          <button 
            style={{...navStyles.navLink, ...(currentNav === "about" ? navStyles.navLinkActive : {})}}
            onClick={() => setNav("about")}
          >
            About
          </button>
        </div>

        {/* Auth Buttons - fade out when scrolled */}
        <div style={{
          display: 'flex',
          gap: '12px',
          alignItems: 'center',
          marginLeft: isScrolled ? 0 : '16px',
          width: isScrolled ? 0 : 'auto',
          opacity: isScrolled ? 0 : 1,
          transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
          pointerEvents: isScrolled ? 'none' : 'auto',
          overflow: 'hidden',
          whiteSpace: 'nowrap',
        }}>
          <button 
            style={navStyles.loginBtn}
            onClick={() => alert("Login functionality coming soon!")}
          >
            Log In
          </button>
          <button 
            style={navStyles.signupBtn}
            onClick={() => alert("Sign up functionality coming soon!")}
          >
            Sign Up
          </button>
        </div>
      </div>
    </>
  );
}

function App() {
  const [nav, setNav] = useState("home");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState("basic");
  const [acceptedTerms, setAcceptedTerms] = useState(false);

  useEffect(() => {
    const origBg = document.body.style.background;
    document.body.style.background = '#000';
    return () => { document.body.style.background = origBg; };
  }, []);

  const handleScan = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const response = await fetch("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, mode }),
      });
      if (!response.ok) throw new Error(`Scan failed: ${response.statusText}`);
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      setResult(data.vulnerabilities || []);
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    const dateStr = new Date().toLocaleString();
    let html = `<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Scan Report</title></head><body style='font-family: monospace; background:#0a0a0d;color:#fafafa;'>`;
    html += `<h1>VulnX Scan Report</h1>`;
    html += `<p><b>Target:</b> ${url}</p>`;
    html += `<p><b>Mode:</b> ${mode.charAt(0).toUpperCase() + mode.slice(1)}</p>`;
    html += `<p><b>Date:</b> ${dateStr}</p>`;
    if (!result || result.length === 0) {
      html += `<div style='margin-top:20px;'><b>No vulnerabilities found.</b></div>`;
    } else {
      html += `<h2>Vulnerabilities</h2>`;
      html += result.map(vuln => `<div style='margin-bottom:12px;padding:8px 12px;border-left:4px solid #d32f2f;background:#23171b;'><b>${vuln.type}</b> at <code>${vuln.url}</code>${vuln.risk ? ` <span style='color:#d32f2f'><b>[${vuln.risk}]</b></span>` : ''}${vuln.description ? `<div style='font-size:90%;margin-top:5px;'>${vuln.description}</div>` : ''}</div>`).join('');
    }
    html += `</body></html>`;
    const blob = new Blob([html], {type: "text/html"});
    const downloadUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = `scan-report-${(url||'site').replace(/[^a-zA-Z0-9]/g, '_')}.html`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(downloadUrl); document.body.removeChild(a); }, 250);
  };

// Home page
if (nav === "home") {
  return (
    <>
      <Background3D />
      <Navbar currentNav={nav} setNav={setNav} />
      <div style={styles.homeBg}>
        <div style={styles.homeContent}>
          <h1 style={{
            fontSize: 90,
            fontWeight: 400,
            textAlign: 'center',
            color: '#fafbfc',
            marginBottom: 300,
            marginTop: 10,
            letterSpacing: '0.05em',
            lineHeight: 1.2,
            fontFamily: "'BitcountGridSingle', monospace",
            textTransform: 'uppercase',
          }}>
            Scan Faster,<br/>Secure Faster
          </h1>
          
          {/* Description */}
          <p style={{
            textAlign: 'center',
            color: '#bbb',
            fontSize: 18,
            lineHeight: 1.6,
            maxWidth: 700,
            marginBottom: 32,
            marginTop: -270,
            fontFamily: "'BitcountGridSingle', monospace",
            fontWeight: 400,
            letterSpacing: '0.02em',
          }}>
            Automated vulnerability detection for modern web applications. 
            Find XSS, SQL Injection, and 50+ security flaws in seconds.
          </p>
          
          <button style={styles.button} onClick={()=>setNav("scan")}>Scan Website</button>
        </div>
      </div>
      
      {/* ADD THIS - Extra content to make page scrollable */}
      <div style={{
        minHeight: '100vh',
        padding: '100px 20px',
        textAlign: 'center',
        color: '#fff',
        position: 'relative',
        zIndex: 1,
      }}>
        <h2 style={{fontSize: 40, marginBottom: 40, fontFamily: "'BitcountGridSingle', monospace"}}>
          Features
        </h2>
        <div style={{maxWidth: 800, margin: '0 auto', fontSize: 18, lineHeight: 1.8}}>
          <p style={{marginBottom: 30}}>🔍 Comprehensive vulnerability scanning</p>
          <p style={{marginBottom: 30}}>⚡ Fast and automated detection</p>
          <p style={{marginBottom: 30}}>📊 Detailed reports with actionable insights</p>
          <p style={{marginBottom: 30}}>🛡️ XSS, SQL Injection, and more</p>
        </div>
      </div>
    </>
  );
}


  // Tips page
  if (nav === "tips") {
    return (
      <>
        <Background3D />
        <Navbar currentNav={nav} setNav={setNav} />
        <div style={styles.container}>
          <h1 style={styles.heading}>Security Tips</h1>
          <div style={{marginTop: 24, color: '#f7f7fa'}}>
            <h3 style={{color: '#304ffe', marginBottom: 12}}>Best Practices for Web Security</h3>
            <ul style={{lineHeight: 1.8}}>
              <li>Always use HTTPS for secure communication</li>
              <li>Keep your software and dependencies up to date</li>
              <li>Implement strong authentication and authorization</li>
              <li>Validate and sanitize all user inputs</li>
              <li>Use parameterized queries to prevent SQL injection</li>
              <li>Implement Content Security Policy (CSP) headers</li>
              <li>Regular security audits and penetration testing</li>
              <li>Use secure password hashing (bcrypt, Argon2)</li>
              <li>Implement rate limiting to prevent brute force attacks</li>
              <li>Keep security logs and monitor for suspicious activity</li>
            </ul>
          </div>
        </div>
      </>
    );
  }

  // About page
  if (nav === "about") {
    return (
      <>
        <Background3D />
        <Navbar currentNav={nav} setNav={setNav} />
        <div style={styles.container}>
          <h1 style={styles.heading}>About VulnX</h1>
          <div style={{marginTop: 24, color: '#f7f7fa', lineHeight: 1.8}}>
            <p>
              VulnX is an automated website vulnerability scanner designed to help security professionals 
              and developers identify common security weaknesses in web applications.
            </p>
            <h3 style={{color: '#304ffe', marginTop: 24, marginBottom: 12}}>Features</h3>
            <ul>
              <li>Basic vulnerability scanning (XSS, SQL Injection)</li>
              <li>Advanced scanning with OWASP ZAP integration</li>
              <li>Detailed vulnerability reports</li>
              <li>Export scan results as HTML reports</li>
            </ul>
            <h3 style={{color: '#304ffe', marginTop: 24, marginBottom: 12}}>Disclaimer</h3>
            <p style={{color: '#ff7a7a'}}>
              This tool is for educational and authorized testing purposes only. 
              Always obtain proper permission before scanning any website you do not own.
            </p>
          </div>
        </div>
      </>
    );
  }

  // Permission modal for scan page
  if (nav === "scan" && !acceptedTerms) {
    return (
      <>
        <Background3D />
        <Navbar currentNav={nav} setNav={setNav} />
        <div style={modalStyles.overlay}>
          <div style={modalStyles.modal}>
            <h2>Permission Required</h2>
            <p>
              <b>Important:</b> By proceeding, you confirm that you own or have explicit permission to scan the target website for vulnerabilities.<br /><br />
              Unauthorized security testing of systems you do not own or have written permission for may violate the law, terms of service, or ethical standards.<br /><br />
              <b>Do you confirm you have the right to scan the entered domain?</b>
            </p>
            <button style={styles.button} onClick={() => setAcceptedTerms(true)}>
              I Accept and Have Permission
            </button>
            <button style={{...styles.button,marginTop:12,background:'#30313a'}} onClick={()=>setNav("home")}>Go Back</button>
          </div>
        </div>
      </>
    );
  }

  // Scan page
  if (nav === "scan") {
    return (
      <>
        <Background3D />
        <Navbar currentNav={nav} setNav={setNav} />
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
            <select value={mode} onChange={(e) => setMode(e.target.value)} style={styles.select}>
              <option value="basic">Basic</option>
              <option value="zap">ZAP</option>
            </select>
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
              <button style={{...styles.button, marginTop: 18}} onClick={downloadReport}>
                Download Report
              </button>
            </div>
          )}
        </div>
      </>
    );
  }

  return null;
}

// Navigation styles
const navStyles = {
  navLink: {
    background: 'transparent',
    border: 'none',
    color: '#aaa',
    fontSize: 14,
    fontWeight: 400,
    cursor: 'pointer',
    padding: '10px 18px',
    borderRadius: 6,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    fontFamily: "'BitcountGridSingle', monospace",
    letterSpacing: '0.03em',
  },
  navLinkActive: {
    color: '#fff',
    background: 'rgba(48, 79, 254, 0.8)',
  },
  loginBtn: {
    background: 'transparent',
    border: '1px solid rgba(48, 79, 254, 0.5)',
    color: '#fff',
    fontSize: 13,
    fontWeight: 400,
    cursor: 'pointer',
    padding: '10px 20px',
    borderRadius: 6,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    fontFamily: "'BitcountGridSingle', monospace",
    letterSpacing: '0.03em',
  },
  signupBtn: {
    background: '#000',
    border: '1px solid #000',
    color: '#fff',
    fontSize: 13,
    fontWeight: 400,
    cursor: 'pointer',
    padding: '10px 20px',
    borderRadius: 6,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    fontFamily: "'BitcountGridSingle', monospace",
    letterSpacing: '0.03em',
  },
};

const styles = {
  homeBg: {
    minHeight: '100vh',
    background:'transparent',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '24px',
    paddingTop: 100,
    position: 'relative',
    zIndex: 1,
  },
  homeContent: {
    display:'flex',
    flexDirection:'column',
    alignItems:'center',
  },
  container: {
    maxWidth: 800,
    margin: "100px auto 40px",
    backgroundColor: "#151515",
    padding: 32,
    borderRadius: 8,
    fontFamily: "'BitcountGridSingle', monospace",
    fontWeight: 400,
    color: "#f7f7fa",
    boxShadow: "none",
    position: 'relative',
    zIndex: 1,
  },
  heading: {
    textAlign: "center",
    color: "#fafbfc",
    fontFamily: "'BitcountGridSingle', monospace",
    fontWeight: 400,
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
  },
  form: {
    display: "flex",
    marginBottom: 20,
    marginTop: 24,
  },
  input: {
    flexGrow: 1,
    padding: 10,
    fontSize: 15,
    borderRadius: 4,
    border: "1px solid #30313a",
    marginRight: 8,
    background: "#252730",
    color: "#f7f7fa",
    fontFamily: "'BitcountGridSingle', monospace",
    fontWeight: 400,
  },
  select: {
    padding: 10,
    borderRadius: 4,
    border: "1px solid #30313a",
    marginRight: 8,
    background: "#252730",
    color: "#f7f7fa",
    fontFamily: "'BitcountGridSingle', monospace",
    fontWeight: 400,
  },
  button: {
    padding: "10px 20px",
    backgroundColor: "#304ffe",
    color: "#f7f7fa",
    border: "none",
    borderRadius: 4,
    cursor: "pointer",
    fontWeight: 400,
    letterSpacing: '0.05em',
    boxShadow: '0 1px 4px #0005',
    transition: 'background 0.18s',
    fontFamily: "'BitcountGridSingle', monospace",
    textTransform: 'uppercase',
  },
  results: {
    marginTop: 20,
    color: "#fafbfc",
  },
  vulnerability: {
    backgroundColor: "#23171b",
    color: "#ff7a7a",
    padding: 10,
    marginBottom: 8,
    borderLeft: "4px solid #c62828",
    borderRadius: 3,
    fontFamily: "'BitcountGridSingle', monospace",
    fontWeight: 400,
  },
  error: {
    color: "#ff5252",
    marginTop: 10,
    fontFamily: "'BitcountGridSingle', monospace",
    fontWeight: 400,
  },
};

const modalStyles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.85)',
    zIndex: 999,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  modal: {
    background: '#191925',
    borderRadius: 10,
    padding: '32px 28px',
    maxWidth: 450,
    boxShadow: "none",
    border: '1px solid #304ffe',
    textAlign: 'center',
    color: '#fafbfc',
    position: 'relative',
    zIndex: 1001,
    fontFamily: "'BitcountGridSingle', monospace",
    fontWeight: 400,
  }
};

export default App;
