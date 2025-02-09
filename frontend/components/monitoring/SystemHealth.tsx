import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface SystemHealthProps {
    health: {
        status: string;
        health: {
            price_feed: string;
            position_monitoring: string;
            active_monitors: number;
            recent_errors: Array<{
                timestamp: string;
                error: string;
            }>;
            last_price_update: string;
            last_position_check: string;
        };
    };
}

export function SystemHealth({ health }: SystemHealthProps) {
    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'healthy':
                return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'warning':
                return <AlertCircle className="h-4 w-4 text-yellow-500" />;
            default:
                return <AlertCircle className="h-4 w-4 text-red-500" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy':
                return 'bg-green-100 text-green-800';
            case 'warning':
                return 'bg-yellow-100 text-yellow-800';
            default:
                return 'bg-red-100 text-red-800';
        }
    };

    const formatTimestamp = (timestamp: string) => {
        if (!timestamp) return 'N/A';
        const date = new Date(timestamp);
        return date.toLocaleString();
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    System Health
                    <Badge variant="outline" className={getStatusColor(health.status)}>
                        {health.status.toUpperCase()}
                    </Badge>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                        {getStatusIcon(health.health.price_feed)}
                        <span>Price Feed</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        {getStatusIcon(health.health.position_monitoring)}
                        <span>Position Monitoring</span>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm text-gray-500">
                    <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4" />
                        <span>Last Price Update:</span>
                        <span>{formatTimestamp(health.health.last_price_update)}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4" />
                        <span>Last Position Check:</span>
                        <span>{formatTimestamp(health.health.last_position_check)}</span>
                    </div>
                </div>

                <div>
                    <Badge variant="secondary">
                        Active Monitors: {health.health.active_monitors}
                    </Badge>
                </div>

                {health.health.recent_errors.length > 0 && (
                    <Alert variant="destructive">
                        <AlertDescription>
                            <div className="text-sm font-semibold mb-2">Recent Errors:</div>
                            <ul className="list-disc pl-4 space-y-1">
                                {health.health.recent_errors.map((error, index) => (
                                    <li key={index} className="text-sm">
                                        {formatTimestamp(error.timestamp)}: {error.error}
                                    </li>
                                ))}
                            </ul>
                        </AlertDescription>
                    </Alert>
                )}
            </CardContent>
        </Card>
    );
} 