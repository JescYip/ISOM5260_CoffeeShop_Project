// 全局变量
let products = [];
let cart = [];
let currentTab = 'menu';
let currentUser = null; 

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
async function initializeApp() {
    try {
        await loadProducts();
        setupEventListeners();
        showTab('menu');
        wireAccountForms();
    } catch (error) {
        console.error('Initialization failed:', error);
        showAlert('System initialization failed. Please refresh the page and try again.', 'error');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 导航标签点击事件
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            showTab(tabName);
        });
    });

    // 订单表单提交
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', handleOrderSubmit);
    }
}

// 绑定登录/注册表单事件
function wireAccountForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const payload = {
                email: formData.get('email'),
                password: formData.get('password')
            };
            try {
                const resp = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await resp.json();
                if (result.success) {
                    currentUser = result.data;
                    showAlert('Signed in successfully', 'success');
                    updateUIForLoggedInUser();
                } else {
                    throw new Error(result.error || 'Login failed');
                }
            } catch (err) {
                console.error(err);
                showAlert('Login failed', 'error');
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            const payload = {
                name: formData.get('name'),
                email: formData.get('email'),
                password: formData.get('password'),
                phone: formData.get('phone'),
                address: formData.get('address'),
                date_of_birth: formData.get('date_of_birth')
            };
            try {
                const resp = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await resp.json();
                if (result.success) {
                    showAlert('Account created. You can sign in now.', 'success');
                    loginForm && loginForm.reset();
                    registerForm.reset();
                } else {
                    throw new Error(result.error || 'Registration failed');
                }
            } catch (err) {
                console.error(err);
                showAlert('Registration failed', 'error');
            }
        });
    }
}

// 加载产品数据
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        const result = await response.json();
        
        if (result.success) {
            products = result.data;
            renderProducts();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to load product:', error);
        showAlert('Failed to load product', 'error');
    }
}

// 渲染产品列表
function renderProducts() {
    const container = document.getElementById('productsContainer');
    if (!container) return;

    container.innerHTML = '';
    
    // 按分类分组产品
    const categories = {};
    products.forEach(product => {
        if (!categories[product.category]) {
            categories[product.category] = [];
        }
        categories[product.category].push(product);
    });

    // 渲染每个分类的产品
    Object.keys(categories).forEach(categoryName => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'category-section';
        categoryDiv.innerHTML = `
            <h2 style="color: #4a5568; margin: 20px 0 15px 0; font-size: 1.5em;">${categoryName}</h2>
            <div class="products-grid" id="category-${categoryName}"></div>
        `;
        container.appendChild(categoryDiv);

        const categoryGrid = document.getElementById(`category-${categoryName}`);
        categories[categoryName].forEach(product => {
            const productCard = createProductCard(product);
            categoryGrid.appendChild(productCard);
        });
    });
}

// 创建产品卡片
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    // 手动指定每个产品的图片路径
    const imageMap = {
        'Americano': '/picture/americano.jpg',
        'Latte': '/picture/latte.jpg',
        'Cappuccino': '/picture/Cappuccino.jpg',
        'Mocha': '/picture/Mocha.jpg',
        'chinesetea': '/picture/chinesetea.jpg',
        'Milk Tea': '/picture/Milktea.jpg',
        'Cheesecake': '/picture/cheesecake.jpg',
        'Tiramisu': '/picture/tiramisu.jpg',
        'Ham Sandwich': '/picture/HamSandwich.jpg',
        'Caesar Salad': '/picture/caesarsalad.jpg'
    };
    
    const imgSrc = imageMap[product.name] || '/picture/default.jpg';
    
    // 检查是否为咖啡类产品
    const isCoffee = product.category === 'Coffee';
    
    let coffeeOptions = '';
    if (isCoffee) {
        coffeeOptions = `
            <div class="coffee-options" style="margin: 10px 0;">
                <div style="margin-bottom: 8px;">
                    <label style="font-size: 0.9em; font-weight: bold;">Milk Type:</label>
                    <select id="milk-${product.id}" style="width: 100%; padding: 4px; font-size: 0.8em; border: 1px solid #ddd; border-radius: 3px;">
                        <option value="regular">Regular Milk</option>
                        <option value="skim">Skim Milk</option>
                        <option value="soy">Soy Milk</option>
                        <option value="almond">Almond Milk</option>
                        <option value="oat">Oat Milk</option>
                        <option value="none">No Milk</option>
                    </select>
                </div>
                <div>
                    <label style="font-size: 0.9em; font-weight: bold;">Ice Level:</label>
                    <select id="ice-${product.id}" style="width: 100%; padding: 4px; font-size: 0.8em; border: 1px solid #ddd; border-radius: 3px;">
                        <option value="hot">Hot</option>
                        <option value="no-ice">No Ice</option>
                        <option value="light-ice">Light Ice</option>
                        <option value="regular-ice">Regular Ice</option>
                        <option value="extra-ice">Extra Ice</option>
                    </select>
                </div>
            </div>
        `;
    }
    
    card.innerHTML = `
        <img class="product-image" src="${imgSrc}" alt="${product.name}" />
        <h3>${product.name}</h3>
        <div class="category">${product.category}</div>
        <div class="price">$${product.price.toFixed(2)}</div>
        ${coffeeOptions}
        <div class="quantity-control">
            <button class="quantity-btn" onclick="changeQuantity(${product.id}, -1)">-</button>
            <input type="number" class="quantity-input" id="qty-${product.id}" value="1" min="1" max="99">
            <button class="quantity-btn" onclick="changeQuantity(${product.id}, 1)">+</button>
        </div>
        <button class="add-to-cart" onclick="addToCart(${product.id})">
            Add to Cart
        </button>
    `;
    return card;
}

