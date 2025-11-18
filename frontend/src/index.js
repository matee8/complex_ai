const socket = new WebSocket('ws://localhost:8000/ws/stocks/');

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};
