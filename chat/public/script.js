const socket = io();
const form = document.getElementById('form');
const input = document.getElementById('input');
const messages = document.getElementById('messages');
const senderIdInput = document.getElementById('sender_id');
const connectBtn = document.getElementById('connect-btn');
const usersList = document.getElementById('users-list');
const userSection = document.getElementById('user-section');
const chatSection = document.getElementById('chat-section');
const endChatBtn = document.getElementById('end-chat-btn');

let currentUserId = null;
let connectedUsers = new Set();
let requesterId = null;

// Encryption and Decryption Functions
function encryptMessage(message) {
    return CryptoJS.AES.encrypt(message, 'secret-key').toString();
}

function decryptMessage(encryptedMessage) {
    try {
        const bytes = CryptoJS.AES.decrypt(encryptedMessage, 'secret-key');
        return bytes.toString(CryptoJS.enc.Utf8);
    } catch (e) {
        return '[Decryption Failed]';
    }
}

// Connect button click
connectBtn.addEventListener('click', () => {
    currentUserId = senderIdInput.value.trim();
    if (currentUserId) {
        socket.emit('join', currentUserId);
        userSection.style.display = 'none';
        chatSection.style.display = 'flex';
    } else {
        alert('Please enter a valid User ID');
    }
});

// End chat button click
endChatBtn.addEventListener('click', () => {
    socket.emit('end chat');
    currentUserId = null;
    requesterId = null;
    connectedUsers.clear();
    usersList.innerHTML = '';
    messages.innerHTML = '';
    userSection.style.display = 'block';
    chatSection.style.display = 'none';
    senderIdInput.value = '';
});

// Form submission for sending messages
form.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = input.value.trim();
    const receiverId = document.querySelector('.user-button.active')?.dataset.userId;

    if (message && currentUserId && receiverId) {
        const data = {
            sender_id: currentUserId,
            receiver_id: receiverId,
            message: message // Send plaintext, server encrypts
        };
        socket.emit('chat message', data);
        input.value = '';
    }
});

// Update user list (initial list on join)
socket.on('user list', (users) => {
    updateUserList(users);
});

// Update user list (broadcasted updates)
socket.on('update user list', (newRequesterId, allUsers) => {
    requesterId = newRequesterId;
    const users = currentUserId === requesterId
        ? allUsers.filter(id => id !== currentUserId)
        : requesterId ? [requesterId] : [];
    updateUserList(users);
});

function updateUserList(users) {
    usersList.innerHTML = '';
    connectedUsers.clear();
    users.forEach(userId => {
        if (userId !== currentUserId && !connectedUsers.has(userId)) {
            connectedUsers.add(userId);
            const button = document.createElement('button');
            button.classList.add('user-button');
            button.dataset.userId = userId;
            button.textContent = userId;
            button.addEventListener('click', () => {
                document.querySelectorAll('.user-button').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                messages.innerHTML = ''; // Clear messages
                loadChatHistory(userId);
            });
            usersList.appendChild(button);
            // Automatically select the requester for donors
            if (currentUserId !== requesterId && users.length === 1) {
                button.classList.add('active');
                loadChatHistory(userId);
            }
        }
    });
}

// Receive chat messages
socket.on('chat message', (data) => {
    const activeUserId = document.querySelector('.user-button.active')?.dataset.userId;
    if (
        (data.sender_id === currentUserId && data.receiver_id === activeUserId) ||
        (data.sender_id === activeUserId && data.receiver_id === currentUserId)
    ) {
        const decryptedMessage = decryptMessage(data.message);
        const item = document.createElement('li');
        item.textContent = `[${data.time}] ${data.sender_id}: ${decryptedMessage}`;
        item.classList.add(data.sender_id === currentUserId ? 'sent' : 'received');
        messages.appendChild(item);
        messages.scrollTop = messages.scrollHeight;

        // Store in localStorage
        const chatKey = [data.sender_id, data.receiver_id].sort().join('-');
        const chatHistory = JSON.parse(localStorage.getItem(chatKey) || '[]');
        chatHistory.push(data);
        localStorage.setItem(chatKey, JSON.stringify(chatHistory));
    }
});

// Load chat history for selected user
function loadChatHistory(receiverId) {
    const chatKey = [currentUserId, receiverId].sort().join('-');
    const chatHistory = JSON.parse(localStorage.getItem(chatKey) || '[]');
    chatHistory.forEach(data => {
        const decryptedMessage = decryptMessage(data.message);
        const item = document.createElement('li');
        item.textContent = `[${data.time}] ${data.sender_id}: ${decryptedMessage}`;
        item.classList.add(data.sender_id === currentUserId ? 'sent' : 'received');
        messages.appendChild(item);
    });
    messages.scrollTop = messages.scrollHeight;
}