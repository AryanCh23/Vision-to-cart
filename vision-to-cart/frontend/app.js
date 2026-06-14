/* =============================================
   Vision-to-Cart V4 — Frontend App Logic
   Communicates with FastAPI MCP Server via SSE
   ============================================= */

// Auto-detect environment:
//   Docker (served via nginx) → use /api/ proxy
//   Local file / dev         → use localhost:8000 directly
const API_BASE = (window.location.protocol === 'file:' || window.location.hostname === 'localhost' && window.location.port !== '3000')
  ? 'http://localhost:8000'
  : '/api';

let currentMode = 'text';
let currentSession = generateSessionId();
let imageBase64 = null;
let lastStyleDNA = null;
let lastMatches = [];
let appliedPromo = null;
let promoDiscountPercent = 0;

// ── Session ─────────────────────────────────────
function generateSessionId() {
  return 'sess' + Math.random().toString(36).substr(2, 9).toUpperCase();
}

function newSession() {
  currentSession = generateSessionId();
  document.getElementById('sessionIdDisplay').textContent = currentSession;
  imageBase64 = null;
  lastStyleDNA = null;
  // Reset UI
  hideResults();
  hidePipeline();
}

// ── Mode Switching ───────────────────────────────
function switchMode(mode) {
  currentMode = mode;
  document.getElementById('panelText').classList.toggle('hidden', mode !== 'text');
  document.getElementById('panelImage').classList.toggle('hidden', mode !== 'image');
  document.getElementById('tabText').classList.toggle('active', mode === 'text');
  document.getElementById('tabImage').classList.toggle('active', mode === 'image');
}

// ── Quick Query ──────────────────────────────────
function setQuery(text) {
  document.getElementById('textQuery').value = text;
  switchMode('text');
}

// ── Image Handling ───────────────────────────────
function handleDragOver(e) {
  e.preventDefault();
  document.getElementById('uploadZone').classList.add('drag-over');
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('uploadZone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) processImageFile(file);
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) processImageFile(file);
}

function processImageFile(file) {
  if (!file.type.startsWith('image/')) {
    alert('Please select a valid image file.');
    return;
  }
  const reader = new FileReader();
  reader.onload = (e) => {
    imageBase64 = e.target.result; // data:image/...;base64,...
    document.getElementById('previewImg').src = imageBase64;
    document.getElementById('uploadZone').classList.add('hidden');
    document.getElementById('imagePreview').classList.remove('hidden');
  };
  reader.readAsDataURL(file);
}

function clearImage() {
  imageBase64 = null;
  document.getElementById('previewImg').src = '';
  document.getElementById('fileInput').value = '';
  document.getElementById('imagePreview').classList.add('hidden');
  document.getElementById('uploadZone').classList.remove('hidden');
}

// ── Pipeline UI ──────────────────────────────────
const PIPELINE_STEPS = [
  { key: 'init',   label: 'Initializing pipeline', icon: '⚙️' },
  { key: 'input',  label: 'Processing input (NL / Vision)', icon: '🧠' },
  { key: 'search', label: 'Hybrid Vector Search', icon: '🔍' },
  { key: 'score',  label: '5-Component Scoring', icon: '📊' },
  { key: 'govern', label: 'Confidence Governance', icon: '🎯' },
  { key: 'recs',   label: 'Generating Recommendations', icon: '💡' },
];

function showPipeline() {
  const section = document.getElementById('pipelineSection');
  section.classList.remove('hidden');
  const track = document.getElementById('pipelineTrack');
  track.innerHTML = PIPELINE_STEPS.map((s, i) => `
    <div class="pipeline-step" id="pstep-${i}">
      <div class="step-indicator pending" id="pind-${i}">◦</div>
      <div>
        <div class="step-label">${s.icon} ${s.label}</div>
        <div class="step-sublabel" id="psub-${i}">Waiting...</div>
      </div>
    </div>
  `).join('');
}

function hidePipeline() {
  document.getElementById('pipelineSection').classList.add('hidden');
}

let currentStepIdx = -1;

function advanceStep(label, isComplete, isError) {
  // Find which step this event matches
  const lowerLabel = label.toLowerCase();
  let idx = -1;

  if (lowerLabel.includes('init')) idx = 0;
  else if (lowerLabel.includes('intent') || lowerLabel.includes('nl') || lowerLabel.includes('image') || lowerLabel.includes('input')) idx = 1;
  else if (lowerLabel.includes('retrieval') || lowerLabel.includes('search') || lowerLabel.includes('vector')) idx = 2;
  else if (lowerLabel.includes('scor')) idx = 3;
  else if (lowerLabel.includes('confidence') || lowerLabel.includes('govern')) idx = 4;
  else if (lowerLabel.includes('recommend')) idx = 5;

  if (idx >= 0) {
    const ind = document.getElementById(`pind-${idx}`);
    const sub = document.getElementById(`psub-${idx}`);
    const step = document.getElementById(`pstep-${idx}`);

    if (ind) {
      ind.className = `step-indicator ${isError ? 'error' : isComplete ? 'done' : 'running'}`;
      ind.textContent = isError ? '✕' : isComplete ? '✓' : '↻';
    }
    if (sub) sub.textContent = isComplete ? 'Complete' : isError ? 'Error' : 'Running…';
    if (step) {
      step.classList.remove('running', 'done', 'error');
      step.classList.add(isError ? 'error' : isComplete ? 'done' : 'running');
    }
  }
}

// ── Results UI ───────────────────────────────────
function hideResults() {
  document.getElementById('resultsSection').classList.add('hidden');
}

function renderResults(data) {
  const section = document.getElementById('resultsSection');
  section.classList.remove('hidden');
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Style DNA
  const dna = data.style_dna || {};
  lastStyleDNA = dna;
  const tags = document.getElementById('dnaTags');
  const dnaEntries = [
    ['Shape', dna.shape],
    ['Frame', dna.frame_color],
    ['Lens', dna.lens_color],
    ['Material', dna.frame_material],
    ['Gender', dna.gender],
    ['Brand', dna.brand_hint],
    ['Price Tier', dna.price_range_preference],
  ].filter(([, v]) => v);

  tags.innerHTML = dnaEntries.map(([k, v]) =>
    `<span class="dna-tag"><span>${k}:</span>${v}</span>`
  ).join('');

  // Confidence
  const tier = (data.confidence_tier || 'medium').toLowerCase();
  const badge = document.getElementById('confidenceBadge');
  badge.textContent = data.confidence_tier || 'Medium';
  badge.className = `confidence-badge ${tier}`;

  document.getElementById('governanceMsg').textContent = data.governance_message || '';

  // Products
  const matches = data.matches || [];
  lastMatches = matches;
  document.getElementById('resultsTitle').textContent =
    `🏆 Top ${matches.length} Match${matches.length !== 1 ? 'es' : ''}`;

  const grid = document.getElementById('productsGrid');
  grid.innerHTML = matches.map((m, i) => renderProductCard(m, i + 1)).join('');

  // Recommendations
  const recs = data.recommendations || {};
  renderRecList('recBudget', recs.budget);
  renderRecList('recPremium', recs.premium);
  renderRecList('recTrending', recs.trending);
}

