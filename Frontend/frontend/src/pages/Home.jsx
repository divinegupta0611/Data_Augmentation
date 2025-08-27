import React from 'react';
import '../scripts/HomeCSS.css';
import { Link } from "react-router-dom";
const Home = () => {
  const handleTryFree = () => {
    console.log('Try it for free clicked!');
    // Add your navigation logic here
  };

  return (
    <div className="home-container">
      <nav className="navbar">
        <div className="nav-content">
          <div className="logo">DataAugment</div>
          <ul className="nav-links">
            <li><a href="#features">Features</a></li>
            <li><a href="#pricing">Pricing</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </div>
      </nav>

      <main className="main-content">
        <section className="hero-section">
          <h1 className="hero-title">Transform Your Data with AI-Powered Augmentation</h1>
          <p className="hero-subtitle">
            Enhance your machine learning models with intelligent data augmentation techniques. 
            Generate high-quality synthetic data to improve model performance and reduce overfitting.
          </p>
          <Link to="/product" className="cta-button">
             Try it for free
          </Link>
        </section>

        <section className="features-section" id="features">
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🚀</div>
              <h3 className="feature-title">Intelligent Augmentation</h3>
              <p className="feature-description">
                Advanced AI algorithms automatically generate diverse, high-quality variations of your training data.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3 className="feature-title">Lightning Fast</h3>
              <p className="feature-description">
                Process thousands of samples in seconds with our optimized augmentation pipeline.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3 className="feature-title">Precision Control</h3>
              <p className="feature-description">
                Fine-tune augmentation parameters to match your specific use case and data requirements.
              </p>
            </div>
          </div>
        </section>

        <section className="stats-section">
          <h2 className="hero-title" style={{fontSize: '2.5rem', marginBottom: '1rem'}}>
            Trusted by Data Scientists Worldwide
          </h2>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-number">50M+</span>
              <div className="stat-label">Data Points Generated</div>
            </div>
            <div className="stat-item">
              <span className="stat-number">95%</span>
              <div className="stat-label">Model Accuracy Improvement</div>
            </div>
            <div className="stat-item">
              <span className="stat-number">10K+</span>
              <div className="stat-label">Active Users</div>
            </div>
            <div className="stat-item">
              <span className="stat-number">24/7</span>
              <div className="stat-label">Support Available</div>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p>&copy; 2025 DataAugment. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;