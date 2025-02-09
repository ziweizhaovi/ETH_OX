import React from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Bell, AlertTriangle, AlertCircle } from 'lucide-react';

interface Notification {
    type: string;
    message: string;
    priority: string;
    data?: any;
    timestamp: string;
}

interface NotificationListProps {
    notifications: Notification[];
}

export function NotificationList({ notifications }: NotificationListProps) {
    const getPriorityColor = (priority: string) => {
        switch (priority.toLowerCase()) {
            case 'low':
                return 'bg-blue-100 text-blue-800';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800';
            case 'high':
                return 'bg-orange-100 text-orange-800';
            case 'critical':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const getNotificationIcon = (type: string) => {
        switch (type.toLowerCase()) {
            case 'position_update':
            case 'order_executed':
                return <Bell className="h-4 w-4" />;
            case 'liquidation_risk':
                return <AlertCircle className="h-4 w-4 text-red-500" />;
            case 'system_alert':
                return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
            default:
                return <Bell className="h-4 w-4" />;
        }
    };

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleString();
    };

    const formatData = (data: any) => {
        if (!data) return null;

        const entries = Object.entries(data)
            .filter(([key]) => !['type', 'message', 'priority'].includes(key))
            .map(([key, value]) => {
                // Format key
                const formattedKey = key.split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');

                // Format value
                let formattedValue = value;
                if (typeof value === 'number') {
                    formattedValue = value.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    });
                }

                return `${formattedKey}: ${formattedValue}`;
            });

        return entries.length > 0 ? entries.join(' | ') : null;
    };

    if (notifications.length === 0) {
        return (
            <div className="text-center text-gray-500 py-8">
                No notifications yet
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {notifications.map((notification, index) => (
                <Alert key={index} className="relative">
                    <div className="flex items-center gap-2">
                        {getNotificationIcon(notification.type)}
                        <Badge 
                            variant="outline"
                            className={getPriorityColor(notification.priority)}
                        >
                            {notification.priority.toUpperCase()}
                        </Badge>
                        <span className="text-xs text-gray-500">
                            {formatTimestamp(notification.timestamp)}
                        </span>
                    </div>
                    <AlertTitle className="mt-2">
                        {notification.type.split('_').map(word => 
                            word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')}
                    </AlertTitle>
                    <AlertDescription className="mt-1">
                        <p>{notification.message}</p>
                        {notification.data && (
                            <p className="text-sm text-gray-500 mt-1">
                                {formatData(notification.data)}
                            </p>
                        )}
                    </AlertDescription>
                </Alert>
            ))}
        </div>
    );
} 