Object.defineProperty(exports, "__esModule", { value: true });
exports.EventBridgeContainer = void 0;
var event_bridge_1 = require("./event-bridge");
var EventBridgeContainer = /** @class */ (function () {
    function EventBridgeContainer() {
    }
    EventBridgeContainer.getInstance = function (instanceName) {
        if (!this.instances[instanceName]) {
            this.instances[instanceName] = new event_bridge_1.EventBridge();
        }
        return this.instances[instanceName];
    };
    EventBridgeContainer.instances = {};
    return EventBridgeContainer;
}());
exports.EventBridgeContainer = EventBridgeContainer;
//# sourceMappingURL=event-bridge-container.js.map