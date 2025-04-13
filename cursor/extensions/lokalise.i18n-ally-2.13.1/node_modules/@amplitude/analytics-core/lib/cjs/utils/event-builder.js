Object.defineProperty(exports, "__esModule", { value: true });
exports.createRevenueEvent = exports.createGroupEvent = exports.createGroupIdentifyEvent = exports.createIdentifyEvent = exports.createTrackEvent = void 0;
var tslib_1 = require("tslib");
var analytics_types_1 = require("@amplitude/analytics-types");
var identify_1 = require("../identify");
var createTrackEvent = function (eventInput, eventProperties, eventOptions) {
    var baseEvent = typeof eventInput === 'string' ? { event_type: eventInput } : eventInput;
    return tslib_1.__assign(tslib_1.__assign(tslib_1.__assign({}, baseEvent), eventOptions), (eventProperties && { event_properties: eventProperties }));
};
exports.createTrackEvent = createTrackEvent;
var createIdentifyEvent = function (identify, eventOptions) {
    var identifyEvent = tslib_1.__assign(tslib_1.__assign({}, eventOptions), { event_type: analytics_types_1.SpecialEventType.IDENTIFY, user_properties: identify.getUserProperties() });
    return identifyEvent;
};
exports.createIdentifyEvent = createIdentifyEvent;
var createGroupIdentifyEvent = function (groupType, groupName, identify, eventOptions) {
    var _a;
    var groupIdentify = tslib_1.__assign(tslib_1.__assign({}, eventOptions), { event_type: analytics_types_1.SpecialEventType.GROUP_IDENTIFY, group_properties: identify.getUserProperties(), groups: (_a = {},
            _a[groupType] = groupName,
            _a) });
    return groupIdentify;
};
exports.createGroupIdentifyEvent = createGroupIdentifyEvent;
var createGroupEvent = function (groupType, groupName, eventOptions) {
    var _a;
    var identify = new identify_1.Identify();
    identify.set(groupType, groupName);
    var groupEvent = tslib_1.__assign(tslib_1.__assign({}, eventOptions), { event_type: analytics_types_1.SpecialEventType.IDENTIFY, user_properties: identify.getUserProperties(), groups: (_a = {},
            _a[groupType] = groupName,
            _a) });
    return groupEvent;
};
exports.createGroupEvent = createGroupEvent;
var createRevenueEvent = function (revenue, eventOptions) {
    return tslib_1.__assign(tslib_1.__assign({}, eventOptions), { event_type: analytics_types_1.SpecialEventType.REVENUE, event_properties: revenue.getEventProperties() });
};
exports.createRevenueEvent = createRevenueEvent;
//# sourceMappingURL=event-builder.js.map