function renderProductCard(match, rank) {
  const score = match.confidence_score || match.match_score || 0.7;
  const pct = Math.round(score * 100);
  const circumference = 2 * Math.PI * 18; // r=18
  const offset = circumference * (1 - score);
  const shapeEmoji = getShapeEmoji(match.shape || '');
  const scenarios = (match.scenario || []).slice(0, 2);
  const rating = match.rating || (4.0 + Math.random() * 0.9).toFixed(1);
  const reviews = match.review_count || Math.floor(80 + Math.random() * 200);
  const frameLensColor = [match.frame_color, match.lens_color].filter(Boolean);
  const swatchColors = { black: '#1a1a1a', gold: '#d4af37', silver: '#c0c0c0', brown: '#8b4513',
    tortoise: '#8b6914', blue: '#2563eb', pink: '#ec4899', red: '#dc2626', green: '#16a34a',
    grey: '#6b7280', clear: 'rgba(200,200,255,0.3)', rose: '#fb7185', white: '#f8fafc' };
  const colorDots = frameLensColor.map(c => {
    const lower = c.toLowerCase();
    const hex = Object.entries(swatchColors).find(([k]) => lower.includes(k))?.[1] || '#6b7280';
    return `<span class="color-swatch" style="background:${hex}" title="${c}"></span>`;
  }).join('');

  return `
    <div class="product-card" onclick="viewProductDetails('${match.product_id}')">
      <div class="product-img-area">
        <span class="product-rank-badge">#${rank} Match</span>
        ${scenarios.length ? `<span class="product-scenario-badge">${scenarios.join(' · ')}</span>` : ''}
        <div class="product-visual">${shapeEmoji}</div>
        <div class="score-ring">
          <svg width="48" height="48" viewBox="0 0 48 48">
            <circle class="bg-c" cx="24" cy="24" r="18"/>
            <circle class="fg-c" cx="24" cy="24" r="18"
              stroke-dasharray="${circumference.toFixed(1)}"
              stroke-dashoffset="${offset.toFixed(1)}"
              stroke="${scoreColor(score)}"
            />
          </svg>
          <div class="score-num">${pct}%</div>
        </div>
      </div>
      <div class="product-info">
        <div class="product-top-row">
          <div class="product-name">
            ${match.name || 'Unknown'}
            ${match.polarized ? '<span class="polarized-badge">⚡ POL</span>' : ''}
          </div>
        </div>
        <div class="product-brand-row">
          <span class="product-brand">${match.brand || ''}</span>
          <span class="product-rating">⭐ ${rating} <span>(${reviews})</span></span>
        </div>
        ${colorDots.length ? `<div class="product-swatches"><span class="swatch-label">Colors:</span>${colorDots}</div>` : ''}
        <div class="product-reason">${match.match_reason || ''}</div>
        <div class="product-tags">
          <span class="product-tag">${match.shape || 'classic'}</span>
          <span class="product-tag">${match.frame_material || 'acetate'}</span>
          ${match.uv_protection ? `<span class="product-tag">☀️ ${match.uv_protection}</span>` : ''}
          ${match.weight_grams ? `<span class="product-tag">${match.weight_grams}g</span>` : ''}
        </div>
        <div class="product-footer-row">
          <div>
            <div class="product-price">₹${(match.price || 0).toLocaleString('en-IN')}</div>
            ${match.warranty_years ? `<div class="price-old">${match.warranty_years}yr warranty</div>` : ''}
          </div>
          <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${match.product_id}', '${(match.name||'').replace(/'/g,"\\'")}')">
            🛒 Add
          </button>
        </div>
      </div>
    </div>
  `;
}

function renderRecList(elemId, items) {
  const el = document.getElementById(elemId);
  if (!items || items.length === 0) {
    el.innerHTML = '<div class="rec-item"><span class="rec-item-name" style="color:var(--text-muted)">None available</span></div>';
    return;
  }
  el.innerHTML = items.map(r => `
    <div class="rec-item" style="cursor: pointer;" onclick="viewProductDetails('${r.product_id || 'P001'}')">
      <span class="rec-item-name">${r.name || r}</span>
      ${r.price ? `<span class="rec-item-price">₹${r.price.toLocaleString('en-IN')}</span>` : ''}
    </div>
  `).join('');
}


// ── PDP/Cart Action UI ────────────────────────────
function toggleCart() {
  const sidebar = document.getElementById('cartSidebar');
  const overlay = document.getElementById('cartOverlay');
  const isOpen = sidebar.classList.toggle('open');
  sidebar.classList.toggle('hidden', !isOpen);
  overlay.classList.toggle('hidden', !isOpen);
}

function openCart() {
  const sidebar = document.getElementById('cartSidebar');
  const overlay = document.getElementById('cartOverlay');
  sidebar.classList.add('open');
  sidebar.classList.remove('hidden');
  overlay.classList.remove('hidden');
}

function closeModal() {
  document.getElementById('modalOverlay').classList.add('hidden');
}

