Object.defineProperty(exports, "__esModule", { value: true });
exports.Identify = void 0;
var tslib_1 = require("tslib");
var analytics_types_1 = require("@amplitude/analytics-types");
var constants_1 = require("./constants");
var valid_properties_1 = require("./utils/valid-properties");
var Identify = /** @class */ (function () {
    function Identify() {
        this._propertySet = new Set();
        this._properties = {};
    }
    Identify.prototype.getUserProperties = function () {
        return tslib_1.__assign({}, this._properties);
    };
    Identify.prototype.set = function (property, value) {
        this._safeSet(analytics_types_1.IdentifyOperation.SET, property, value);
        return this;
    };
    Identify.prototype.setOnce = function (property, value) {
        this._safeSet(analytics_types_1.IdentifyOperation.SET_ONCE, property, value);
        return this;
    };
    Identify.prototype.append = function (property, value) {
        this._safeSet(analytics_types_1.IdentifyOperation.APPEND, property, value);
        return this;
    };
    Identify.prototype.prepend = function (property, value) {
        this._safeSet(analytics_types_1.IdentifyOperation.PREPEND, property, value);
        return this;
    };
    Identify.prototype.postInsert = function (property, value) {
        this._safeSet(analytics_types_1.IdentifyOperation.POSTINSERT, property, value);
        return this;
    };
    Identify.prototype.preInsert = function (property, value) {
        this._safeSet(analytics_types_1.IdentifyOperation.PREINSERT, property, value);
        return this;
    };
    Identify.prototype.remove = function (property, value) {
        this._safeSet(analytics_types_1.IdentifyOperation.REMOVE, property, value);
        return this;
    };
    Identify.prototype.add = function (property, value) {
        this._safeSet(analytics_types_1.IdentifyOperation.ADD, property, value);
        return this;
    };
    Identify.prototype.unset = function (property) {
        this._safeSet(analytics_types_1.IdentifyOperation.UNSET, property, constants_1.UNSET_VALUE);
        return this;
    };
    Identify.prototype.clearAll = function () {
        // When clear all happens, all properties are unset. Reset the entire object.
        this._properties = {};
        this._properties[analytics_types_1.IdentifyOperation.CLEAR_ALL] = constants_1.UNSET_VALUE;
        return this;
    };
    // Returns whether or not this set actually worked.
    Identify.prototype._safeSet = function (operation, property, value) {
        if (this._validate(operation, property, value)) {
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
            var userPropertyMap = this._properties[operation];
            if (userPropertyMap === undefined) {
                userPropertyMap = {};
                // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
                this._properties[operation] = userPropertyMap;
            }
            // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
            userPropertyMap[property] = value;
            this._propertySet.add(property);
            return true;
        }
        return false;
    };
    Identify.prototype._validate = function (operation, property, value) {
        if (this._properties[analytics_types_1.IdentifyOperation.CLEAR_ALL] !== undefined) {
            // clear all already set. Skipping operation;
            return false;
        }
        if (this._propertySet.has(property)) {
            // Property already used. Skipping operation
            return false;
        }
        if (operation === analytics_types_1.IdentifyOperation.ADD) {
            return typeof value === 'number';
        }
        if (operation !== analytics_types_1.IdentifyOperation.UNSET && operation !== analytics_types_1.IdentifyOperation.REMOVE) {
            return (0, valid_properties_1.isValidProperties)(property, value);
        }
        return true;
    };
    return Identify;
}());
exports.Identify = Identify;
//# sourceMappingURL=identify.js.map