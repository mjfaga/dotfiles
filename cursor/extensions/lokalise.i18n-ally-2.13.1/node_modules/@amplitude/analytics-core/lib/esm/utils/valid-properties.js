import { __values } from "tslib";
var MAX_PROPERTY_KEYS = 1000;
export var isValidObject = function (properties) {
    if (Object.keys(properties).length > MAX_PROPERTY_KEYS) {
        return false;
    }
    for (var key in properties) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        var value = properties[key];
        if (!isValidProperties(key, value))
            return false;
    }
    return true;
};
export var isValidProperties = function (property, value) {
    var e_1, _a;
    if (typeof property !== 'string')
        return false;
    if (Array.isArray(value)) {
        var isValid = true;
        try {
            for (var value_1 = __values(value), value_1_1 = value_1.next(); !value_1_1.done; value_1_1 = value_1.next()) {
                var valueElement = value_1_1.value;
                if (Array.isArray(valueElement)) {
                    return false;
                }
                else if (typeof valueElement === 'object') {
                    isValid = isValid && isValidObject(valueElement);
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
        return isValidObject(value);
    }
    else if (!['number', 'string', 'boolean'].includes(typeof value)) {
        return false;
    }
    return true;
};
//# sourceMappingURL=valid-properties.js.map