import WebSocket from 'ws';
import { IncomingMessage } from 'http';
import jwt from 'jsonwebtoken';

interface AuthenticatedWebSocket extends WebSocket {
  userId?: string;
  schoolId?: string;
  role?: string;
}

export class WebSocketService {
  private wss: WebSocket.Server;
  private clients: Map<string, AuthenticatedWebSocket> = new Map();

  constructor(server: any) {
    this.wss = new WebSocket.Server({ 
      server,
      path: '/ws'
    });

    this.wss.on('connection', this.handleConnection.bind(this));
    console.log('WebSocket server initialized');
  }

  /**
   * Handle new WebSocket connection
   */
  private async handleConnection(ws: AuthenticatedWebSocket, req: IncomingMessage) {
    try {
      // Extract token from query parameters or headers
      const url = new URL(req.url!, `http://${req.headers.host}`);
      const token = url.searchParams.get('token') || req.headers.authorization?.replace('Bearer ', '');

      if (!token) {
        ws.close(1008, 'Authentication required');
        return;
      }

      // Verify JWT token
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
      
      ws.userId = decoded.userId;
      ws.schoolId = decoded.schoolId;
      ws.role = decoded.role;

      // Store client connection
      this.clients.set(decoded.userId, ws);

      // Send welcome message
      this.sendToClient(ws, {
        type: 'CONNECTION_ESTABLISHED',
        data: {
          userId: decoded.userId,
          timestamp: new Date().toISOString()
        }
      });

      // Handle client messages
      ws.on('message', (message: string) => {
        this.handleMessage(ws, message);
      });

      // Handle client disconnect
      ws.on('close', () => {
        this.clients.delete(decoded.userId);
        console.log(`WebSocket client disconnected: ${decoded.userId}`);
      });

      // Handle errors
      ws.on('error', (error) => {
        console.error(`WebSocket error for user ${decoded.userId}:`, error);
        this.clients.delete(decoded.userId);
      });

      console.log(`WebSocket client connected: ${decoded.userId}`);

    } catch (error) {
      console.error('WebSocket authentication error:', error);
      ws.close(1008, 'Authentication failed');
    }
  }

