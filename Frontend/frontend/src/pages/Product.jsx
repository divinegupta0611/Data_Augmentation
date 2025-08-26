import React, { useState, useRef } from 'react';
import '../scripts/ProductCSS.css';

const Product = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [augmentedImages, setAugmentedImages] = useState([]); // new state
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

      // Use the URLs returned by backend directly
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

        {augmentedImages.length > 0 && (
  <div className="augmented-images">
    <h3>Augmented Images:</h3>
    <div className="augmented-list" style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
      {augmentedImages.map((img, i) => (
  <div key={i} style={{ marginBottom: '10px' }}>
    <img src={img} alt={`augmented-${i}`} className="augmented-preview" />

    <a
      href={img}
  download={`augmented-image-${i}.jpg`}
  onClick={(e) => {
    // For cross-origin images, use fetch method
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
  style={{
    display: 'inline-block',
    marginTop: '15px',
    textDecoration: 'none',
    color: '#fff',
    background: '#007bff',
    padding: '5px 10px',
    borderRadius: '5px',
  }}
>
  Download
</a>
  </div>
))}


    </div>
  </div>
)}


        <div className="button-group">
          <button
            className="upload-button"
            onClick={uploadToBackend}
            disabled={!imageFile || isUploading}
          >
            {isUploading && <span className="loading-spinner"></span>}
            {isUploading ? 'Uploading...' : 'Upload Image'}
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
      </div>
      {/* {augmentedImages.length > 0 && (
  <div className="augmented-images">
    <h3>Augmented Images:</h3>
    <div className="augmented-list">
      {augmentedImages.map((img, i) => (
        <img
          key={i}
          src={img}
          alt={`augmented-${i}`}
          className="augmented-preview"
        />
      ))}
    </div>
  </div>
)} */}

    </div>
  );
};

export default Product;
