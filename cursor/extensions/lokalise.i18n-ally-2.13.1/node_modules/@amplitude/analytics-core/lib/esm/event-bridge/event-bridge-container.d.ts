import { EventBridge as IEventBridge } from '@amplitude/analytics-types';
export declare class EventBridgeContainer {
    static instances: Record<string, IEventBridge>;
    static getInstance(instanceName: string): IEventBridge;
}
//# sourceMappingURL=event-bridge-container.d.ts.map