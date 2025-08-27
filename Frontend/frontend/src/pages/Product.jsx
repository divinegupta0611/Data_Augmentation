import React, { useState, useRef } from 'react';
import '../scripts/ProductCSS.css';
const Product = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [augmentedImages, setAugmentedImages] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const fileInputRef = useRef(null);

  const uploadToBackend = async () => {
    if (!imageFile) {
      setUploadMessage('Please select an image first');
      return;
    }

    setIsUploading(true);
    setUploadMessage('');

    try {
      const formData = new FormData();
      formData.append('image', imageFile);

      const response = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadMessage('Image uploaded successfully!');
        console.log('Upload response:', result);

        if (result.augmented && result.augmented.length > 0) {
          setAugmentedImages(result.augmented.map((url) => `http://localhost:8000${url}`));
        }
      } else {
        setUploadMessage(result.error || 'Upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadMessage('Upload failed. Please check your connection.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = (e) => setSelectedImage(e.target.result);
      reader.readAsDataURL(file);
      setUploadMessage('');
      setAugmentedImages([]);
    } else {
      setUploadMessage('Please select a valid image file');
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();

    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = (e) => setSelectedImage(e.target.result);
      reader.readAsDataURL(file);
      setUploadMessage('');
      setAugmentedImages([]);
    } else {
      setUploadMessage('Please drop a valid image file');
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const clearImage = () => {
    setSelectedImage(null);
    setImageFile(null);
    setAugmentedImages([]);
    setUploadMessage('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="product-page">
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
      <div className="upload-section">
        <h2 className="section-title">Upload Image for Augmentation</h2>

        <div
          className="upload-area"
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragEnter={(e) => e.currentTarget.classList.add('drag-over')}
          onDragLeave={(e) => e.currentTarget.classList.remove('drag-over')}
        >
          <div className="upload-icon">📁</div>
          <div className="upload-text">
            Click to select or drag & drop your image
          </div>
          <div className="upload-subtext">
            Supports JPG, PNG, GIF • Max size: 10MB
          </div>
        </div>

        <input
          type="file"
          ref={fileInputRef}
          className="file-input"
          accept="image/*"
          onChange={handleFileSelect}
        />

        {imageFile && (
          <div className="file-info">
            <div className="file-name">{imageFile.name}</div>
            <div className="file-size">{(imageFile.size / 1024 / 1024).toFixed(2)} MB</div>
          </div>
        )}

        {selectedImage && (
          <div className="image-preview">
            <img src={selectedImage} alt="Preview" className="preview-image" />
          </div>
        )}

        <div className="button-group">
          <button
            className="upload-button"
            onClick={uploadToBackend}
            disabled={!imageFile || isUploading}
          >
            {isUploading && <span className="loading-spinner"></span>}
            {isUploading ? 'Processing...' : 'Upload & Augment'}
          </button>

          {selectedImage && (
            <button className="clear-button" onClick={clearImage}>
              Clear Image
            </button>
          )}
        </div>

        {uploadMessage && (
          <div className={`message ${uploadMessage.includes('successfully') ? 'success' : 'error'}`}>
            {uploadMessage}
          </div>
        )}

        {augmentedImages.length > 0 && (
          <div className="augmented-images">
            <h3>✨ Augmented Results</h3>
            <div className="augmented-list">
              {augmentedImages.map((img, i) => (
  <div key={i} className="augmented-item">
    <img src={img} alt={`augmented-${i}`} className="augmented-preview" />
    <a
      href={img}
      download={`augmented-image-${i}.jpg`}
      className="download-button"
      onClick={(e) => {
        e.preventDefault();
        fetch(img)
          .then(res => res.blob())
          .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `augmented-image-${i}.jpg`;
            a.click();
            URL.revokeObjectURL(url);
          })
          .catch(() => window.open(img, '_blank'));
      }}
    >
      📥 Download
    </a>
  </div>
))}

{/* Download All as ZIP button */}
{augmentedImages.length > 0 && (
  <div style={{ marginTop: "20px" }}>
    <button
      className="download-all-button"
      onClick={async () => {
        const JSZip = (await import("jszip")).default;
        const { saveAs } = await import("file-saver");
        const zip = new JSZip();

        for (let i = 0; i < augmentedImages.length; i++) {
          const response = await fetch(augmentedImages[i]);
          const blob = await response.blob();
          zip.file(`augmented-image-${i}.jpg`, blob);
        }

        zip.generateAsync({ type: "blob" }).then((content) => {
          saveAs(content, "augmented-images.zip");
        });
      }}
    >
      📥 Download All as ZIP
    </button>
  </div>
)}

            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Product;