async function viewProductDetails(productId) {
  const modalOverlay = document.getElementById('modalOverlay');
  const modalContent = document.getElementById('modalContent');
  
  modalContent.innerHTML = `<div style="text-align:center; padding: 60px;"><span class="loader-dots">Analyzing PDP Specifications</span></div>`;
  modalOverlay.classList.remove('hidden');
  
  let product = null;
  try {
    const isOnline = await checkServer();
    if (isOnline) {
      const res = await fetch(`${API_BASE}/products/${productId}`);
      if (res.ok) {
        const payload = await res.json();
        product = payload.data;
      }
    }
  } catch (err) {
    console.error('Failed to fetch product PDP details:', err);
  }
  
  // Construct fallback if server offline
  if (!product) {
    product = {
      product_id: productId,
      name: "Designer Sunglasses Model " + productId,
      brand: "Premium Design",
      shape: "wayfarer",
      price: 8900,
      polarized: true,
      uv_protection: "UV400",
      frame_material: "acetate",
      lens_technology: "Standard Tint",
      weight_grams: 30,
      warranty_years: 2,
      description: "Elegant polarized eyewear crafted with maximum comfort and UV400 standard coverage.",
      rating: 4.8,
      review_count: 156,
      face_shape_fit: ["oval", "round", "heart"],
      scenario: ["everyday", "fashion"]
    };
  }
  
  const shapeEmoji = getShapeEmoji(product.shape || '');
  
  modalContent.innerHTML = `
    <div class="modal-hero">
      <div class="modal-hero-emoji">${shapeEmoji}</div>
    </div>
    <div class="modal-body">
      <h2 class="modal-name">${product.name}</h2>
      <div class="modal-brand-row">
        <span class="modal-brand">${product.brand}</span>
        <div class="modal-rating">
          ⭐ ${product.rating || '4.5'} <span class="review-count">(${product.review_count || '120'} reviews)</span>
        </div>
      </div>
      
      <div class="modal-price-row">
        <div class="modal-price">₹${(product.price || 0).toLocaleString('en-IN')}</div>
        <button class="modal-cart-btn" onclick="addCartFromModal('${product.product_id}', this)">
          <span>🛒</span> <span class="btn-text">Add to Cart</span>
        </button>
      </div>
      
      <div class="modal-sections">
        <div>
          <div class="modal-section-title">Description</div>
          <p class="modal-description">${product.description || 'No description available.'}</p>
        </div>
        
        <div>
          <div class="modal-section-title">Specifications</div>
          <div class="modal-specs-grid">
            <div class="spec-item">
              <div class="spec-label">Shape</div>
              <div class="spec-value">${product.shape || 'Classic'}</div>
            </div>
            <div class="spec-item">
              <div class="spec-label">Polarized</div>
              <div class="spec-value ${product.polarized ? 'highlight' : ''}">${product.polarized ? 'Yes' : 'No'}</div>
            </div>
            <div class="spec-item">
              <div class="spec-label">UV Protection</div>
              <div class="spec-value highlight">${product.uv_protection || 'UV400'}</div>
            </div>
            <div class="spec-item">
              <div class="spec-label">Material</div>
              <div class="spec-value">${product.frame_material || 'Acetate'}</div>
            </div>
            <div class="spec-item">
              <div class="spec-label">Lens Tech</div>
              <div class="spec-value">${product.lens_technology || 'Standard'}</div>
            </div>
            <div class="spec-item">
              <div class="spec-label">Weight</div>
              <div class="spec-value">${product.weight_grams ? product.weight_grams + 'g' : '30g'}</div>
            </div>
          </div>
        </div>
        
        ${product.celebrity_worn ? `
        <div>
          <div class="modal-section-title">Celebrity Style</div>
          <div class="celebrity-badge">
            😎 Worn by: ${product.celebrity_worn}
          </div>
        </div>
        ` : ''}
        
        <div>
          <div class="modal-section-title">Best Fit Face Shapes</div>
          <div class="face-shape-tags">
            ${(product.face_shape_fit || ["Oval", "Square"]).map(f => `<span class="face-shape-tag">${f}</span>`).join('')}
          </div>
        </div>
        
        <div>
          <div class="modal-section-title">Scenarios</div>
          <div class="scenario-tags">
            ${(product.scenario || ["everyday"]).map(s => `<span class="scenario-chip" style="cursor:pointer;" onclick="closeModal(); searchScenario('${s}', '')">${s}</span>`).join('')}
          </div>
        </div>
        
        <div class="warranty-row" style="margin-top:16px;">
          <span class="warranty-check">✓</span> <span>${product.warranty_years || 1} Year Warranty included</span>
        </div>
      </div>
    </div>
  `;
}

async function addCartFromModal(productId, btn) {
  btn.classList.add('added');
  const btnText = btn.querySelector('.btn-text');
  if (btnText) btnText.textContent = 'Added to Cart!';
  
  await addToCart(productId);
  
  setTimeout(() => {
    btn.classList.remove('added');
    if (btnText) btnText.textContent = 'Add to Cart';
  }, 2500);
}

function syncCartUI(cartData) {
  document.getElementById('cartCount').textContent = cartData.cart_count || 0;
  const cartItems = document.getElementById('cartItems');
  const cartFooter = document.getElementById('cartFooter');
  
  if (!cartData.cart || cartData.cart.length === 0) {
    cartItems.innerHTML = `
      <div class="cart-empty">
        <div class="cart-empty-icon">🕶️</div>
        <p>Your cart is empty</p>
        <p class="cart-empty-sub">Start searching to add sunglasses</p>
      </div>
    `;
    cartFooter.classList.add('hidden');
    
    const progressText = document.getElementById('shippingProgressText');
    const progressBar = document.getElementById('shippingProgressBar');
    if (progressText) progressText.textContent = 'Add items to qualify for Free Shipping!';
    if (progressBar) progressBar.style.width = '0%';
    return;
  }
  
  cartItems.innerHTML = cartData.cart.map(item => {
    const shapeEmoji = getShapeEmoji(item.shape || '');
    return `
      <div class="cart-item-card">
        <div class="cart-item-emoji">${shapeEmoji}</div>
        <div class="cart-item-info">
          <div class="cart-item-name">${item.name}</div>
          <div class="cart-item-brand">${item.brand}</div>
          <div class="cart-item-price">₹${item.price.toLocaleString('en-IN')}</div>
          <div class="cart-item-details" style="font-size: 0.72rem; color: var(--text-secondary); margin-top: 6px; line-height: 1.4; border-top: 1px solid rgba(255,255,255,0.04); padding-top: 4px;">
            <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:2px;">
              <span style="background:rgba(255,255,255,0.05); padding:1px 5px; border-radius:3px;">${item.shape || 'classic'}</span>
              <span style="background:rgba(255,255,255,0.05); padding:1px 5px; border-radius:3px;">${item.frame_material || 'acetate'}</span>
              ${item.polarized ? '<span style="color:var(--accent-3); background:rgba(6,182,212,0.08); padding:1px 5px; border-radius:3px;">✨ Polarized</span>' : ''}
              <span style="background:rgba(255,255,255,0.05); padding:1px 5px; border-radius:3px;">☀️ ${item.uv_protection || 'UV400'}</span>
            </div>
            <div>Weight: ${item.weight_grams || 30}g · Warranty: ${item.warranty_years || 2} Yr${item.warranty_years !== 1 ? 's' : ''}</div>
            <div style="color: #4ade80; font-weight: 500; margin-top:2px;">🚚 Express Delivery in 2 Days</div>
            ${item.celebrity_worn ? `<div style="color:var(--accent-gold); font-weight: 500; margin-top:2px;">⭐ Worn by: ${item.celebrity_worn}</div>` : ''}
          </div>
        </div>
        <button class="cart-item-remove" onclick="removeFromCart('${item.product_id}')">✕</button>
      </div>
    `;
  }).join('');
  
  const subtotal = cartData.cart.reduce((sum, item) => sum + (item.price || 0), 0);
  const discount = appliedPromo ? Math.round(subtotal * promoDiscountPercent) : 0;
  const threshold = 15000;
  const shipping = (subtotal - discount) >= threshold ? 0 : 150;
  const total = subtotal - discount + shipping;

  document.getElementById('cartSubtotal').textContent = `₹${subtotal.toLocaleString('en-IN')}`;
  
  const discountRow = document.getElementById('cartDiscountRow');
  if (discount > 0) {
    discountRow.classList.remove('hidden');
    document.getElementById('cartDiscount').textContent = `-₹${discount.toLocaleString('en-IN')}`;
  } else {
    discountRow.classList.add('hidden');
  }

  document.getElementById('cartShipping').textContent = shipping === 0 ? 'FREE' : `₹${shipping}`;
  document.getElementById('cartTotal').textContent = `₹${total.toLocaleString('en-IN')}`;
  
  const netSubtotal = subtotal - discount;
  const percentage = Math.min(100, (netSubtotal / threshold) * 100);
  const progressBar = document.getElementById('shippingProgressBar');
  const progressText = document.getElementById('shippingProgressText');
  
  if (progressBar) progressBar.style.width = `${percentage}%`;
  if (progressText) {
    if (netSubtotal >= threshold) {
      progressText.innerHTML = '🎉 You qualify for <strong style="color:#4ade80">Free Express Shipping</strong>!';
    } else {
      const remaining = threshold - netSubtotal;
      progressText.innerHTML = `Add <strong style="color:var(--accent-3)">₹${remaining.toLocaleString('en-IN')}</strong> more for Free Shipping!`;
    }
  }

  cartFooter.classList.remove('hidden');
}

