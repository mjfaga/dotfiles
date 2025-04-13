Object.defineProperty(exports, "__esModule", { value: true });
exports.isValidProperties = exports.isValidObject = void 0;
var tslib_1 = require("tslib");
var MAX_PROPERTY_KEYS = 1000;
var isValidObject = function (properties) {
    if (Object.keys(properties).length > MAX_PROPERTY_KEYS) {
        return false;
    }
    for (var key in properties) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        var value = properties[key];
        if (!(0, exports.isValidProperties)(key, value))
            return false;
    }
    return true;
};
exports.isValidObject = isValidObject;
var isValidProperties = function (property, value) {
    var e_1, _a;
    if (typeof property !== 'string')
        return false;
    if (Array.isArray(value)) {
        var isValid = true;
        try {
            for (var value_1 = tslib_1.__values(value), value_1_1 = value_1.next(); !value_1_1.done; value_1_1 = value_1.next()) {
                var valueElement = value_1_1.value;
                if (Array.isArray(valueElement)) {
                    return false;
                }
                else if (typeof valueElement === 'object') {
                    isValid = isValid && (0, exports.isValidObject)(valueElement);
                }
                else if (!['number', 'string'].includes(typeof valueElement)) {
                    return false;
                }
                if (!isValid) {
                    return false;
                }
            }
        }
        catch (e_1_1) { e_1 = { error: e_1_1 }; }
        finally {
            try {
                if (value_1_1 && !value_1_1.done && (_a = value_1.return)) _a.call(value_1);
            }
            finally { if (e_1) throw e_1.error; }
        }
    }
    else if (value === null || value === undefined) {
        return false;
    }
    else if (typeof value === 'object') {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
        return (0, exports.isValidObject)(value);
    }
    else if (!['number', 'string', 'boolean'].includes(typeof value)) {
        return false;
    }
    return true;
};
exports.isValidProperties = isValidProperties;
//# sourceMappingURL=valid-properties.js.map