// 将产品名转为图片文件名（小写、去空格和特殊字符）
/*function slugifyProductName(name) {
    return String(name)
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .trim()
        .replace(/\s+/g, '');
}*/

// 修改数量
function changeQuantity(productId, change) {
    const input = document.getElementById(`qty-${productId}`);
    const currentValue = parseInt(input.value);
    const newValue = Math.max(1, Math.min(99, currentValue + change));
    input.value = newValue;
}

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const quantity = parseInt(document.getElementById(`qty-${productId}`).value);
    
    if (!product) return;

    // 获取咖啡选项（如果是咖啡类产品）
    let coffeeOptions = {};
    if (product.category === 'Coffee') {
        const milkSelect = document.getElementById(`milk-${productId}`);
        const iceSelect = document.getElementById(`ice-${productId}`);
        
        if (milkSelect && iceSelect) {
            coffeeOptions = {
                milk_type: milkSelect.value,
                ice_level: iceSelect.value
            };
        }
    }

    const existingItem = cart.find(item => 
        item.product_id === productId && 
        JSON.stringify(item.coffee_options || {}) === JSON.stringify(coffeeOptions)
    );
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        const cartItem = {
            product_id: productId,
            name: product.name,
            price: product.price,
            quantity: quantity
        };
        
        // 如果有咖啡选项，添加到购物车项中
        if (Object.keys(coffeeOptions).length > 0) {
            cartItem.coffee_options = coffeeOptions;
        }
        
        cart.push(cartItem);
    }

    updateCartDisplay();
    
    // 显示添加成功的消息，包含咖啡选项信息
    let message = `${product.name} added to cart`;
    if (coffeeOptions.milk_type || coffeeOptions.ice_level) {
        const options = [];
        if (coffeeOptions.milk_type) options.push(`Milk: ${coffeeOptions.milk_type}`);
        if (coffeeOptions.ice_level) options.push(`Ice: ${coffeeOptions.ice_level}`);
        message += ` (${options.join(', ')})`;
    }
    showAlert(message, 'success');
    
    document.getElementById(`qty-${productId}`).value = 1;
}

// 更新购物车显示
function updateCartDisplay() {
    const cartContainer = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    if (!cartContainer || !cartTotal) return;

    if (cart.length === 0) {
        cartContainer.innerHTML = '<p style="text-align: center; color: #718096;">Your cart is empty</p>';
        cartTotal.textContent = 'Total: $0.00';
        return;
    }

    let total = 0;
    cartContainer.innerHTML = '';

    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        
        // 显示咖啡选项信息
        let optionsText = '';
        if (item.coffee_options) {
            const options = [];
            if (item.coffee_options.milk_type) options.push(`Milk: ${item.coffee_options.milk_type}`);
            if (item.coffee_options.ice_level) options.push(`Ice: ${item.coffee_options.ice_level}`);
            if (options.length > 0) {
                optionsText = `<br><small style="color: #718096;">${options.join(', ')}</small>`;
            }
        }
        
        cartItem.innerHTML = `
            <div>
                <strong>${item.name}</strong><br>
                <small>$${item.price.toFixed(2)} x ${item.quantity}</small>
                ${optionsText}
            </div>
            <div>
                <span style="margin-right: 10px;">$${itemTotal.toFixed(2)}</span>
                <button class="btn-danger" style="padding: 5px 10px; font-size: 0.8em;" onclick="removeFromCart(${index})">Remove</button>
            </div>
        `;
        cartContainer.appendChild(cartItem);
    });

    cartTotal.textContent = `Total: $${total.toFixed(2)}`;
}

