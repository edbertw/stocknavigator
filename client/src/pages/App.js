import React, { useState, lazy, Suspense } from 'react';
import '../styles/App.css';
import { useNavigate, Routes, Route } from 'react-router-dom';
import { UserProvider, useUser } from '../contexts/UserContext';

// Lazy load components for better performance
const NextPage = lazy(() => import('./NextPage'));
const NextNextPage = lazy(() => import('./NextNextPage'));

const AppContent = () => {
  const [selectedValue, setSelectedValue] = useState(''); // Selected stock
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(''); // Error state
  const [description, setDescription] = useState(''); // Description state
  const { user } = useUser();
  const navigate = useNavigate(); // Navigation


  const handleSelectChange = (e) => {
    const value = e.target.value;
    setSelectedValue(value); // Update selected stock

    // Update description based on selected stock
    const descriptions = {
      NVDA: 'NVIDIA is a leading manufacturer of GPUs for gaming, AI, and data center computing.',
      NDAQ: 'NASDAQ is the second-largest stock exchange in the world, known for its tech-heavy listings.',
      TSLA: 'Tesla is an electric vehicle and clean energy company led by Elon Musk.',
      HSBC: 'HSBC is a British multinational banking and financial services company with a strong presence in Asia.',
      JPM: 'JPMorgan Chase is a global financial services firm and the largest bank in the U.S. by assets.',
      MS: 'Morgan Stanley is a leading investment bank specializing in wealth management and institutional securities.',
      GS: 'Goldman Sachs is a top-tier investment bank and financial services firm serving corporations and high-net-worth clients.',
      JEF: 'Jefferies is a global investment banking firm focused on equities, fixed income, and advisory services.',
      APPL: 'Apple is a tech giant known for its iPhones, Macs, and services like Apple Music and iCloud.',
      GOOGL: 'Google (Alphabet Inc.) dominates online search, advertising, cloud computing, and AI through products like YouTube and Android.',
      AMZN: 'Amazon is the world’s largest e-commerce company and a leader in cloud computing (AWS).',
      META: 'Meta (formerly Facebook) owns social platforms like Facebook, Instagram, and WhatsApp, and invests heavily in VR/AR.',
      MSFT: 'Microsoft is a software leader (Windows, Office, Azure) and a major player in cloud computing and AI.',
      NFLX: 'Netflix is the leading global streaming service, producing original films and TV shows.',
      DIS: 'Disney is a media and entertainment powerhouse, owning Marvel, Star Wars, ESPN, and theme parks.',
      C: 'Citi is a global bank offering consumer banking, investment services, and corporate finance.',
      V: 'Visa is the world’s largest payment processor, enabling digital transactions worldwide.',
      BLK: 'BlackRock is the world’s largest asset manager, known for its iShares ETFs.',
      IBM: 'IBM is a legacy tech company focusing on hybrid cloud, AI (Watson), and enterprise solutions.',
      UBER: 'Uber is a ride-hailing and food delivery (Uber Eats) platform operating globally.',
      ORCL: 'Oracle provides enterprise software, cloud solutions, and database management systems.',
      WMT: 'Walmart is the world’s largest retailer, operating hypermarkets and e-commerce platforms.',
      MA: 'Mastercard is a global payments technology company, second only to Visa in transaction volume.',
      XOM: 'ExxonMobil is one of the largest publicly traded oil and gas companies.',
      COST: 'Costco operates membership-based warehouse clubs offering bulk retail goods.',
      BAC: 'Bank of America is a major U.S. bank providing consumer banking, investing, and corporate services.',
      PLTR: 'Palantir provides big data analytics and AI software for governments and enterprises.',
      KO: 'Coca-Cola is the world’s largest beverage company, famous for its soft drinks.',
      PEP: 'PepsiCo is a global food and beverage leader (Pepsi, Lay’s, Gatorade).',
      UNH: 'UnitedHealth Group is the largest U.S. health insurer and a provider of healthcare services.',
      CRM: 'Salesforce is the leading CRM (customer relationship management) software provider.',
      MCD: 'McDonald’s is the world’s largest fast-food chain, known for its burgers and fries.',
      ACN: 'Accenture is a global IT services and consulting firm specializing in digital transformation.',
      BA: 'Boeing is a major aerospace company manufacturing commercial jets and defense systems.',
      ABNB: 'Airbnb operates an online marketplace for short-term lodging and travel experiences.',
      AON: 'Aon is a professional services firm offering risk management and insurance solutions.',
      DASH: 'DoorDash is a leading food delivery platform in the U.S. and other markets.',
      INTC: 'Intel is a semiconductor leader, producing CPUs for PCs, servers, and data centers.',
      ZM: 'Zoom provides video conferencing software widely used for remote work and education.',
      SBUX: 'Starbucks is the world’s largest coffeehouse chain, offering beverages and food.',
      NKE: 'Nike is a global leader in athletic footwear, apparel, and sports equipment.',
      CB: 'Chubb is a multinational insurer specializing in property, casualty, and reinsurance.',
      CRWD: 'CrowdStrike is a cybersecurity firm offering cloud-based endpoint protection.',
      BX: 'Blackstone is a leading private equity and alternative investment firm.',
      MFC: 'Manulife is a Canadian insurance and financial services company with global operations.',
      '1299.HK': 'AIA Group is a pan-Asian life insurance giant headquartered in Hong Kong.',
      '0388.HK': 'Hong Kong Exchanges & Clearing (HKEX) operates the Hong Kong Stock Exchange.',
      '0700.HK': 'Tencent is a Chinese tech conglomerate known for WeChat, gaming, and fintech.',
      '2318.HK': 'Ping An Insurance is a Chinese financial services group focusing on insurance and banking.',
      '0939.HK': 'China Construction Bank (CCB) is one of China’s "Big Four" state-owned banks.',
      '0005.HK': 'HSBC Holdings is the Hong Kong-listed entity of the global HSBC banking group.',
      '0001.HK': 'CK Hutchison Holdings is a Hong Kong conglomerate with global ports, retail, and telecom interests.',
      '0002.HK': 'CLP Holdings is a Hong Kong-based electric utility company operating in Asia.',
      '0011.HK': 'MTR Corporation operates Hong Kong’s metro system and has international rail investments.',
      '3988.HK': 'Bank of China (Hong Kong) is a leading commercial bank in Hong Kong and a subsidiary of Bank of China.',
      '0003.HK': 'Hang Seng Bank is a Hong Kong-based banking and financial services company, majority-owned by HSBC.',
      '9888.HK': 'Baidu is a Chinese multinational technology company specializing in Internet-related services and AI.',
      '9988.HK': 'Alibaba Group is a Chinese multinational technology company focusing on e-commerce, retail, and cloud computing.',
      '9618.HK': 'Meituan is a Chinese e-commerce platform for services including food delivery, hotels, and other local services.',
      '8147.HK': 'Millennium Pacific Group Holdings Ltd is an investment holding company primarily engaged in R&D, Manufacture and etc.',
      '1828.HK': 'FWD Group is a pan-Asian life insurance company headquartered in Hong Kong.',
      '2628.HK': 'China Life Insurance is the largest state-owned life insurance company in mainland China.',
      '0966.HK': 'China Taiping Insurance is a Chinese state-owned insurance and financial services company.',
      '1508.HK': 'China Reinsurance Group is the sole national reinsurance company in China.'
    };

    setDescription(descriptions[value] || '');
  };

  const handleSubmit = () => {
    setLoading(true); // Show loading
    setError(''); // Clear errors

    // API call to submit stock
    fetch('http://127.0.0.1:8000/api/submit-stock/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        stock_symbol: selectedValue, // Send selected stock
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.company) {
          // Navigate to NextPage with state
          navigate('/next-page', { state: { stockSymbol: selectedValue, company: data.company } });
        } else {
          setError(data.error || 'Company not found'); // Handle error
        }
        setLoading(false); // Hide loading
      })
      .catch((err) => {
        setError('An error occurred while submitting the stock.');
        setLoading(false); // Hide loading
      });
  };

  return (
    <div className="trading-platform">
      {/* Sidebar Navigation */}
      <nav className="trading-sidebar">
        <div className="sidebar-header">
          <a href="/" className="sidebar-logo">
            <div className="sidebar-logo-icon">📈</div>
            <span>StockNavigator</span>
          </a>
        </div>
        <div className="sidebar-nav">
          <a href="/app" className="nav-item active">
            <span className="nav-icon">🏠</span>
            <span>Dashboard</span>
          </a>
          <a href="/analytics" className="nav-item">
            <span className="nav-icon">📊</span>
            <span>Analytics</span>
          </a>
          <a href="/login" className="nav-item" onClick={() => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }}>
            <span className="nav-icon">🚪</span>
            <span>Sign Out</span>
          </a>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="trading-main">
        {/* Header */}
        <header className="trading-header">
          <div className="header-left">
            <h1 className="header-title">Trading Dashboard</h1>
            <p className="header-subtitle">Real-time market analysis & predictions</p>
          </div>
          <div className="header-right">
            {user && (
              <div className="user-info">
                <div className="user-avatar">
                  {user.username ? user.username.charAt(0).toUpperCase() : 'U'}
                </div>
                <span className="user-name">{user.username}</span>
              </div>
            )}
          </div>
        </header>

        {/* Main Content */}
        <div className="trading-content">
          {/* Stock Selector Section */}
          <section className="stock-selector-section">
            <h2 className="section-title">Stock Analysis</h2>
            <div className="stock-search-container">
              <select
                value={selectedValue}
                onChange={handleSelectChange}
                className="stock-dropdown"
              >
                <option value="">-- Choose a Stock --</option>
                <option value="NVDA">NVIDIA (NVDA)</option>
                <option value="NDAQ">NASDAQ (NDAQ)</option>
                <option value="TSLA">TESLA (TSLA)</option>
                <option value="HSBC">HSBC (HSBC)</option>
                <option value="JPM">JPMORGAN (JPM)</option>
                <option value="MS">MORGAN STANLEY (MS)</option>
                <option value="GS">GOLDMAN SACHS (GS)</option>
                <option value="JEF">JEFFERIES (JEF)</option>
                <option value="APPL">APPLE (APPL)</option>
                <option value="GOOGL">GOOGLE (GOOGL)</option>
                <option value="AMZN">AMAZON (AMZN)</option>
                <option value="META">META (META)</option>
                <option value="MSFT">MICROSOFT (MSFT)</option>
                <option value="NFLX">NETFLIX (NFLX)</option>
                <option value="DIS">DISNEY (DIS)</option>
                <option value="C">CITI (C)</option>
                <option value="V">VISA (V)</option>
                <option value="BLK">BLACKROCK (BLK)</option>
                <option value="IBM">IBM (IBM)</option>
                <option value="UBER">UBER (UBER)</option>
                <option value="ORCL">ORACLE (ORCL)</option> 
                <option value="WMT">WALMART (WMT)</option>
                <option value="MA">MASTERCARD (MA)</option>
                <option value="XOM">EXXONMOBIL (XOM)</option>
                <option value="COST">COSTCO (COST)</option>
                <option value="BAC">BANK OF AMERICA (BAC)</option>
                <option value="PLTR">PALANTIR TECHNOLOGIES (PLTR)</option>
                <option value="KO">COCA-COLA (KO)</option>
                <option value="PEP">PEPSICO (PEP)</option>
                <option value="UNH">UNITED HEALTHCARE (UNH)</option>
                <option value="CRM">SALESFORCE (CRM)</option>
                <option value="MCD">MCDONALDS (MCD)</option>
                <option value="ACN">ACCENTURE (ACN)</option>
                <option value="BA">BOEING (BA)</option>
                <option value="ABNB">AIRBNB (ABNB)</option>
                <option value="AON">AON (AON)</option>
                <option value="DASH">DOORDASH (DASH)</option>
                <option value="INTC">INTEL (INTC)</option>
                <option value="ZM">ZOOM (ZM)</option>
                <option value="SBUX">STARBUCKS (SBUX)</option>
                <option value="NKE">NIKE (NKE)</option>
                <option value="CB">CHUBB LIMITED (CB)</option>
                <option value="CRWD">CROWDSTRIKE (CRWD)</option>
                <option value="BX">BLACKSTONE (BX)</option>
                <option value="MFC">MANULIFE US (MFC)</option>
                <option value="1299.HK">AIA HK (1299.HK)</option>
                <option value="0388.HK">HKEX (0388.HK)</option>
                <option value="0700.HK">TENCENT HK (0700.HK)</option>
                <option value="2318.HK">PING AN HK (2318.HK)</option>
                <option value="0939.HK">CITIC BANK HK (0939.HK)</option>
                <option value="0005.HK">HSBC HK (0005.HK)</option>
                <option value="0001.HK">CKH HOLDINGS HK (0001.HK)</option>
                <option value="0002.HK">CLP HOLDINGS HK (0002.HK)</option>
                <option value="0011.HK">MTR CORPORATION HK (0011.HK)</option>
                <option value="3988.HK">BANK OF CHINA HK (3988.HK)</option>
                <option value="0003.HK">HANG SENG BANK HK (0003.HK)</option>
                <option value="9888.HK">BAIDU INC (9888.HK)</option>
                <option value="9988.HK">ALIBABA GROUP (9988.HK)</option>
                <option value="9618.HK">MEITUAN (9618.HK)</option>
                <option value="8147.HK">MILLENNIUM PACIFIC HOLDINGS (8147.HK)</option>
                <option value="1828.HK">FWD GROUP (1828.HK)</option>
                <option value="2628.HK">CHINA LIFE INSURANCE (2628.HK)</option>
                <option value="0966.HK">CHINA TAIPING INSURANCE (0966.HK)</option>
                <option value="1508.HK">CHINA REINSURANCE GROUP (1508.HK)</option>
              </select>
              <button
                onClick={handleSubmit}
                className="submit-button"
                disabled={loading || !selectedValue}
              >
                {loading ? (
                  <>
                    <div className="loading-spinner"></div>
                    Analyzing...
                  </>
                ) : (
                  'Analyze Stock'
                )}
              </button>
            </div>

            {description && (
              <div className="stock-description">
                <h3>About {selectedValue}</h3>
                <p>{description}</p>
              </div>
            )}

            {error && <div className="error-message">{error}</div>}
          </section>
        </div>
      </main>


      <Routes>
        <Route 
          path="/next-page" 
          element={
            <Suspense fallback={<div className="loading">Loading...</div>}>
              <NextPage />
            </Suspense>
          } 
        />
        <Route 
          path="/next-next-page" 
          element={
            <Suspense fallback={<div className="loading">Loading...</div>}>
              <NextNextPage />
            </Suspense>
          } 
        />
      </Routes>
    </div>
  );
};

const App = () => {
  return (
    <UserProvider>
      <AppContent />
    </UserProvider>
  );
};

export default App;