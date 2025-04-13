import { Event, EventBridgeReceiver, EventBridge as IEventBridge } from '@amplitude/analytics-types';
import { EventBridgeChannel } from './event-bridge-channel';
export declare class EventBridge implements IEventBridge {
    eventBridgeChannels: Record<string, EventBridgeChannel | undefined>;
    sendEvent(channel: string, event: Event): void;
    setReceiver(channel: string, receiver: EventBridgeReceiver): void;
}
//# sourceMappingURL=event-bridge.d.ts.map