// 从购物车移除商品
function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartDisplay();
    showAlert('Item removed from cart', 'info');
}

// 清空购物车
function clearCart() {
    cart = [];
    updateCartDisplay();
    showAlert('Cart cleared', 'info');
}

// 处理订单提交
async function handleOrderSubmit(e) {
    e.preventDefault();
    
    if (cart.length === 0) {
        showAlert('Your cart is empty. Please add items first.', 'error');
        return;
    }

    const formData = new FormData(e.target);
    const orderData = {
        customer_name: formData.get('customer_name'),
        customer_phone: formData.get('customer_phone'),
        customer_email: formData.get('customer_email'),
        customer_address: formData.get('customer_address'),
        payment_method: formData.get('payment_method'),
        items: cart
    };

    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();
        
        if (result.success) {
            showAlert(`Order created! ID: ${result.order_id}`, 'success');
            clearCart();
            document.getElementById('orderForm').reset();
            hideMemberVerificationForm();
        } else if (result.error === 'VERIFICATION_REQUIRED') {
            // 需要会员验证
            showMemberVerificationForm(orderData.customer_name, orderData);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Create order failed:', error);
        showAlert('Failed to create order. Please try again.', 'error');
    }
}

// 显示会员验证表单
function showMemberVerificationForm(customerName, orderData) {
    // 移除现有的验证表单
    const existingForm = document.getElementById('memberVerificationForm');
    if (existingForm) {
        existingForm.remove();
    }

    const verificationForm = document.createElement('div');
    verificationForm.id = 'memberVerificationForm';
    verificationForm.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 500px;
        width: 90%;
        max-height: 80%;
        overflow-y: auto;
    `;

    content.innerHTML = `
        <h2 style="margin-bottom: 20px; color: #4a5568;">Member Verification Required</h2>
        <p style="margin-bottom: 20px; color: #718096;">
            We found potential member(s) with the name "${customerName}". 
            Please provide your email or phone number to verify your membership.
        </p>
        <form id="verificationForm">
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Email:</label>
                <input type="email" name="verification_email" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            </div>
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Phone:</label>
                <input type="tel" name="verification_phone" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            </div>
            <div style="text-align: center;">
                <button type="button" onclick="verifyMember('${customerName}', ${JSON.stringify(orderData).replace(/"/g, '&quot;')})" 
                        style="background: #4299e1; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin-right: 10px; cursor: pointer;">
                    Verify Member
                </button>
                <button type="button" onclick="createRegularCustomer(${JSON.stringify(orderData).replace(/"/g, '&quot;')})" 
                        style="background: #718096; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                    Continue as Regular Customer
                </button>
            </div>
        </form>
    `;

    verificationForm.appendChild(content);
    document.body.appendChild(verificationForm);
}

// 隐藏会员验证表单
function hideMemberVerificationForm() {
    const form = document.getElementById('memberVerificationForm');
    if (form) {
        form.remove();
    }
}

// 验证会员身份
async function verifyMember(customerName, orderData) {
    const form = document.getElementById('verificationForm');
    const formData = new FormData(form);
    const email = formData.get('verification_email');
    const phone = formData.get('verification_phone');

    if (!email && !phone) {
        showAlert('Please provide either email or phone number for verification.', 'error');
        return;
    }

    try {
        const response = await fetch('/api/customers/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: customerName,
                email: email,
                phone: phone
            })
        });

        const result = await response.json();
        
        if (result.success && result.verified) {
            // 验证成功，使用会员信息创建订单
            orderData.customer_id = result.customer.customer_id;
            orderData.customer_email = email || orderData.customer_email;
            orderData.customer_phone = phone || orderData.customer_phone;
            
            await createOrderWithData(orderData);
            hideMemberVerificationForm();
        } else {
            showAlert(result.error || 'Verification failed. Please check your email or phone number.', 'error');
        }
    } catch (error) {
        console.error('Verification failed:', error);
        showAlert('Verification failed. Please try again.', 'error');
    }
}

// 创建普通客户订单
async function createRegularCustomer(orderData) {
    // 添加force_regular标志，表示用户明确要求作为普通客户
    orderData.force_regular = true;
    await createOrderWithData(orderData);
    hideMemberVerificationForm();
}

// 使用指定数据创建订单
async function createOrderWithData(orderData) {
    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();
        
        if (result.success) {
            showAlert(`Order created! ID: ${result.order_id}`, 'success');
            clearCart();
            document.getElementById('orderForm').reset();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Create order failed:', error);
        showAlert('Failed to create order. Please try again.', 'error');
    }
}

// 显示标签页
function showTab(tabName) {
    // 更新导航标签
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // 更新内容区域
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');

    currentTab = tabName;

    // Orders tab removed for public site; admin handles orders
}

// 加载订单历史
async function loadOrderHistory() {
    try {
        const response = await fetch('/api/orders');
        const result = await response.json();
        
        if (result.success) {
            renderOrderHistory(result.data);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Load order history failed:', error);
        showAlert('Failed to load order history', 'error');
    }
}

// 渲染订单历史
function renderOrderHistory(orders) {
    const container = document.getElementById('ordersContainer');
    if (!container) return;

    if (orders.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #718096;">No orders yet</p>';
        return;
    }

    const table = document.createElement('table');
    table.className = 'table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Order Date</th>
                <th>Status</th>
                <th>Payment</th>
                <th>Total</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            ${orders.map(order => `
                <tr>
                    <td>#${order.order_id}</td>
                    <td>${order.customer_name}</td>
                            <td>${new Date(order.order_date).toLocaleString('en-US')}</td>
                    <td><span class="status-${order.status}">${getStatusText(order.status)}</span></td>
                    <td>${getPaymentMethodText(order.payment_method)}</td>
                    <td>$${order.total_amount.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 0.8em;" onclick="viewOrderDetails(${order.order_id})">Details</button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;

    container.innerHTML = '';
    container.appendChild(table);
}

