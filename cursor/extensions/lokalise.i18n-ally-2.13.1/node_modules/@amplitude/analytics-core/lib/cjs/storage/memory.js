Object.defineProperty(exports, "__esModule", { value: true });
exports.MemoryStorage = void 0;
var tslib_1 = require("tslib");
var MemoryStorage = /** @class */ (function () {
    function MemoryStorage() {
        this.memoryStorage = new Map();
    }
    MemoryStorage.prototype.isEnabled = function () {
        return tslib_1.__awaiter(this, void 0, void 0, function () {
            return tslib_1.__generator(this, function (_a) {
                return [2 /*return*/, true];
            });
        });
    };
    MemoryStorage.prototype.get = function (key) {
        return tslib_1.__awaiter(this, void 0, void 0, function () {
            return tslib_1.__generator(this, function (_a) {
                return [2 /*return*/, this.memoryStorage.get(key)];
            });
        });
    };
    MemoryStorage.prototype.getRaw = function (key) {
        return tslib_1.__awaiter(this, void 0, void 0, function () {
            var value;
            return tslib_1.__generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.get(key)];
                    case 1:
                        value = _a.sent();
                        return [2 /*return*/, value ? JSON.stringify(value) : undefined];
                }
            });
        });
    };
    MemoryStorage.prototype.set = function (key, value) {
        return tslib_1.__awaiter(this, void 0, void 0, function () {
            return tslib_1.__generator(this, function (_a) {
                this.memoryStorage.set(key, value);
                return [2 /*return*/];
            });
        });
    };
    MemoryStorage.prototype.remove = function (key) {
        return tslib_1.__awaiter(this, void 0, void 0, function () {
            return tslib_1.__generator(this, function (_a) {
                this.memoryStorage.delete(key);
                return [2 /*return*/];
            });
        });
    };
    MemoryStorage.prototype.reset = function () {
        return tslib_1.__awaiter(this, void 0, void 0, function () {
            return tslib_1.__generator(this, function (_a) {
                this.memoryStorage.clear();
                return [2 /*return*/];
            });
        });
    };
    return MemoryStorage;
}());
exports.MemoryStorage = MemoryStorage;
//# sourceMappingURL=memory.js.map