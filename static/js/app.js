// Business Card Generator - Enhanced JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card-item');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                submitBtn.disabled = true;
            }
        });
    });

    // File input preview with drag and drop
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const label = input.nextElementSibling;
        
        // Drag and drop functionality
        label.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.borderColor = '#667eea';
            this.style.background = '#edf2f7';
        });

        label.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.borderColor = '#cbd5e0';
            this.style.background = '#f8fafc';
        });

        label.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderColor = '#cbd5e0';
            this.style.background = '#f8fafc';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                handleFileSelect(input, files[0]);
            }
        });

        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFileSelect(this, this.files[0]);
            }
        });
    });

    function handleFileSelect(input, file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.createElement('img');
                preview.src = e.target.result;
                preview.className = 'logo-preview fade-in';
                preview.style.display = 'block';
                
                const container = input.parentElement;
                const existingPreview = container.querySelector('.logo-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }
                container.appendChild(preview);
            };
            reader.readAsDataURL(file);
        }
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Toast notifications
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} fade-in`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        if (type === 'success') {
            toast.style.background = 'linear-gradient(135deg, #48bb78, #38a169)';
        } else if (type === 'error') {
            toast.style.background = 'linear-gradient(135deg, #f56565, #e53e3e)';
        } else {
            toast.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
        }
        
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    // Add toast functionality to window object
    window.showToast = showToast;

    // QR code click to copy functionality
    const qrCodes = document.querySelectorAll('.qr-code');
    qrCodes.forEach(qr => {
        qr.style.cursor = 'pointer';
        qr.title = 'Click to copy QR code';
        qr.addEventListener('click', function() {
            // Create a temporary canvas to copy the QR code
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = function() {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                canvas.toBlob(function(blob) {
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'business-card-qr.png';
                    a.click();
                    URL.revokeObjectURL(url);
                    showToast('QR code downloaded!', 'success');
                });
            };
            img.src = this.src;
        });
    });

    // Responsive navigation
    const mobileBreakpoint = 768;
    function handleResize() {
        const navLinks = document.querySelector('.nav-links');
        if (window.innerWidth <= mobileBreakpoint) {
            navLinks.style.flexDirection = 'column';
        } else {
            navLinks.style.flexDirection = 'row';
        }
    }

    window.addEventListener('resize', handleResize);
    handleResize(); // Initial call
}); 