// 查看订单详情
async function viewOrderDetails(orderId) {
    try {
        const response = await fetch(`/api/orders/${orderId}/details`);
        const result = await response.json();
        
        if (result.success) {
            showOrderDetailsModal(orderId, result.data);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to load order details:', error);
        showAlert('Failed to load order details', 'error');
    }
}

function showOrderDetailsModal(orderId, items) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 600px;
        width: 90%;
        max-height: 80%;
        overflow-y: auto;
    `;

    let total = 0;
    items.forEach(item => {
        total += item.line_amount;
    });

    content.innerHTML = `
        <h2 style="margin-bottom: 20px; color: #4a5568;">Order Details #${orderId}</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Qty</th>
                    <th>Unit Price</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.product_name}</td>
                        <td>${item.quantity}</td>
                        <td>$${item.unit_price.toFixed(2)}</td>
                        <td>$${item.line_amount.toFixed(2)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        <div style="text-align: right; margin-top: 20px; font-size: 1.2em; font-weight: bold; color: #4a5568;">
            Total: $${total.toFixed(2)}
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
        </div>
    `;

    modal.className = 'modal';
    modal.appendChild(content);
    document.body.appendChild(modal);

    // 点击背景关闭模态框
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'pending': 'Pending',
        'processing': 'Processing',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    };
    return statusMap[status] || status;
}

// 获取支付方式文本
function getPaymentMethodText(method) {
    const methodMap = {
        'cash': 'Cash',
        'card': 'Card',
        'alipay': 'Alipay',
        'wechat': 'WeChat Pay'
    };
    return methodMap[method] || method;
}

// 更新登录后的UI
function updateUIForLoggedInUser() {
    if (!currentUser) return;
    
    // 更新导航栏，显示用户信息
    const navTabs = document.querySelector('.nav-tabs');
    if (navTabs && currentUser.customer_type === 'member') {
        // 添加会员标识
        const memberBadge = document.createElement('div');
        memberBadge.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: #f6ad55;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        `;
        memberBadge.textContent = `👑 ${currentUser.name} (Member)`;
        navTabs.appendChild(memberBadge);
        
        // 添加登出按钮
        const logoutBtn = document.createElement('button');
        logoutBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 200px;
            background: #e53e3e;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8em;
            cursor: pointer;
        `;
        logoutBtn.textContent = 'Logout';
        logoutBtn.onclick = logout;
        navTabs.appendChild(logoutBtn);
    }
    
    // 更新结账表单，预填会员信息
    if (currentUser.customer_type === 'member') {
        const nameField = document.getElementById('customer_name');
        const emailField = document.getElementById('customer_email');
        const phoneField = document.getElementById('customer_phone');
        const addressField = document.getElementById('customer_address');
        
        if (nameField) nameField.value = currentUser.name;
        if (emailField) emailField.value = currentUser.email || '';
        if (phoneField) phoneField.value = currentUser.phone || '';
        if (addressField) addressField.value = currentUser.address || '';
        
        // 显示会员专属功能
        showMemberFeatures();
        
        // 应用会员的咖啡偏好
        applyMemberCoffeePreferences();
        
        // 显示会员偏好
        loadMemberPreferencesDisplay();
    }
}

// 显示会员专属功能
function showMemberFeatures() {
    const orderTab = document.getElementById('orderTab');
    if (orderTab && currentUser && currentUser.customer_type === 'member') {
        const memberInfo = document.createElement('div');
        memberInfo.style.cssText = `
            background: #e6fffa;
            border: 1px solid #38b2ac;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            color: #2d3748;
        `;
        memberInfo.innerHTML = `
            <h4 style="margin: 0 0 10px 0; color: #2c7a7b;">👑 Member Features</h4>
            <div id="memberPreferencesDisplay" style="margin-bottom: 10px;">
                <div style="text-align: center; color: #718096; font-size: 0.9em;">Loading preferences...</div>
            </div>
            <div style="margin-top: 10px;">
                <button onclick="showOrderHistory()" style="
                    background: #38b2ac;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    margin-right: 10px;
                    cursor: pointer;
                    font-size: 0.9em;
                ">Order History</button>
                <button onclick="showMemberPreferences()" style="
                    background: #4299e1;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    margin-right: 10px;
                    cursor: pointer;
                    font-size: 0.9em;
                ">Manage Preferences</button>
                <button onclick="quickApplyPreferences()" style="
                    background: #f6ad55;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 0.9em;
                ">Apply Preferences</button>
            </div>
        `;
        
        // 插入到订单摘要之前
        const orderSummary = orderTab.querySelector('.cart');
        if (orderSummary) {
            orderTab.insertBefore(memberInfo, orderSummary);
        }
    }
}

// 登出功能
function logout() {
    currentUser = null;
    // 移除会员标识和登出按钮
    const memberBadge = document.querySelector('.nav-tabs div[style*="👑"]');
    const logoutBtn = document.querySelector('.nav-tabs button[style*="Logout"]');
    if (memberBadge) memberBadge.remove();
    if (logoutBtn) logoutBtn.remove();
    
    // 移除会员功能信息
    const memberInfo = document.querySelector('div[style*="Member Features"]');
    if (memberInfo) memberInfo.remove();
    
    // 清空结账表单
    document.getElementById('orderForm').reset();
    
    showAlert('Logged out successfully', 'info');
}

// 显示订单历史
async function showOrderHistory() {
    if (!currentUser || currentUser.customer_type !== 'member') {
        showAlert('Please login as a member to view order history', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/orders?customer_id=${currentUser.customer_id}`);
        const result = await response.json();
        
        if (result.success) {
            showOrderHistoryModal(result.data);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to load order history:', error);
        showAlert('Failed to load order history', 'error');
    }
}

