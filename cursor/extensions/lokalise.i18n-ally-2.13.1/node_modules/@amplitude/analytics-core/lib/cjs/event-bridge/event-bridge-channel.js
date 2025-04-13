Object.defineProperty(exports, "__esModule", { value: true });
exports.EventBridgeChannel = void 0;
var tslib_1 = require("tslib");
var QUEUE_CAPACITY = 512;
var EventBridgeChannel = /** @class */ (function () {
    function EventBridgeChannel(channel) {
        this.queue = [];
        this.channel = channel;
    }
    EventBridgeChannel.prototype.sendEvent = function (event) {
        if (!this.receiver) {
            this.queue = tslib_1.__spreadArray(tslib_1.__spreadArray([], tslib_1.__read(this.queue.slice(0, QUEUE_CAPACITY)), false), [event], false);
            return;
        }
        this.receiver.receive(this.channel, event);
    };
    EventBridgeChannel.prototype.setReceiver = function (receiver) {
        var _this = this;
        if (this.receiver) {
            return;
        }
        this.receiver = receiver;
        var events = this.queue;
        this.queue = [];
        events.forEach(function (event) {
            _this.receiver.receive(_this.channel, event);
        });
    };
    return EventBridgeChannel;
}());
exports.EventBridgeChannel = EventBridgeChannel;
//# sourceMappingURL=event-bridge-channel.js.map