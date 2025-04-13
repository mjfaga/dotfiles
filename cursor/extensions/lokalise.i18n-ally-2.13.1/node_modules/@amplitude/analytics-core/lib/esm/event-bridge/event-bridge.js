import { EventBridgeChannel } from './event-bridge-channel';
var EventBridge = /** @class */ (function () {
    function EventBridge() {
        this.eventBridgeChannels = {};
    }
    EventBridge.prototype.sendEvent = function (channel, event) {
        if (!this.eventBridgeChannels[channel]) {
            this.eventBridgeChannels[channel] = new EventBridgeChannel(channel);
        }
        this.eventBridgeChannels[channel].sendEvent(event);
    };
    EventBridge.prototype.setReceiver = function (channel, receiver) {
        if (!this.eventBridgeChannels[channel]) {
            this.eventBridgeChannels[channel] = new EventBridgeChannel(channel);
        }
        this.eventBridgeChannels[channel].setReceiver(receiver);
    };
    return EventBridge;
}());
export { EventBridge };
//# sourceMappingURL=event-bridge.js.map