// 显示订单历史模态框
function showOrderHistoryModal(orders) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 800px;
        width: 90%;
        max-height: 80%;
        overflow-y: auto;
    `;

    if (orders.length === 0) {
        content.innerHTML = `
            <h2 style="margin-bottom: 20px; color: #4a5568;">Order History</h2>
            <p style="text-align: center; color: #718096; padding: 40px;">No orders found</p>
            <div style="text-align: center; margin-top: 20px;">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
            </div>
        `;
    } else {
        content.innerHTML = `
            <h2 style="margin-bottom: 20px; color: #4a5568;">Order History</h2>
            <div style="max-height: 400px; overflow-y: auto;">
                ${orders.map(order => `
                    <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4 style="margin: 0; color: #2d3748;">Order #${order.order_id}</h4>
                            <span style="color: #718096; font-size: 0.9em;">${new Date(order.order_date).toLocaleDateString()}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div>
                                <span style="color: #4a5568;">Payment: ${getPaymentMethodText(order.payment_method)}</span>
                            </div>
                            <div style="font-weight: bold; color: #2d3748;">$${order.total_amount.toFixed(2)}</div>
                        </div>
                        <div id="order-items-${order.order_id}" style="margin-bottom: 10px;">
                            <div style="text-align: center; color: #718096; font-size: 0.9em;">Loading items...</div>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button onclick="loadOrderItems(${order.order_id})" style="
                                background: #38b2ac;
                                color: white;
                                border: none;
                                padding: 5px 10px;
                                border-radius: 5px;
                                cursor: pointer;
                                font-size: 0.8em;
                            ">View Items</button>
                            <button onclick="reorderFromHistory(${order.order_id})" style="
                                background: #4299e1;
                                color: white;
                                border: none;
                                padding: 5px 10px;
                                border-radius: 5px;
                                cursor: pointer;
                                font-size: 0.8em;
                            ">Reorder</button>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
            </div>
        `;
    }

    modal.className = 'modal';
    modal.appendChild(content);
    document.body.appendChild(modal);

    // 点击背景关闭模态框
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// 加载订单详情
async function loadOrderItems(orderId) {
    const itemsContainer = document.getElementById(`order-items-${orderId}`);
    if (!itemsContainer) return;
    
    try {
        const response = await fetch(`/api/orders/${orderId}/details`);
        const result = await response.json();
        
        if (result.success) {
            if (result.data.length > 0) {
                itemsContainer.innerHTML = `
                    <div style="background: #f7fafc; padding: 10px; border-radius: 5px;">
                        <div style="font-weight: bold; margin-bottom: 8px; color: #2d3748;">Order Items:</div>
                        ${result.data.map(item => `
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; font-size: 0.9em;">
                                <span>${item.product_name} x ${item.quantity}</span>
                                <span style="font-weight: bold;">$${item.line_amount.toFixed(2)}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                itemsContainer.innerHTML = '<div style="text-align: center; color: #718096; font-size: 0.9em;">No items found</div>';
            }
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to load order items:', error);
        itemsContainer.innerHTML = '<div style="text-align: center; color: #e53e3e; font-size: 0.9em;">Failed to load items</div>';
    }
}

// 从历史订单重新下单
async function reorderFromHistory(orderId) {
    try {
        const response = await fetch(`/api/orders/${orderId}/details`);
        const result = await response.json();
        
        if (result.success) {
            // 清空当前购物车
            cart = [];
            
            // 添加历史订单中的商品到购物车
            result.data.forEach(item => {
                cart.push({
                    product_id: item.product_id,
                    name: item.product_name,
                    price: item.unit_price,
                    quantity: item.quantity
                });
            });
            
            updateCartDisplay();
            showAlert('Items added to cart from order history', 'success');
            
            // 关闭模态框并切换到购物车
            document.querySelector('.modal').remove();
            showTab('cart');
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to reorder:', error);
        showAlert('Failed to reorder items', 'error');
    }
}

// 显示会员偏好管理
async function showMemberPreferences() {
    if (!currentUser || currentUser.customer_type !== 'member') {
        showAlert('Please login as a member to manage preferences', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/member/preferences?customer_id=${currentUser.customer_id}`);
        const result = await response.json();
        
        if (result.success) {
            showPreferencesModal(result.data);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to load preferences:', error);
        showAlert('Failed to load preferences', 'error');
    }
}

// 显示偏好管理模态框
function showPreferencesModal(data) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 600px;
        width: 90%;
        max-height: 80%;
        overflow-y: auto;
    `;

    content.innerHTML = `
        <h2 style="margin-bottom: 20px; color: #4a5568;">My Preferences</h2>
        
        <div style="margin-bottom: 30px;">
            <h3 style="color: #2d3748; margin-bottom: 15px;">Favorite Products</h3>
            ${data.favorites.length > 0 ? `
                <div style="display: grid; gap: 10px;">
                    ${data.favorites.map(fav => `
                        <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${fav.name}</strong>
                                <div style="color: #718096; font-size: 0.9em;">
                                    Ordered ${fav.order_count} times • Total: ${fav.total_quantity} items
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-weight: bold; color: #2d3748;">$${fav.price.toFixed(2)}</div>
                                <button onclick="addFavoriteToCart(${fav.product_id})" style="
                                    background: #4299e1;
                                    color: white;
                                    border: none;
                                    padding: 5px 10px;
                                    border-radius: 5px;
                                    margin-top: 5px;
                                    cursor: pointer;
                                    font-size: 0.8em;
                                ">Add to Cart</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : '<p style="color: #718096; text-align: center; padding: 20px;">No favorite products yet. Start ordering to see your favorites!</p>'}
        </div>
        
        <div style="margin-bottom: 30px;">
            <h3 style="color: #2d3748; margin-bottom: 15px;">Coffee Preferences</h3>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Preferred Milk Type:</label>
                <select id="preferredMilk" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="">Select milk type</option>
                    <option value="regular">Regular Milk</option>
                    <option value="skim">Skim Milk</option>
                    <option value="soy">Soy Milk</option>
                    <option value="almond">Almond Milk</option>
                    <option value="oat">Oat Milk</option>
                    <option value="none">No Milk</option>
                </select>
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Preferred Ice Level:</label>
                <select id="preferredIce" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="">Select ice level</option>
                    <option value="hot">Hot</option>
                    <option value="no-ice">No Ice</option>
                    <option value="light-ice">Light Ice</option>
                    <option value="regular-ice">Regular Ice</option>
                    <option value="extra-ice">Extra Ice</option>
                </select>
            </div>
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Preferred Payment Method:</label>
                <select id="preferredPayment" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="">Select payment method</option>
                    <option value="cash">Cash</option>
                    <option value="card">Card</option>
                    <option value="alipay">Alipay</option>
                    <option value="wechat">WeChat Pay</option>
                </select>
            </div>
            <div style="display: flex; gap: 10px;">
                <button onclick="savePreferences()" style="
                    background: #38b2ac;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 0.9em;
                ">Save Preferences</button>
                <button onclick="applyPreferencesToProducts()" style="
                    background: #4299e1;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 0.9em;
                ">Apply to Products</button>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
        </div>
    `;

    modal.className = 'modal';
    modal.appendChild(content);
    document.body.appendChild(modal);

    // 设置当前偏好值（在模态框添加到DOM后）
    data.preferences.forEach(pref => {
        if (pref.type === 'payment_method') {
            const element = document.getElementById('preferredPayment');
            if (element) element.value = pref.value;
        } else if (pref.type === 'milk_type') {
            const element = document.getElementById('preferredMilk');
            if (element) element.value = pref.value;
        } else if (pref.type === 'ice_level') {
            const element = document.getElementById('preferredIce');
            if (element) element.value = pref.value;
        }
    });

    // 点击背景关闭模态框
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// 保存偏好设置
async function savePreferences() {
    const paymentMethod = document.getElementById('preferredPayment').value;
    const milkType = document.getElementById('preferredMilk').value;
    const iceLevel = document.getElementById('preferredIce').value;
    
    try {
        const promises = [];
        
        if (paymentMethod) {
            promises.push(fetch('/api/member/preferences', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_id: currentUser.customer_id,
                    preference_type: 'payment_method',
                    preference_value: paymentMethod
                })
            }));
        }
        
        if (milkType) {
            promises.push(fetch('/api/member/preferences', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_id: currentUser.customer_id,
                    preference_type: 'milk_type',
                    preference_value: milkType
                })
            }));
        }
        
        if (iceLevel) {
            promises.push(fetch('/api/member/preferences', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_id: currentUser.customer_id,
                    preference_type: 'ice_level',
                    preference_value: iceLevel
                })
            }));
        }
        
        if (promises.length > 0) {
            await Promise.all(promises);
            showAlert('Preferences saved successfully', 'success');
            // 刷新偏好显示
            loadMemberPreferencesDisplay();
        } else {
            showAlert('Please select at least one preference to save', 'info');
        }
    } catch (error) {
        console.error('Failed to save preferences:', error);
        showAlert('Failed to save preferences', 'error');
    }
}

