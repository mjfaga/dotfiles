import { Event, EventBridgeReceiver } from '@amplitude/analytics-types';
export declare class EventBridgeChannel {
    channel: string;
    queue: Event[];
    receiver: EventBridgeReceiver | undefined;
    constructor(channel: string);
    sendEvent(event: Event): void;
    setReceiver(receiver: EventBridgeReceiver): void;
}
//# sourceMappingURL=event-bridge-channel.d.ts.map