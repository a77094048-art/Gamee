const WebSocket = require('ws');
const http = require('http');

const server = http.createServer();
const wss = new WebSocket.Server({ server });

const rooms = new Map();

wss.on('connection', (ws) => {
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      handleMessage(ws, data);
    } catch (e) {
      console.error('Invalid message');
    }
  });
  
  ws.on('close', () => {
    rooms.forEach((room, roomId) => {
      const idx = room.players.indexOf(ws);
      if (idx !== -1) {
        room.players.splice(idx, 1);
        if (room.players.length === 0) {
          rooms.delete(roomId);
        }
      }
    });
  });
});

function handleMessage(ws, data) {
  const { type, roomId } = data;
  if (!roomId) return;
  
  let room = rooms.get(roomId);
  if (!room && type !== 'join') return;
  
  switch (type) {
    case 'join': {
      if (!room) {
        room = {
          players: [],
          scores: [0, 0],
          turn: 0,
          questions: null,
          currentIndex: 0,
          chat: []
        };
        rooms.set(roomId, room);
      }
      if (room.players.length >= 2) {
        ws.send(JSON.stringify({ type: 'error', message: 'الغرفة مكتملة' }));
        return;
      }
      room.players.push(ws);
      ws.send(JSON.stringify({ type: 'joined', role: room.players.length - 1, roomId }));
      
      if (room.players.length === 2) {
        // إرسال إشارة البدء للمضيف (role 0) لتوليد الأسئلة
        const hostWs = room.players[0];
        hostWs.send(JSON.stringify({ type: 'start', turn: 0 }));
      }
      break;
    }
    case 'state': {
      // المضيف يرسل الأسئلة بعد خلطها
      if (room && ws === room.players[0]) {
        room.questions = data.questions;
        // إرسال الأسئلة للضيف
        if (room.players[1]) {
          room.players[1].send(JSON.stringify({
            type: 'state',
            questions: room.questions
          }));
        }
      }
      break;
    }
    case 'answer': {
      if (!room || room.players[room.turn] !== ws) return;
      const { correct, questionIndex } = data;
      if (correct) room.scores[room.turn]++;
      room.turn = 1 - room.turn;
      room.currentIndex = questionIndex + 1;
      broadcast(room, {
        type: 'answer',
        correct,
        scores: room.scores,
        turn: room.turn,
        currentIndex: room.currentIndex
      });
      break;
    }
    case 'chat': {
      if (!room) return;
      const { text, sender } = data;
      const chatMsg = { sender, text, time: Date.now() };
      room.chat.push(chatMsg);
      if (room.chat.length > 100) room.chat.shift();
      broadcast(room, { type: 'chat', chat: chatMsg });
      break;
    }
    case 'reset': {
      if (!room) return;
      room.scores = [0, 0];
      room.turn = 0;
      room.currentIndex = 0;
      room.questions = null;
      broadcast(room, {
        type: 'reset',
        scores: [0, 0],
        turn: 0,
        currentIndex: 0
      });
      break;
    }
  }
}

function broadcast(room, message) {
  const json = JSON.stringify(message);
  room.players.forEach(ws => {
    if (ws.readyState === WebSocket.OPEN) ws.send(json);
  });
}

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));