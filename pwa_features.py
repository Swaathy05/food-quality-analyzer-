"""
Progressive Web App Features for Mobile-First Experience
"""

import streamlit as st
import json

def add_pwa_features():
    """Add PWA capabilities to make it mobile-friendly"""
    
    # PWA Manifest
    manifest = {
        "name": "AI Food Quality Analyzer",
        "short_name": "FoodAI",
        "description": "AI-powered food quality and chemical analysis",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#667eea",
        "icons": [
            {
                "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyIiBoZWlnaHQ9IjE5MiIgdmlld0JveD0iMCAwIDE5MiAxOTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiByeD0iMjQiIGZpbGw9IiM2NjdlZWEiLz4KPHN2ZyB4PSI0OCIgeT0iNDgiIHdpZHRoPSI5NiIgaGVpZ2h0PSI5NiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+CjxwYXRoIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPgo8L3N2Zz4KPC9zdmc+",
                "sizes": "192x192",
                "type": "image/svg+xml"
            }
        ]
    }
    
    # Add PWA meta tags
    st.markdown(f"""
    <script>
        // Add manifest
        const manifestBlob = new Blob(['{json.dumps(manifest)}'], {{type: 'application/json'}});
        const manifestURL = URL.createObjectURL(manifestBlob);
        const link = document.createElement('link');
        link.rel = 'manifest';
        link.href = manifestURL;
        document.head.appendChild(link);
        
        // Service Worker Registration
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('/sw.js').then(function(registration) {{
                console.log('SW registered: ', registration);
            }}).catch(function(registrationError) {{
                console.log('SW registration failed: ', registrationError);
            }});
        }}
    </script>
    
    <style>
        /* Mobile-first responsive design */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }}
            
            .stButton > button {{
                width: 100%;
                margin-bottom: 0.5rem;
            }}
            
            .stFileUploader {{
                margin-bottom: 1rem;
            }}
        }}
        
        /* Install prompt */
        .install-prompt {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 1000;
            display: none;
        }}
    </style>
    
    <div id="installPrompt" class="install-prompt">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>📱 Install Food Analyzer</strong><br>
                <small>Add to home screen for better experience</small>
            </div>
            <button onclick="installApp()" style="background: white; color: #667eea; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                Install
            </button>
        </div>
    </div>
    
    <script>
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('installPrompt').style.display = 'block';
        }});
        
        function installApp() {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        console.log('User accepted the install prompt');
                    }}
                    deferredPrompt = null;
                    document.getElementById('installPrompt').style.display = 'none';
                }});
            }}
        }}
    </script>
    """, unsafe_allow_html=True)

def add_mobile_camera_integration():
    """Add mobile camera integration for direct photo capture"""
    
    st.markdown("""
    <script>
        function openCamera() {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
                .then(function(stream) {
                    const video = document.createElement('video');
                    video.srcObject = stream;
                    video.play();
                    
                    // Create camera interface
                    const cameraDiv = document.createElement('div');
                    cameraDiv.innerHTML = `
                        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: black; z-index: 9999;">
                            <video id="cameraVideo" style="width: 100%; height: 100%; object-fit: cover;"></video>
                            <div style="position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);">
                                <button onclick="capturePhoto()" style="width: 70px; height: 70px; border-radius: 50%; background: white; border: 3px solid #667eea; cursor: pointer;">📷</button>
                                <button onclick="closeCamera()" style="margin-left: 20px; padding: 10px 20px; background: #ff4444; color: white; border: none; border-radius: 5px; cursor: pointer;">Close</button>
                            </div>
                        </div>
                    `;
                    document.body.appendChild(cameraDiv);
                    document.getElementById('cameraVideo').srcObject = stream;
                })
                .catch(function(error) {
                    alert('Camera access denied or not available');
                });
            }
        }
        
        function capturePhoto() {
            const video = document.getElementById('cameraVideo');
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            
            canvas.toBlob(function(blob) {
                // Create file input and trigger upload
                const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
                // Trigger Streamlit file upload (would need integration)
                console.log('Photo captured:', file);
            });
        }
        
        function closeCamera() {
            const cameraDiv = document.querySelector('div[style*="position: fixed"]');
            if (cameraDiv) {
                const video = document.getElementById('cameraVideo');
                if (video && video.srcObject) {
                    video.srcObject.getTracks().forEach(track => track.stop());
                }
                cameraDiv.remove();
            }
        }
    </script>
    """, unsafe_allow_html=True)