function applyPromoCode() {
  const input = document.getElementById('cartPromoInput');
  const msg = document.getElementById('cartPromoMessage');
  const code = input.value.trim().toUpperCase();
  
  if (code === 'HACKATHON') {
    appliedPromo = 'HACKATHON';
    promoDiscountPercent = 0.10;
    msg.textContent = 'Coupon applied! 10% Discount applied.';
    msg.className = 'cart-promo-message success';
    loadCart();
  } else if (code === '') {
    appliedPromo = null;
    promoDiscountPercent = 0;
    msg.textContent = '';
    msg.className = 'cart-promo-message';
    loadCart();
  } else {
    msg.textContent = 'Invalid promo code. Try HACKATHON';
    msg.className = 'cart-promo-message error';
  }
}

async function loadCart() {
  try {
    const isOnline = await checkServer();
    if (isOnline) {
      const res = await fetch(`${API_BASE}/cart?session_id=${currentSession}`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'success') {
          syncCartUI(data);
          return;
        }
      }
    }
  } catch (err) {
    console.error('Failed to load cart from API:', err);
  }
  
  // Local fallback
  const localCart = JSON.parse(localStorage.getItem(`cart_${currentSession}`) || '[]');
  const count = localCart.length;
  const total = localCart.reduce((sum, item) => sum + (item.price || 0), 0);
  syncCartUI({ cart: localCart, cart_count: count, total_price: total });
}

async function addToCart(productId, name) {
  const btn = event ? event.target : null;
  if (btn && btn.classList.contains('btn-add-cart')) {
    btn.textContent = '✓ Added!';
    btn.style.background = 'linear-gradient(135deg,#4ade80,#22c55e)';
    setTimeout(() => {
      btn.textContent = 'Add to Cart 🛒';
      btn.style.background = '';
    }, 2000);
  }

  try {
    const isOnline = await checkServer();
    if (isOnline) {
      const res = await fetch(`${API_BASE}/cart/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: currentSession, product_id: productId })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'success') {
          syncCartUI(data);
          openCart();
          return;
        }
      }
    }
  } catch (err) {
    console.error('Failed to add to cart on API:', err);
  }

  // Local fallback cache
  let localCart = JSON.parse(localStorage.getItem(`cart_${currentSession}`) || '[]');
  let product = null;

  // Try finding in lastMatches first
  if (lastMatches && lastMatches.length > 0) {
    product = lastMatches.find(m => m.product_id === productId);
  }
  
  // Try finding details in UI grid
  if (!product) {
    const cardElements = document.querySelectorAll('.product-card');
    for (const card of cardElements) {
      const nameEl = card.querySelector('.product-name');
      const priceEl = card.querySelector('.product-price');
      const brandEl = card.querySelector('.product-brand');
      if (nameEl && (nameEl.textContent === name || card.getAttribute('onclick')?.includes(productId))) {
        const priceVal = parseInt(priceEl?.textContent.replace(/[^\d]/g, '') || '5000');
        product = {
          product_id: productId,
          name: nameEl.textContent,
          brand: brandEl?.textContent || 'Premium Brand',
          price: priceVal,
          shape: 'aviator',
          polarized: true,
          uv_protection: 'UV400',
          frame_material: 'metal',
          weight_grams: 28,
          warranty_years: 2
        };
        break;
      }
    }
  }

  if (!product) {
    product = {
      product_id: productId,
      name: name || 'Sunglasses Model',
      brand: 'Premium Design',
      price: 7500,
      shape: 'wayfarer',
      polarized: true,
      uv_protection: 'UV400',
      frame_material: 'acetate',
      weight_grams: 30,
      warranty_years: 2
    };
  }

  localCart.push(product);
  localStorage.setItem(`cart_${currentSession}`, JSON.stringify(localCart));
  
  const count = localCart.length;
  const total = localCart.reduce((sum, item) => sum + (item.price || 0), 0);
  syncCartUI({ cart: localCart, cart_count: count, total_price: total });
  openCart();
}

async function removeFromCart(productId) {
  try {
    const isOnline = await checkServer();
    if (isOnline) {
      const res = await fetch(`${API_BASE}/cart/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: currentSession, product_id: productId })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'success') {
          syncCartUI(data);
          return;
        }
      }
    }
  } catch (err) {
    console.error('Failed to remove from cart on API:', err);
  }

  // Local fallback
  let localCart = JSON.parse(localStorage.getItem(`cart_${currentSession}`) || '[]');
  localCart = localCart.filter(item => item.product_id !== productId);
  localStorage.setItem(`cart_${currentSession}`, JSON.stringify(localCart));

  const count = localCart.length;
  const total = localCart.reduce((sum, item) => sum + (item.price || 0), 0);
  syncCartUI({ cart: localCart, cart_count: count, total_price: total });
}

