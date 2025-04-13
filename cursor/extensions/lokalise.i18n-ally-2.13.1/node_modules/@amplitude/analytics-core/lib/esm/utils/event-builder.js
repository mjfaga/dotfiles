import { __assign } from "tslib";
import { SpecialEventType, } from '@amplitude/analytics-types';
import { Identify } from '../identify';
export var createTrackEvent = function (eventInput, eventProperties, eventOptions) {
    var baseEvent = typeof eventInput === 'string' ? { event_type: eventInput } : eventInput;
    return __assign(__assign(__assign({}, baseEvent), eventOptions), (eventProperties && { event_properties: eventProperties }));
};
export var createIdentifyEvent = function (identify, eventOptions) {
    var identifyEvent = __assign(__assign({}, eventOptions), { event_type: SpecialEventType.IDENTIFY, user_properties: identify.getUserProperties() });
    return identifyEvent;
};
export var createGroupIdentifyEvent = function (groupType, groupName, identify, eventOptions) {
    var _a;
    var groupIdentify = __assign(__assign({}, eventOptions), { event_type: SpecialEventType.GROUP_IDENTIFY, group_properties: identify.getUserProperties(), groups: (_a = {},
            _a[groupType] = groupName,
            _a) });
    return groupIdentify;
};
export var createGroupEvent = function (groupType, groupName, eventOptions) {
    var _a;
    var identify = new Identify();
    identify.set(groupType, groupName);
    var groupEvent = __assign(__assign({}, eventOptions), { event_type: SpecialEventType.IDENTIFY, user_properties: identify.getUserProperties(), groups: (_a = {},
            _a[groupType] = groupName,
            _a) });
    return groupEvent;
};
export var createRevenueEvent = function (revenue, eventOptions) {
    return __assign(__assign({}, eventOptions), { event_type: SpecialEventType.REVENUE, event_properties: revenue.getEventProperties() });
};
//# sourceMappingURL=event-builder.js.map