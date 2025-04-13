Object.defineProperty(exports, "__esModule", { value: true });
exports.Revenue = void 0;
var tslib_1 = require("tslib");
var analytics_types_1 = require("@amplitude/analytics-types");
var valid_properties_1 = require("./utils/valid-properties");
var Revenue = /** @class */ (function () {
    function Revenue() {
        this.productId = '';
        this.quantity = 1;
        this.price = 0.0;
    }
    Revenue.prototype.setProductId = function (productId) {
        this.productId = productId;
        return this;
    };
    Revenue.prototype.setQuantity = function (quantity) {
        if (quantity > 0) {
            this.quantity = quantity;
        }
        return this;
    };
    Revenue.prototype.setPrice = function (price) {
        this.price = price;
        return this;
    };
    Revenue.prototype.setRevenueType = function (revenueType) {
        this.revenueType = revenueType;
        return this;
    };
    Revenue.prototype.setRevenue = function (revenue) {
        this.revenue = revenue;
        return this;
    };
    Revenue.prototype.setEventProperties = function (properties) {
        if ((0, valid_properties_1.isValidObject)(properties)) {
            this.properties = properties;
        }
        return this;
    };
    Revenue.prototype.getEventProperties = function () {
        var eventProperties = this.properties ? tslib_1.__assign({}, this.properties) : {};
        eventProperties[analytics_types_1.RevenueProperty.REVENUE_PRODUCT_ID] = this.productId;
        eventProperties[analytics_types_1.RevenueProperty.REVENUE_QUANTITY] = this.quantity;
        eventProperties[analytics_types_1.RevenueProperty.REVENUE_PRICE] = this.price;
        eventProperties[analytics_types_1.RevenueProperty.REVENUE_TYPE] = this.revenueType;
        eventProperties[analytics_types_1.RevenueProperty.REVENUE] = this.revenue;
        return eventProperties;
    };
    return Revenue;
}());
exports.Revenue = Revenue;
//# sourceMappingURL=revenue.js.map