async function checkout() {
  try {
    const isOnline = await checkServer();
    if (isOnline) {
      await fetch(`${API_BASE}/cart/clear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: currentSession })
      });
    }
  } catch (err) {
    console.error('Failed to checkout on API:', err);
  }

  localStorage.removeItem(`cart_${currentSession}`);
  syncCartUI({ cart: [], cart_count: 0, total_price: 0 });
  toggleCart();
  
  showCheckoutSuccess();
}

function showCheckoutSuccess() {
  const overlay = document.createElement('div');
  overlay.style.position = 'fixed';
  overlay.style.inset = '0';
  overlay.style.background = 'rgba(0, 0, 0, 0.8)';
  overlay.style.zIndex = '500';
  overlay.style.display = 'flex';
  overlay.style.alignItems = 'center';
  overlay.style.justifyContent = 'center';
  overlay.style.backdropFilter = 'blur(12px)';
  overlay.style.animation = 'fadeIn 0.2s ease-out';
  
  overlay.innerHTML = `
    <div style="
      background: var(--bg-card2, #111827);
      border: 1px solid var(--border, rgba(255,255,255,0.08));
      border-radius: 24px;
      padding: 40px;
      text-align: center;
      max-width: 440px;
      width: 90%;
      box-shadow: 0 40px 100px rgba(0,0,0,0.8), 0 0 40px rgba(99,102,241,0.25);
    ">
      <div style="font-size: 4.5rem; margin-bottom: 20px;">🎉</div>
      <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 800; margin-bottom: 12px; background: linear-gradient(135deg, #a5b4fc, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Order Placed!</h3>
      <p style="color: var(--text-secondary, #9ca3af); font-size: 0.95rem; line-height: 1.6; margin-bottom: 30px;">Your order has been routed through our MCP pipeline successfully. Thank you for shopping with Vision-to-Cart!</p>
      <button onclick="this.parentElement.parentElement.remove()" style="
        background: linear-gradient(135deg, var(--accent-1, #6366f1), var(--accent-2, #4f46e5));
        border: none;
        color: white;
        padding: 12px 36px;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 16px rgba(99,102,241,0.4);
        transition: all 0.2s;
      ">Continue Discovery</button>
    </div>
  `;
  document.body.appendChild(overlay);
}

async function searchScenario(scenarioKey, emoji) {
  let query = '';
  switch (scenarioKey) {
    case 'beach':
      query = 'Polarized sunglasses with UV400 protection for beach and sunny summer vacation';
      break;
    case 'driving':
      query = 'Anti-glare driving sunglasses with polarized lenses for clear highway vision';
      break;
    case 'sports':
      query = 'Wraparound impact resistant sports sunglasses for running or cycling';
      break;
    case 'fashion':
      query = 'Luxury fashion sunglasses from premium designer brands like Gucci, Tom Ford or Prada';
      break;
    case 'office':
      query = 'Refined professional sunglasses with subtle frames for office everyday wear';
      break;
    case 'outdoor':
      query = 'Full coverage hiking sunglasses with high altitude UV protection';
      break;
    case 'festival':
      query = 'Bold tinted retro sunglasses and statement festival party glasses';
      break;
    case 'travel':
      query = 'Lightweight packable travel vacation resort sunglasses';
      break;
    case 'luxury':
      query = 'High-end luxury premium craft statement eyewear Cartier';
      break;
    case 'everyday':
      query = 'Comfortable daily wear classic sunglasses with wayfarer or round frame shapes';
      break;
    case 'water':
      query = 'Water sports surfing marine grade polarized sunglasses';
      break;
    default:
      query = `Sunglasses for ${scenarioKey}`;
  }

  document.getElementById('textQuery').value = query;
  switchMode('text');
  
  const cards = document.querySelectorAll('.scenario-card');
  cards.forEach(c => c.classList.remove('active'));
  const activeCard = document.getElementById(`sc-${scenarioKey}`);
  if (activeCard) activeCard.classList.add('active');
  
  document.getElementById('search').scrollIntoView({ behavior: 'smooth', block: 'center' });
  await runSearch();
}

// ── Main Search ──────────────────────────────────
async function runSearch() {
  const btn = document.getElementById('searchBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="loader-dots">Searching</span>';

  const payload = buildPayload();
  if (!payload) {
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon-inner">🔍</span><span>Search</span>';
    return;
  }

  hideResults();
  showPipeline();
  currentStepIdx = -1;

  try {
    // Try real server first; fallback to mock if offline
    const online = await checkServer();
    if (online) {
      await runSSESearch(payload);
    } else {
      await runMockSearch(payload);
    }
  } catch (err) {
    console.error('Search failed:', err);
    await runMockSearch(payload);
  }

  btn.disabled = false;
  btn.innerHTML = '<span class="btn-icon-inner">🔍</span><span>Search</span>';
}

function buildPayload() {
  if (currentMode === 'text') {
    const q = document.getElementById('textQuery').value.trim();
    if (!q) { alert('Please enter a search query.'); return null; }
    return { session_id: currentSession, input_type: 'text', text_query: q };
  } else {
    if (!imageBase64) { alert('Please upload an image first.'); return null; }
    return { session_id: currentSession, input_type: 'image', image_base64: imageBase64 };
  }
}

async function checkServer() {
  try {
    const res = await fetch(`${API_BASE}/`, { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch { return false; }
}

async function runSSESearch(payload) {
  const response = await fetch(`${API_BASE}/mcp/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n\n');
    buffer = lines.pop();

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const event = JSON.parse(line.slice(6));
          handleEvent(event);
        } catch { /* skip malformed */ }
      }
    }
  }
}

function handleEvent(event) {
  const { event_type, label, data } = event;

  if (event_type === 'step_start') {
    advanceStep(label, false, false);
  } else if (event_type === 'step_complete') {
    advanceStep(label, true, false);
  } else if (event_type === 'result_ready') {
    // Mark all done
    PIPELINE_STEPS.forEach((_, i) => {
      const ind = document.getElementById(`pind-${i}`);
      const step = document.getElementById(`pstep-${i}`);
      if (ind) { ind.className = 'step-indicator done'; ind.textContent = '✓'; }
      if (step) { step.classList.remove('running'); step.classList.add('done'); }
    });
    setTimeout(() => renderResults(data), 400);
  } else if (event_type === 'error') {
    advanceStep(label, false, true);
  }
}

// ── Mock Fallback ────────────────────────────────
async function runMockSearch(payload) {
  const steps = [
    { label: 'init', delay: 300 },
    { label: 'nl', delay: 600 },
    { label: 'retrieval', delay: 900 },
    { label: 'scor', delay: 700 },
    { label: 'confidence', delay: 400 },
    { label: 'recommend', delay: 500 },
  ];

  for (const s of steps) {
    advanceStep(s.label, false, false);
    await sleep(s.delay);
    advanceStep(s.label, true, false);
  }

  await sleep(300);

  const query = (payload.text_query || '').toLowerCase();
  const mockData = getMockResults(query);
  renderResults(mockData);
}

function getMockResults(query) {
  // Intelligent mock based on keywords
  let shape = 'wayfarer', brand = 'Ray-Ban', color = 'black';
  let matches = [];

  if (query.includes('aviator') || query.includes('top gun') || query.includes('skyfall') || query.includes('james bond')) {
    shape = 'aviator'; brand = 'Ray-Ban'; color = 'gold';
    matches = [
      { product_id: 'P001', name: 'Classic Gold Aviator', brand: 'Ray-Ban', price: 7500, shape: 'aviator', polarized: true, uv_protection: 'UV400', frame_material: 'metal', weight_grams: 26, warranty_years: 2, celebrity_worn: 'Tom Cruise', scenario: ['beach', 'driving', 'travel'], confidence_score: 0.92, match_reason: 'Iconic aviator shape, gold metal frame, polarized — exactly like Top Gun' },
      { product_id: 'P002', name: 'Titanium Premium Aviator', brand: 'Maui Jim', price: 21000, shape: 'aviator', polarized: true, uv_protection: 'UV400+', frame_material: 'titanium', weight_grams: 20, warranty_years: 3, celebrity_worn: 'George Clooney', scenario: ['luxury', 'travel', 'everyday'], confidence_score: 0.78, match_reason: 'Lightweight titanium, premium polarized lenses' },
      { product_id: 'P003', name: 'Budget Aviator Classic', brand: 'Lenskart', price: 1500, shape: 'aviator', polarized: false, uv_protection: 'UV400', frame_material: 'alloy', weight_grams: 32, warranty_years: 1, scenario: ['everyday', 'driving'], confidence_score: 0.59, match_reason: 'Classic aviator shape — great budget pick' },
    ];
  } else if (query.includes('oakley') || query.includes('sport') || query.includes('running') || query.includes('cycling') || query.includes('active')) {
    shape = 'sport'; brand = 'Oakley'; color = 'blue';
    matches = [
      { product_id: 'P010', name: 'Radar EV Path Sport', brand: 'Oakley', price: 14500, shape: 'sport', polarized: true, uv_protection: 'UV400', frame_material: 'o-matter', weight_grams: 24, warranty_years: 2, scenario: ['sports', 'outdoor', 'cycling'], confidence_score: 0.89, match_reason: 'Wraparound sport fit, blue Prizm lens, impact-resistant O-Matter frame' },
      { product_id: 'P011', name: 'Sutro Shield Sport', brand: 'Oakley', price: 12500, shape: 'sport', polarized: false, uv_protection: 'UV400', frame_material: 'o-matter', weight_grams: 28, warranty_years: 2, scenario: ['sports', 'outdoor'], confidence_score: 0.73, match_reason: 'Shield design, maximum coverage for running' },
      { product_id: 'P012', name: 'Active Sport Budget', brand: 'Decathlon', price: 1200, shape: 'sport', polarized: false, uv_protection: 'UV380', frame_material: 'nylon', weight_grams: 30, warranty_years: 1, scenario: ['sports', 'outdoor'], confidence_score: 0.55, match_reason: 'Affordable sport sunglasses for casual active use' },
    ];
  } else if (query.includes('cat') || query.includes('women') || query.includes('feminine') || query.includes('fashion') || query.includes('gucci') || query.includes('prada') || query.includes('luxury')) {
    shape = 'cat-eye'; brand = 'Gucci'; color = 'tortoise';
    matches = [
      { product_id: 'P041', name: 'Gucci Glamour Cat-Eye', brand: 'Gucci', price: 42000, shape: 'cat-eye', polarized: false, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 34, warranty_years: 2, celebrity_worn: 'Priyanka Chopra', scenario: ['fashion', 'luxury', 'festival'], confidence_score: 0.91, match_reason: 'High-fashion cat-eye, acetate frame, runway-ready style' },
      { product_id: 'P020', name: 'Retro Cat-Eye Tortoise', brand: 'Fastrack', price: 1499, shape: 'cat-eye', polarized: false, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 28, warranty_years: 1, scenario: ['fashion', 'everyday'], confidence_score: 0.77, match_reason: 'Classic cat-eye, tortoise finish, affordable fashion' },
      { product_id: 'P021', name: 'Oversized Acetate Cat-Eye', brand: 'Vogue', price: 5200, shape: 'oversized', polarized: false, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 36, warranty_years: 1, celebrity_worn: 'Deepika Padukone', scenario: ['fashion', 'travel'], confidence_score: 0.64, match_reason: 'Oversized cat-eye frame, statement fashion look' },
    ];
  } else if (query.includes('beach') || query.includes('summer') || query.includes('polarized') || query.includes('uv')) {
    shape = 'wayfarer'; brand = 'Ray-Ban'; color = 'black';
    matches = [
      { product_id: 'P030', name: 'Wayfarer Stealth Black', brand: 'Ray-Ban', price: 6800, shape: 'wayfarer', polarized: true, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 30, warranty_years: 2, celebrity_worn: 'Ranveer Singh', scenario: ['beach', 'everyday', 'travel'], confidence_score: 0.86, match_reason: 'Polarized UV400 protection, iconic wayfarer for beach' },
      { product_id: 'P001', name: 'Classic Gold Aviator', brand: 'Ray-Ban', price: 7500, shape: 'aviator', polarized: true, uv_protection: 'UV400', frame_material: 'metal', weight_grams: 26, warranty_years: 2, scenario: ['beach', 'driving'], confidence_score: 0.73, match_reason: 'Polarized aviator, perfect beach companion' },
      { product_id: 'P002', name: 'Titanium Premium Aviator', brand: 'Maui Jim', price: 21000, shape: 'aviator', polarized: true, uv_protection: 'UV400+', frame_material: 'titanium', weight_grams: 20, warranty_years: 3, scenario: ['beach', 'luxury'], confidence_score: 0.61, match_reason: 'Ultra-premium polarized titanium, best UV block' },
    ];
  } else if (query.includes('festival') || query.includes('party') || query.includes('bold') || query.includes('retro')) {
    shape = 'round'; brand = 'Quay'; color = 'pink';
    matches = [
      { product_id: 'P041', name: 'VibeCheck Festival Round', brand: 'Quay Australia', price: 4200, shape: 'round', polarized: false, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 22, warranty_years: 1, scenario: ['festival', 'fashion', 'party'], confidence_score: 0.87, match_reason: 'Bold colored lenses, festival-ready round frame' },
      { product_id: 'P022', name: 'Bold Cat-Eye Statement', brand: 'Titan', price: 2100, shape: 'cat-eye', polarized: false, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 28, warranty_years: 1, scenario: ['festival', 'fashion'], confidence_score: 0.69, match_reason: 'Statement cat-eye, perfect for events' },
      { product_id: 'P032', name: 'Round Vintage Gold', brand: 'Lenskart', price: 1299, shape: 'round', polarized: false, uv_protection: 'UV380', frame_material: 'metal', weight_grams: 22, warranty_years: 1, scenario: ['festival', 'everyday'], confidence_score: 0.54, match_reason: 'Budget retro round frames, festival vibe' },
    ];
  } else if (query.includes('hiking') || query.includes('outdoor') || query.includes('trekking') || query.includes('mountain')) {
    shape = 'sport'; brand = 'Julbo'; color = 'grey';
    matches = [
      { product_id: 'P043', name: 'Summit Trail Shield', brand: 'Julbo', price: 9800, shape: 'sport', polarized: true, uv_protection: 'UV400 Cat 4', frame_material: 'nylon', weight_grams: 22, warranty_years: 2, scenario: ['outdoor', 'sports', 'hiking'], confidence_score: 0.90, match_reason: 'Category 4 UV, full coverage, ideal for high altitude trekking' },
      { product_id: 'P010', name: 'Radar EV Path Sport', brand: 'Oakley', price: 14500, shape: 'sport', polarized: true, uv_protection: 'UV400', frame_material: 'o-matter', weight_grams: 24, warranty_years: 2, scenario: ['outdoor', 'sports'], confidence_score: 0.72, match_reason: 'Wraparound, durable, high-performance outdoor sports' },
      { product_id: 'P011', name: 'Sutro Shield Sport', brand: 'Oakley', price: 12500, shape: 'sport', polarized: false, uv_protection: 'UV400', frame_material: 'o-matter', weight_grams: 28, warranty_years: 2, scenario: ['outdoor', 'sports'], confidence_score: 0.58, match_reason: 'Full shield, max coverage for outdoor activities' },
    ];
  } else if (query.includes('travel') || query.includes('vacation') || query.includes('resort') || query.includes('packable') || query.includes('lightweight')) {
    shape = 'wayfarer'; brand = 'Ray-Ban'; color = 'brown';
    matches = [
      { product_id: 'P030', name: 'Wayfarer Stealth Black', brand: 'Ray-Ban', price: 6800, shape: 'wayfarer', polarized: true, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 30, warranty_years: 2, celebrity_worn: 'Ranveer Singh', scenario: ['travel', 'beach', 'everyday'], confidence_score: 0.87, match_reason: 'Iconic packable wayfarer, polarized for all-day travel comfort' },
      { product_id: 'P002', name: 'Titanium Premium Aviator', brand: 'Maui Jim', price: 21000, shape: 'aviator', polarized: true, uv_protection: 'UV400+', frame_material: 'titanium', weight_grams: 20, warranty_years: 3, scenario: ['travel', 'luxury'], confidence_score: 0.74, match_reason: 'Ultra-lightweight 20g titanium frame, ideal for long-haul travel' },
      { product_id: 'P045', name: 'AquaShield Water Sports', brand: 'Costa Del Mar', price: 6800, shape: 'sport', polarized: true, uv_protection: 'UV400 Marine', frame_material: 'nylon', weight_grams: 22, warranty_years: 2, scenario: ['travel', 'beach', 'outdoor'], confidence_score: 0.61, match_reason: 'Marine-grade polarized, perfect for beach resorts and water activities' },
    ];
  } else if (query.includes('water') || query.includes('swimming') || query.includes('snorkeling') || query.includes('surfing') || query.includes('marine')) {
    shape = 'sport'; brand = 'Costa Del Mar'; color = 'blue';
    matches = [
      { product_id: 'P045', name: 'AquaShield Water Sports', brand: 'Costa Del Mar', price: 6800, shape: 'sport', polarized: true, uv_protection: 'UV400 Marine', frame_material: 'nylon', weight_grams: 22, warranty_years: 2, scenario: ['outdoor', 'beach', 'sports'], confidence_score: 0.93, match_reason: 'Marine-grade polarization, floating frame, purpose-built for water sports' },
      { product_id: 'P010', name: 'Radar EV Path Sport', brand: 'Oakley', price: 14500, shape: 'sport', polarized: true, uv_protection: 'UV400', frame_material: 'o-matter', weight_grams: 24, warranty_years: 2, scenario: ['sports', 'outdoor'], confidence_score: 0.68, match_reason: 'Impact-resistant, great for active water sports' },
      { product_id: 'P043', name: 'Summit Trail Shield', brand: 'Julbo', price: 9800, shape: 'sport', polarized: true, uv_protection: 'UV400 Cat 4', frame_material: 'nylon', weight_grams: 22, warranty_years: 2, scenario: ['outdoor', 'sports'], confidence_score: 0.54, match_reason: 'High UV protection, durable, suitable for extreme water environments' },
    ];
  } else if (query.includes('luxury') || query.includes('cartier') || query.includes('tom ford') || query.includes('high-end') || query.includes('premium craft')) {
    shape = 'square'; brand = 'Cartier'; color = 'gold';
    matches = [
      { product_id: 'P041', name: 'Gucci Glamour Cat-Eye', brand: 'Gucci', price: 42000, shape: 'cat-eye', polarized: false, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 34, warranty_years: 2, celebrity_worn: 'Priyanka Chopra', scenario: ['luxury', 'fashion'], confidence_score: 0.91, match_reason: 'Runway-level luxury, Italian craftsmanship, worn by global celebrities' },
      { product_id: 'P002', name: 'Titanium Premium Aviator', brand: 'Maui Jim', price: 21000, shape: 'aviator', polarized: true, uv_protection: 'UV400+', frame_material: 'titanium', weight_grams: 20, warranty_years: 3, celebrity_worn: 'George Clooney', scenario: ['luxury', 'everyday'], confidence_score: 0.79, match_reason: 'Premium titanium, legendary optical clarity, ultra-premium feel' },
      { product_id: 'P044', name: 'Executive Square Matte', brand: 'Hugo Boss', price: 14500, shape: 'square', polarized: true, uv_protection: 'UV400', frame_material: 'titanium', weight_grams: 24, warranty_years: 3, scenario: ['luxury', 'office'], confidence_score: 0.63, match_reason: 'Executive titanium square frame, precision German engineering' },
    ];
  } else if (query.includes('office') || query.includes('professional') || query.includes('work') || query.includes('subtle')) {
    shape = 'square'; brand = 'Boss'; color = 'black';
    matches = [
      { product_id: 'P044', name: 'Executive Square Matte', brand: 'Hugo Boss', price: 14500, shape: 'square', polarized: true, uv_protection: 'UV400', frame_material: 'titanium', weight_grams: 24, warranty_years: 3, scenario: ['office', 'everyday', 'driving'], confidence_score: 0.88, match_reason: 'Refined matte square frame, professional look for office and commute' },
      { product_id: 'P031', name: 'Clubmaster Classic', brand: 'Ray-Ban', price: 8900, shape: 'clubmaster', polarized: true, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 32, warranty_years: 2, scenario: ['everyday', 'office'], confidence_score: 0.69, match_reason: 'Classic clubmaster, polished professional aesthetic' },
      { product_id: 'P030', name: 'Wayfarer Stealth Black', brand: 'Ray-Ban', price: 6800, shape: 'wayfarer', polarized: true, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 30, warranty_years: 2, scenario: ['everyday', 'office'], confidence_score: 0.55, match_reason: 'Understated classic, suitable for professional environments' },
    ];
  } else if (query.includes('driving') || query.includes('anti-glare') || query.includes('highway')) {
    shape = 'aviator'; brand = 'Polaroid'; color = 'brown';
    matches = [
      { product_id: 'P042', name: 'DriveMaster Pro Polarized', brand: 'Polaroid', price: 3200, shape: 'aviator', polarized: true, uv_protection: 'UV400', frame_material: 'metal', weight_grams: 26, warranty_years: 2, scenario: ['driving', 'everyday', 'travel'], confidence_score: 0.91, match_reason: 'HD polarized lenses eliminate road glare, designed for driving' },
      { product_id: 'P001', name: 'Classic Gold Aviator', brand: 'Ray-Ban', price: 7500, shape: 'aviator', polarized: true, uv_protection: 'UV400', frame_material: 'metal', weight_grams: 26, warranty_years: 2, scenario: ['driving', 'beach'], confidence_score: 0.78, match_reason: 'Polarized aviator, classic choice for drivers' },
      { product_id: 'P044', name: 'Executive Square Matte', brand: 'Hugo Boss', price: 14500, shape: 'square', polarized: true, uv_protection: 'UV400', frame_material: 'titanium', weight_grams: 24, warranty_years: 3, scenario: ['driving', 'office'], confidence_score: 0.62, match_reason: 'Premium polarized lenses, refined road presence' },
    ];
  } else {
    matches = [
      { product_id: 'P030', name: 'Wayfarer Stealth Black', brand: 'Ray-Ban', price: 6800, shape: 'wayfarer', polarized: true, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 30, warranty_years: 2, celebrity_worn: 'Ranveer Singh', scenario: ['everyday', 'travel'], confidence_score: 0.78, match_reason: 'Classic polarized wayfarer, timeless everyday choice' },
      { product_id: 'P031', name: 'Clubmaster Classic', brand: 'Ray-Ban', price: 8900, shape: 'clubmaster', polarized: true, uv_protection: 'UV400', frame_material: 'acetate', weight_grams: 32, warranty_years: 2, scenario: ['everyday', 'office'], confidence_score: 0.65, match_reason: 'Iconic browline frame, polished everyday look' },
      { product_id: 'P032', name: 'Round Vintage Gold', brand: 'Lenskart', price: 1299, shape: 'round', polarized: false, uv_protection: 'UV380', frame_material: 'metal', weight_grams: 22, warranty_years: 1, scenario: ['everyday', 'fashion'], confidence_score: 0.51, match_reason: 'Budget retro round frames, great entry-level pick' },
    ];
  }

  // Celebrity detection — add to top result
  if (query.includes('priyanka') || query.includes('deepika') || query.includes('alia')) {
    matches.forEach(m => { if (!m.celebrity_worn) m.celebrity_worn = 'Bollywood Celebrity'; });
  }
  if (query.includes('tom cruise') || query.includes('brad pitt') || query.includes('clooney')) {
    matches.forEach(m => { if (!m.celebrity_worn) m.celebrity_worn = 'Hollywood A-lister'; });
  }

  const tier = matches[0].confidence_score >= 0.7 ? 'High' :
               matches[0].confidence_score >= 0.5 ? 'Medium' : 'Low';

  const budgetPicks = matches.filter(m => m.price < 3000).map(m => ({ product_id: m.product_id, name: m.name, price: m.price }));
  const premiumPicks = matches.filter(m => m.price >= 8000).map(m => ({ product_id: m.product_id, name: m.name, price: m.price }));

  // Always guarantee some budget picks
  if (budgetPicks.length === 0) budgetPicks.push({ product_id: 'P032', name: 'Round Vintage Gold', price: 1299 });
  if (premiumPicks.length === 0) premiumPicks.push({ product_id: 'P002', name: 'Titanium Premium Aviator', price: 21000 });

  return {
    session_id: currentSession,
    style_dna: { shape, frame_color: color, lens_color: color, brand_hint: brand, gender: 'unisex', price_range_preference: null },
    matches,
    recommendations: {
      budget: budgetPicks,
      premium: premiumPicks,
      trending: [
        { product_id: 'P045', name: 'AquaShield Water Sports', price: 6800 },
        { product_id: 'P001', name: 'Classic Gold Aviator', price: 7500 },
        { product_id: 'P041', name: 'Festival Bold Round', price: 4200 },
      ],
    },
    confidence_tier: tier,
    governance_message: tier === 'High'
      ? `🎯 Excellent match! Our MCP pipeline identified a ${matches[0].confidence_score*100|0}% style alignment.`
      : tier === 'Medium'
      ? `✨ Found ${matches.length} strong matches. Try refining for more specific results.`
      : `💡 Showing best alternatives. Try describing shape, color, or occasion for better results.`,
  };
}


// ── Sort Results ────────────────────────────────
function sortResults() {
  const sort = document.getElementById('sortSelect').value;
  let sorted = [...lastMatches];
  if (sort === 'price-asc') sorted.sort((a, b) => (a.price||0) - (b.price||0));
  else if (sort === 'price-desc') sorted.sort((a, b) => (b.price||0) - (a.price||0));
  else if (sort === 'rating') sorted.sort((a, b) => (b.rating||4.5) - (a.rating||4.5));
  else if (sort === 'popular') sorted.sort((a, b) => (b.review_count||100) - (a.review_count||100));
  else sorted.sort((a, b) => (b.confidence_score||0) - (a.confidence_score||0));
  const grid = document.getElementById('productsGrid');
  grid.innerHTML = sorted.map((m, i) => renderProductCard(m, i + 1)).join('');
}

// ── Refinement ───────────────────────────────────
async function runRefine() {
  const refineText = document.getElementById('refineInput').value.trim();
  if (!refineText) return;

  const refinedQuery = refineText + (lastStyleDNA ?
    ` (context: ${lastStyleDNA.brand_hint || ''} ${lastStyleDNA.frame_color || ''} ${lastStyleDNA.shape || ''} ${lastStyleDNA.lens_color || ''})` : '');

  document.getElementById('textQuery').value = refinedQuery;
  switchMode('text');
  document.getElementById('refineInput').value = '';
  await runSearch();
}

// ── Utility ──────────────────────────────────────
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function getShapeEmoji(shape) {
  const map = {
    'aviator': '🕶️', 'wayfarer': '😎', 'round': '🔵',
    'square': '🟦', 'cat-eye': '😼', 'sport': '🏃',
    'shield': '🛡️', 'clubmaster': '🎭', 'oversized': '🌟',
  };
  const key = Object.keys(map).find(k => shape.toLowerCase().includes(k));
  return key ? map[key] : '👓';
}

function scoreColor(score) {
  if (score >= 0.7) return '#4ade80';
  if (score >= 0.45) return '#fbbf24';
  return '#f87171';
}

// ── Init ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('sessionIdDisplay').textContent = currentSession;

  // Check server connectivity
  checkServer().then(online => {
    const status = document.getElementById('serverStatus');
    if (online) {
      status.innerHTML = '<span class="status-dot" style="background:#4ade80"></span> MCP Server Live';
    } else {
      status.innerHTML = '<span class="status-dot" style="background:#fbbf24"></span> Demo Mode';
      status.style.color = '#fbbf24';
    }
    loadCart();
  });
});
