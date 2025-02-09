import React, { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/use-websocket';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PriceAlertForm } from './PriceAlertForm';
import { SystemHealth } from './SystemHealth';
import { NotificationList } from './NotificationList';

interface MonitoringDashboardProps {
    walletAddress: string;
}

export function MonitoringDashboard({ walletAddress }: MonitoringDashboardProps) {
    const [isMonitoring, setIsMonitoring] = useState(false);
    const [notifications, setNotifications] = useState<any[]>([]);
    const [systemHealth, setSystemHealth] = useState<any>(null);
    const { toast } = useToast();

    // Initialize WebSocket connection
    const { lastMessage, sendMessage } = useWebSocket(
        `ws://localhost:8000/ws/monitor/${walletAddress}`
    );

    // Handle incoming WebSocket messages
    useEffect(() => {
        if (lastMessage) {
            const data = JSON.parse(lastMessage.data);
            if (data.type === 'notification') {
                setNotifications(prev => [data.data, ...prev]);
                
                // Show toast for high priority notifications
                if (data.data.priority === 'high' || data.data.priority === 'critical') {
                    toast({
                        title: 'Important Alert',
                        description: data.data.message,
                        variant: 'destructive',
                    });
                }
            }
        }
    }, [lastMessage, toast]);

    // Fetch system health status periodically
    useEffect(() => {
        const fetchHealth = async () => {
            try {
                const response = await fetch(
                    `/api/monitor/health/${walletAddress}`
                );
                const data = await response.json();
                setSystemHealth(data);
            } catch (error) {
                console.error('Failed to fetch system health:', error);
            }
        };

        if (isMonitoring) {
            fetchHealth();
            const interval = setInterval(fetchHealth, 30000); // Every 30 seconds
            return () => clearInterval(interval);
        }
    }, [walletAddress, isMonitoring]);

    // Start monitoring
    const handleStartMonitoring = async () => {
        try {
            const response = await fetch(
                `/api/monitor/start/${walletAddress}`,
                { method: 'POST' }
            );
            const data = await response.json();
            
            if (data.status === 'success') {
                setIsMonitoring(true);
                toast({
                    title: 'Monitoring Started',
                    description: 'Successfully started position monitoring',
                });
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to start monitoring',
                variant: 'destructive',
            });
        }
    };

    // Stop monitoring
    const handleStopMonitoring = async () => {
        try {
            const response = await fetch(
                `/api/monitor/stop/${walletAddress}`,
                { method: 'POST' }
            );
            const data = await response.json();
            
            if (data.status === 'success') {
                setIsMonitoring(false);
                toast({
                    title: 'Monitoring Stopped',
                    description: 'Successfully stopped position monitoring',
                });
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to stop monitoring',
                variant: 'destructive',
            });
        }
    };

    return (
        <div className="container mx-auto p-4 space-y-4">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">Position Monitoring</h1>
                <Button
                    onClick={isMonitoring ? handleStopMonitoring : handleStartMonitoring}
                    variant={isMonitoring ? "destructive" : "default"}
                >
                    {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
                </Button>
            </div>

            {systemHealth && (
                <SystemHealth health={systemHealth} />
            )}

            <Tabs defaultValue="notifications" className="w-full">
                <TabsList>
                    <TabsTrigger value="notifications">
                        Notifications
                        {notifications.length > 0 && (
                            <Badge variant="secondary" className="ml-2">
                                {notifications.length}
                            </Badge>
                        )}
                    </TabsTrigger>
                    <TabsTrigger value="alerts">Price Alerts</TabsTrigger>
                </TabsList>

                <TabsContent value="notifications">
                    <Card>
                        <CardHeader>
                            <CardTitle>Recent Notifications</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ScrollArea className="h-[400px]">
                                <NotificationList notifications={notifications} />
                            </ScrollArea>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="alerts">
                    <Card>
                        <CardHeader>
                            <CardTitle>Price Alerts</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <PriceAlertForm walletAddress={walletAddress} />
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
} 