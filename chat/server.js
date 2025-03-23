const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const moment = require('moment');
const CryptoJS = require('crypto-js');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static('public'));

// Map to store userId -> socketId
const userSocketMap = new Map();
let requesterId = null; // Track the first user (requester)

io.on('connection', (socket) => {
    console.log('A user connected');

    socket.on('join', (userId) => {
        if (!userId) return;
        socket.userId = userId;
        userSocketMap.set(userId, socket.id);

        // Set the first user as the requester
        if (!requesterId && userSocketMap.size === 1) {
            requesterId = userId;
            console.log(`${userId} is the requester`);
        }

        // Send the user list to the client
        // If the user is the requester, send all users except themselves
        // If the user is a donor, only send the requester
        if (socket.userId === requesterId) {
            const users = Array.from(userSocketMap.keys()).filter(id => id !== requesterId);
            socket.emit('user list', users);
        } else {
            socket.emit('user list', requesterId ? [requesterId] : []);
        }

        // Broadcast updated user list to all other clients
        io.emit('update user list', requesterId, Array.from(userSocketMap.keys()));
        console.log(`${userId} joined`);
    });

    socket.on('chat message', (data) => {
        const timestamp = moment().format('hh:mm a');
        const encryptedMessage = CryptoJS.AES.encrypt(data.message, 'secret-key').toString();
        
        const messageData = {
            sender_id: data.sender_id,
            receiver_id: data.receiver_id,
            message: encryptedMessage,
            time: timestamp
        };

        // Only allow communication between requester and donor
        if (
            (data.sender_id === requesterId && userSocketMap.has(data.receiver_id)) ||
            (data.receiver_id === requesterId && userSocketMap.has(data.sender_id))
        ) {
            // Send to sender
            io.to(socket.id).emit('chat message', messageData);

            // Send to receiver
            const receiverSocketId = userSocketMap.get(data.receiver_id);
            if (receiverSocketId) {
                io.to(receiverSocketId).emit('chat message', messageData);
            }
        } else {
            console.log(`Blocked message: ${data.sender_id} tried to message ${data.receiver_id}`);
        }
    });

    socket.on('end chat', () => {
        if (socket.userId) {
            const wasRequester = socket.userId === requesterId;
            userSocketMap.delete(socket.userId);
            if (wasRequester) {
                requesterId = userSocketMap.size > 0 ? Array.from(userSocketMap.keys())[0] : null;
                console.log(`Requester changed to ${requesterId || 'none'}`);
            }
            io.emit('update user list', requesterId, Array.from(userSocketMap.keys()));
            console.log(`${socket.userId} ended chat`);
        }
    });

    socket.on('disconnect', () => {
        if (socket.userId) {
            const wasRequester = socket.userId === requesterId;
            userSocketMap.delete(socket.userId);
            if (wasRequester) {
                requesterId = userSocketMap.size > 0 ? Array.from(userSocketMap.keys())[0] : null;
                console.log(`Requester changed to ${requesterId || 'none'}`);
            }
            io.emit('update user list', requesterId, Array.from(userSocketMap.keys()));
            console.log(`${socket.userId} disconnected`);
        }
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});