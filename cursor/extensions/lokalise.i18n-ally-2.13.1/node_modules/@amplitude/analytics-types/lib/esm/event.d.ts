import { BaseEvent } from './base-event';
export interface Identify {
    getUserProperties(): IdentifyUserProperties;
    set(property: string, value: ValidPropertyType): Identify;
    setOnce(property: string, value: ValidPropertyType): Identify;
    append(property: string, value: ValidPropertyType): Identify;
    prepend(property: string, value: ValidPropertyType): Identify;
    postInsert(property: string, value: ValidPropertyType): Identify;
    preInsert(property: string, value: ValidPropertyType): Identify;
    remove(property: string, value: ValidPropertyType): Identify;
    add(property: string, value: number): Identify;
    unset(property: string): Identify;
    clearAll(): Identify;
}
export declare enum IdentifyOperation {
    SET = "$set",
    SET_ONCE = "$setOnce",
    ADD = "$add",
    APPEND = "$append",
    PREPEND = "$prepend",
    REMOVE = "$remove",
    PREINSERT = "$preInsert",
    POSTINSERT = "$postInsert",
    UNSET = "$unset",
    CLEAR_ALL = "$clearAll"
}
export type ValidPropertyType = number | string | boolean | Array<string | number> | {
    [key: string]: ValidPropertyType;
};
interface BaseOperationConfig {
    [key: string]: ValidPropertyType;
}
export interface IdentifyUserProperties {
    [IdentifyOperation.ADD]?: {
        [key: string]: number;
    };
    [IdentifyOperation.UNSET]?: BaseOperationConfig;
    [IdentifyOperation.CLEAR_ALL]?: any;
    [IdentifyOperation.SET]?: BaseOperationConfig;
    [IdentifyOperation.SET_ONCE]?: BaseOperationConfig;
    [IdentifyOperation.APPEND]?: BaseOperationConfig;
    [IdentifyOperation.PREPEND]?: BaseOperationConfig;
    [IdentifyOperation.POSTINSERT]?: BaseOperationConfig;
    [IdentifyOperation.PREINSERT]?: BaseOperationConfig;
    [IdentifyOperation.REMOVE]?: BaseOperationConfig;
}
export interface Revenue {
    getEventProperties(): RevenueEventProperties;
    setProductId(productId: string): Revenue;
    setQuantity(quantity: number): Revenue;
    setPrice(price: number): Revenue;
    setRevenueType(revenueType: string): Revenue;
    setEventProperties(properties: {
        [key: string]: any;
    }): Revenue;
    setRevenue(revenue: number): Revenue;
}
export declare enum RevenueProperty {
    REVENUE_PRODUCT_ID = "$productId",
    REVENUE_QUANTITY = "$quantity",
    REVENUE_PRICE = "$price",
    REVENUE_TYPE = "$revenueType",
    REVENUE = "$revenue"
}
export interface RevenueEventProperties {
    [RevenueProperty.REVENUE_PRODUCT_ID]?: string;
    [RevenueProperty.REVENUE_QUANTITY]?: number;
    [RevenueProperty.REVENUE_PRICE]?: number;
    [RevenueProperty.REVENUE_TYPE]?: string;
    [RevenueProperty.REVENUE_TYPE]?: string;
    [RevenueProperty.REVENUE]?: number;
}
/**
 * Strings that have special meaning when used as an event's type
 * and have different specifications.
 */
export declare enum SpecialEventType {
    IDENTIFY = "$identify",
    GROUP_IDENTIFY = "$groupidentify",
    REVENUE = "revenue_amount"
}
export interface TrackEvent extends BaseEvent {
    event_type: Exclude<string, SpecialEventType>;
}
export interface IdentifyEvent extends BaseEvent {
    event_type: SpecialEventType.IDENTIFY;
    user_properties: IdentifyUserProperties | {
        [key in Exclude<string, IdentifyOperation>]: any;
    };
}
export interface GroupIdentifyEvent extends BaseEvent {
    event_type: SpecialEventType.GROUP_IDENTIFY;
    group_properties: IdentifyUserProperties | {
        [key in Exclude<string, IdentifyOperation>]: any;
    };
}
export interface RevenueEvent extends BaseEvent {
    event_type: SpecialEventType.REVENUE;
    event_properties: RevenueEventProperties | {
        [key: string]: any;
    };
}
export type Event = TrackEvent | IdentifyEvent | GroupIdentifyEvent | RevenueEvent;
export {};
//# sourceMappingURL=event.d.ts.map