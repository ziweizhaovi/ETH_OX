import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';

const formSchema = z.object({
    price_level: z.string().refine((val) => !isNaN(Number(val)) && Number(val) > 0, {
        message: "Price must be a positive number",
    }),
    alert_type: z.enum(['above', 'below']),
    expiry_hours: z.string().refine((val) => !isNaN(Number(val)) && Number(val) >= 0, {
        message: "Hours must be a non-negative number",
    }),
});

interface PriceAlertFormProps {
    walletAddress: string;
}

export function PriceAlertForm({ walletAddress }: PriceAlertFormProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { toast } = useToast();

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            price_level: '',
            alert_type: 'above',
            expiry_hours: '24',
        },
    });

    const onSubmit = async (values: z.infer<typeof formSchema>) => {
        try {
            setIsSubmitting(true);

            // Calculate expiry time
            const expiry = new Date();
            expiry.setHours(expiry.getHours() + Number(values.expiry_hours));

            const response = await fetch(`/api/monitor/alerts/add/${walletAddress}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    price_level: Number(values.price_level),
                    alert_type: values.alert_type,
                    expiry: values.expiry_hours === '0' ? null : expiry.toISOString(),
                }),
            });

            const data = await response.json();

            if (data.status === 'success') {
                toast({
                    title: 'Alert Created',
                    description: `Price alert will trigger when AVAX goes ${values.alert_type} $${values.price_level}`,
                });
                form.reset();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to create price alert',
                variant: 'destructive',
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Card className="p-4">
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                        control={form.control}
                        name="price_level"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Price Level (USD)</FormLabel>
                                <FormControl>
                                    <Input
                                        placeholder="Enter price level"
                                        type="number"
                                        step="0.01"
                                        min="0"
                                        {...field}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="alert_type"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Alert Type</FormLabel>
                                <Select
                                    onValueChange={field.onChange}
                                    defaultValue={field.value}
                                >
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select alert type" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="above">Price Goes Above</SelectItem>
                                        <SelectItem value="below">Price Goes Below</SelectItem>
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="expiry_hours"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Expiry (Hours)</FormLabel>
                                <FormControl>
                                    <Input
                                        placeholder="Enter expiry in hours (0 for no expiry)"
                                        type="number"
                                        min="0"
                                        {...field}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <Button
                        type="submit"
                        className="w-full"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? 'Creating Alert...' : 'Create Price Alert'}
                    </Button>
                </form>
            </Form>
        </Card>
    );
} 