// 应用会员的咖啡偏好
async function applyMemberCoffeePreferences() {
    if (!currentUser || currentUser.customer_type !== 'member') return;
    
    try {
        const response = await fetch(`/api/member/preferences?customer_id=${currentUser.customer_id}`);
        const result = await response.json();
        
        if (result.success) {
            const preferences = result.data.preferences;
            let milkPreference = '';
            let icePreference = '';
            
            preferences.forEach(pref => {
                if (pref.type === 'milk_type') milkPreference = pref.value;
                if (pref.type === 'ice_level') icePreference = pref.value;
            });
            
            // 应用偏好到所有咖啡产品
            applyPreferencesToCoffeeProducts(milkPreference, icePreference);
        }
    } catch (error) {
        console.error('Failed to apply coffee preferences:', error);
    }
}

// 应用偏好到咖啡产品
function applyPreferencesToCoffeeProducts(milkPreference, icePreference) {
    if (milkPreference || icePreference) {
        products.forEach(product => {
            if (product.category === 'Coffee') {
                if (milkPreference) {
                    const milkSelect = document.getElementById(`milk-${product.id}`);
                    if (milkSelect) milkSelect.value = milkPreference;
                }
                if (icePreference) {
                    const iceSelect = document.getElementById(`ice-${product.id}`);
                    if (iceSelect) iceSelect.value = icePreference;
                }
            }
        });
        showAlert('Preferences applied to all coffee products', 'success');
    } else {
        showAlert('No coffee preferences to apply', 'info');
    }
}