  /**
   * Handle incoming messages from clients
   */
  private handleMessage(ws: AuthenticatedWebSocket, message: string) {
    try {
      const data = JSON.parse(message);
      
      switch (data.type) {
        case 'PING':
          this.sendToClient(ws, { type: 'PONG', data: { timestamp: new Date().toISOString() } });
          break;
          
        case 'SUBSCRIBE_WELLNESS':
          // Subscribe to wellness updates for specific teachers
          this.handleWellnessSubscription(ws, data.data);
          break;
          
        case 'SUBSCRIBE_ALERTS':
          // Subscribe to alert notifications
          this.handleAlertSubscription(ws, data.data);
          break;
          
        default:
          console.log(`Unknown message type: ${data.type}`);
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
    }
  }

  /**
   * Send message to a specific user
   */
  async sendToUser(userId: string, message: any) {
    const client = this.clients.get(userId);
    if (client && client.readyState === WebSocket.OPEN) {
      this.sendToClient(client, message);
      return true;
    }
    return false;
  }

  /**
   * Send message to all users in a school
   */
  async sendToSchool(schoolId: string, message: any, excludeUserId?: string) {
    let sentCount = 0;
    
    for (const [userId, client] of this.clients.entries()) {
      if (client.schoolId === schoolId && 
          userId !== excludeUserId && 
          client.readyState === WebSocket.OPEN) {
        this.sendToClient(client, message);
        sentCount++;
      }
    }
    
    return sentCount;
  }

  /**
   * Send message to users with specific roles
   */
  async sendToRole(schoolId: string, roles: string[], message: any) {
    let sentCount = 0;
    
    for (const [userId, client] of this.clients.entries()) {
      if (client.schoolId === schoolId && 
          client.role && 
          roles.includes(client.role) && 
          client.readyState === WebSocket.OPEN) {
        this.sendToClient(client, message);
        sentCount++;
      }
    }
    
    return sentCount;
  }

  /**
   * Broadcast wellness alert to relevant users
   */
  async broadcastWellnessAlert(alert: any) {
    const message = {
      type: 'WELLNESS_ALERT',
      data: {
        id: alert.id,
        teacherId: alert.teacherId,
        severity: alert.severity,
        title: alert.title,
        message: alert.message,
        timestamp: new Date().toISOString()
      }
    };

    // Send to the teacher
    await this.sendToUser(alert.teacher.userId, {
      ...message,
      data: {
        ...message.data,
        isPersonal: true
      }
    });

    // Send to administrators
    await this.sendToRole(alert.teacher.user.schoolId, ['ADMIN', 'PRINCIPAL'], message);
  }

  /**
   * Broadcast wellness metrics update
   */
  async broadcastWellnessUpdate(teacherId: string, schoolId: string, metrics: any) {
    const message = {
      type: 'WELLNESS_METRICS_UPDATE',
      data: {
        teacherId,
        wellnessScore: metrics.wellnessScore,
        burnoutRisk: metrics.burnoutRisk,
        timestamp: new Date().toISOString()
      }
    };

    // Send to the teacher
    await this.sendToUser(teacherId, message);

    // Send to administrators
    await this.sendToRole(schoolId, ['ADMIN', 'PRINCIPAL'], message);
  }

  /**
   * Send real-time timetable update
   */
  async broadcastTimetableUpdate(schoolId: string, update: any) {
    const message = {
      type: 'TIMETABLE_UPDATE',
      data: {
        ...update,
        timestamp: new Date().toISOString()
      }
    };

    await this.sendToSchool(schoolId, message);
  }

  /**
   * Send system notification
   */
  async sendSystemNotification(schoolId: string, notification: any) {
    const message = {
      type: 'SYSTEM_NOTIFICATION',
      data: {
        ...notification,
        timestamp: new Date().toISOString()
      }
    };

    await this.sendToSchool(schoolId, message);
  }

  /**
   * Get connected users count
   */
  getConnectedUsersCount(schoolId?: string): number {
    if (!schoolId) {
      return this.clients.size;
    }
    
    let count = 0;
    for (const client of this.clients.values()) {
      if (client.schoolId === schoolId) {
        count++;
      }
    }
    return count;
  }

  /**
   * Get connected users by role
   */
  getConnectedUsersByRole(schoolId: string): Record<string, number> {
    const roleCount: Record<string, number> = {};
    
    for (const client of this.clients.values()) {
      if (client.schoolId === schoolId && client.role) {
        roleCount[client.role] = (roleCount[client.role] || 0) + 1;
      }
    }
    
    return roleCount;
  }

  /**
   * Private helper methods
   */
  private sendToClient(client: AuthenticatedWebSocket, message: any) {
    try {
      client.send(JSON.stringify(message));
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
    }
  }

  private handleWellnessSubscription(ws: AuthenticatedWebSocket, data: any) {
    // Store subscription preferences (could be enhanced with Redis for persistence)
    console.log(`User ${ws.userId} subscribed to wellness updates:`, data);
    
    this.sendToClient(ws, {
      type: 'SUBSCRIPTION_CONFIRMED',
      data: {
        type: 'wellness',
        subscriptions: data
      }
    });
  }

  private handleAlertSubscription(ws: AuthenticatedWebSocket, data: any) {
    console.log(`User ${ws.userId} subscribed to alert updates:`, data);
    
    this.sendToClient(ws, {
      type: 'SUBSCRIPTION_CONFIRMED',
      data: {
        type: 'alerts',
        subscriptions: data
      }
    });
  }

  /**
   * Cleanup and shutdown
   */
  shutdown() {
    console.log('Shutting down WebSocket service...');
    
    // Close all client connections
    for (const client of this.clients.values()) {
      client.close(1001, 'Server shutting down');
    }
    
    // Close the server
    this.wss.close(() => {
      console.log('WebSocket server closed');
    });
  }

  /**
   * Health check for WebSocket service
   */
  healthCheck() {
    return {
      status: 'healthy',
      connectedClients: this.clients.size,
      serverState: this.wss.readyState === WebSocket.OPEN ? 'open' : 'closed'
    };
  }
}