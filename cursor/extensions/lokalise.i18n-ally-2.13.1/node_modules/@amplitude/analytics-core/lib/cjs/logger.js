Object.defineProperty(exports, "__esModule", { value: true });
exports.Logger = void 0;
var analytics_types_1 = require("@amplitude/analytics-types");
var PREFIX = 'Amplitude Logger ';
var Logger = /** @class */ (function () {
    function Logger() {
        this.logLevel = analytics_types_1.LogLevel.None;
    }
    Logger.prototype.disable = function () {
        this.logLevel = analytics_types_1.LogLevel.None;
    };
    Logger.prototype.enable = function (logLevel) {
        if (logLevel === void 0) { logLevel = analytics_types_1.LogLevel.Warn; }
        this.logLevel = logLevel;
    };
    Logger.prototype.log = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (this.logLevel < analytics_types_1.LogLevel.Verbose) {
            return;
        }
        console.log("".concat(PREFIX, "[Log]: ").concat(args.join(' ')));
    };
    Logger.prototype.warn = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (this.logLevel < analytics_types_1.LogLevel.Warn) {
            return;
        }
        console.warn("".concat(PREFIX, "[Warn]: ").concat(args.join(' ')));
    };
    Logger.prototype.error = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (this.logLevel < analytics_types_1.LogLevel.Error) {
            return;
        }
        console.error("".concat(PREFIX, "[Error]: ").concat(args.join(' ')));
    };
    Logger.prototype.debug = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (this.logLevel < analytics_types_1.LogLevel.Debug) {
            return;
        }
        // console.debug output is hidden by default in chrome
        console.log("".concat(PREFIX, "[Debug]: ").concat(args.join(' ')));
    };
    return Logger;
}());
exports.Logger = Logger;
//# sourceMappingURL=logger.js.map