// 从偏好设置模态框应用偏好到产品
async function applyPreferencesToProducts() {
    if (!currentUser || currentUser.customer_type !== 'member') return;
    
    try {
        const response = await fetch(`/api/member/preferences?customer_id=${currentUser.customer_id}`);
        const result = await response.json();
        
        if (result.success) {
            const preferences = result.data.preferences;
            let milkPreference = '';
            let icePreference = '';
            
            preferences.forEach(pref => {
                if (pref.type === 'milk_type') milkPreference = pref.value;
                if (pref.type === 'ice_level') icePreference = pref.value;
            });
            
            applyPreferencesToCoffeeProducts(milkPreference, icePreference);
        }
    } catch (error) {
        console.error('Failed to apply preferences:', error);
        showAlert('Failed to apply preferences', 'error');
    }
}

// 快速应用偏好（从会员功能区域）
async function quickApplyPreferences() {
    if (!currentUser || currentUser.customer_type !== 'member') {
        showAlert('Please login as a member to apply preferences', 'error');
        return;
    }
    
    await applyMemberCoffeePreferences();
}

// 加载会员偏好显示
async function loadMemberPreferencesDisplay() {
    const preferencesDisplay = document.getElementById('memberPreferencesDisplay');
    if (!preferencesDisplay || !currentUser || currentUser.customer_type !== 'member') return;
    
    try {
        const response = await fetch(`/api/member/preferences?customer_id=${currentUser.customer_id}`);
        const result = await response.json();
        
        if (result.success) {
            const preferences = result.data.preferences;
            
            if (preferences.length > 0) {
                let preferencesText = '<div style="font-size: 0.9em; color: #4a5568;">';
                preferences.forEach(pref => {
                    let displayValue = pref.value;
                    if (pref.type === 'milk_type') {
                        displayValue = displayValue.charAt(0).toUpperCase() + displayValue.slice(1).replace('-', ' ');
                    } else if (pref.type === 'ice_level') {
                        displayValue = displayValue.charAt(0).toUpperCase() + displayValue.slice(1).replace('-', ' ');
                    } else if (pref.type === 'payment_method') {
                        displayValue = getPaymentMethodText(pref.value);
                    }
                    preferencesText += `• ${pref.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}: ${displayValue}<br>`;
                });
                preferencesText += '</div>';
                preferencesDisplay.innerHTML = preferencesText;
            } else {
                preferencesDisplay.innerHTML = '<div style="text-align: center; color: #718096; font-size: 0.9em;">No preferences set yet</div>';
            }
        } else {
            preferencesDisplay.innerHTML = '<div style="text-align: center; color: #e53e3e; font-size: 0.9em;">Failed to load preferences</div>';
        }
    } catch (error) {
        console.error('Failed to load preferences display:', error);
        preferencesDisplay.innerHTML = '<div style="text-align: center; color: #e53e3e; font-size: 0.9em;">Failed to load preferences</div>';
    }
}

// 添加喜欢的商品到购物车
function addFavoriteToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (product) {
        addToCart(productId);
        showAlert(`${product.name} added to cart`, 'success');
    }
}

// 显示提示消息
function showAlert(message, type = 'info') {
    // 移除现有的提示
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    // 插入到内容区域顶部
    const content = document.querySelector('.content');
    content.insertBefore(alert, content.firstChild);

    // 3秒后自动移除
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 3000);
}