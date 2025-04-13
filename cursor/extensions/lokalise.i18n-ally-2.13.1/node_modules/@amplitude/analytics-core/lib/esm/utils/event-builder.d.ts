import { BaseEvent, TrackEvent, IdentifyEvent, GroupIdentifyEvent, Identify as IIdentify, Revenue, RevenueEvent, EventOptions } from '@amplitude/analytics-types';
export declare const createTrackEvent: (eventInput: BaseEvent | string, eventProperties?: Record<string, any>, eventOptions?: EventOptions) => TrackEvent;
export declare const createIdentifyEvent: (identify: IIdentify, eventOptions?: EventOptions) => IdentifyEvent;
export declare const createGroupIdentifyEvent: (groupType: string, groupName: string | string[], identify: IIdentify, eventOptions?: EventOptions) => GroupIdentifyEvent;
export declare const createGroupEvent: (groupType: string, groupName: string | string[], eventOptions?: EventOptions) => IdentifyEvent;
export declare const createRevenueEvent: (revenue: Revenue, eventOptions?: EventOptions) => RevenueEvent;
//# sourceMappingURL=event-builder.d.ts.map