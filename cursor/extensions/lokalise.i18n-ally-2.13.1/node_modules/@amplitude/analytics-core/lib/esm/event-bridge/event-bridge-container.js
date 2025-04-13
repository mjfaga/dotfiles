import { EventBridge } from './event-bridge';
var EventBridgeContainer = /** @class */ (function () {
    function EventBridgeContainer() {
    }
    EventBridgeContainer.getInstance = function (instanceName) {
        if (!this.instances[instanceName]) {
            this.instances[instanceName] = new EventBridge();
        }
        return this.instances[instanceName];
    };
    EventBridgeContainer.instances = {};
    return EventBridgeContainer;
}());
export { EventBridgeContainer };
//# sourceMappingURL=event-bridge-container.js.map