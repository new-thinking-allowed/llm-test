import { WebSocketServer } from 'ws';

// Create a new WebSocket server that listens on port 8080
const wss = new WebSocketServer( { port: 8080 } );
console.log( 'WebSocket server started on ws://localhost:8080' );

// When a client connects, send a welcome message
wss.on( 'connection', ( ws ) => {
  console.log( 'Client connected' );
  ws.send( JSON.stringify( { type: 'welcome', text: 'Hello! I\'m your local chatbot.' } ) );

  // Handle incoming messages from the client
  ws.on( 'message', ( message ) => {
    console.log( `Received message: ${ message }` );
    // Process the message and send a response back to the client
    const response = { type: 'response', text: `You said: ${ message }` };
    ws.send( JSON.stringify( response ) );
  } );

  // Handle disconnections
  ws.on( 'close', () => {
    console.log( 'Client disconnected' );
  } );
} );
