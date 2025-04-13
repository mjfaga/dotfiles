import { __read, __spreadArray } from "tslib";
var QUEUE_CAPACITY = 512;
var EventBridgeChannel = /** @class */ (function () {
    function EventBridgeChannel(channel) {
        this.queue = [];
        this.channel = channel;
    }
    EventBridgeChannel.prototype.sendEvent = function (event) {
        if (!this.receiver) {
            this.queue = __spreadArray(__spreadArray([], __read(this.queue.slice(0, QUEUE_CAPACITY)), false), [event], false);
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
export { EventBridgeChannel };
//# sourceMappingURL=event-bridge-channel.js.map