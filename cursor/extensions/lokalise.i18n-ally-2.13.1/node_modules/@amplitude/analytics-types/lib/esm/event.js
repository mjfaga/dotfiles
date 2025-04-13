export var IdentifyOperation;
(function (IdentifyOperation) {
    // Base Operations to set values
    IdentifyOperation["SET"] = "$set";
    IdentifyOperation["SET_ONCE"] = "$setOnce";
    // Operations around modifying existing values
    IdentifyOperation["ADD"] = "$add";
    IdentifyOperation["APPEND"] = "$append";
    IdentifyOperation["PREPEND"] = "$prepend";
    IdentifyOperation["REMOVE"] = "$remove";
    // Operations around appending values *if* they aren't present
    IdentifyOperation["PREINSERT"] = "$preInsert";
    IdentifyOperation["POSTINSERT"] = "$postInsert";
    // Operations around removing properties/values
    IdentifyOperation["UNSET"] = "$unset";
    IdentifyOperation["CLEAR_ALL"] = "$clearAll";
})(IdentifyOperation || (IdentifyOperation = {}));
export var RevenueProperty;
(function (RevenueProperty) {
    RevenueProperty["REVENUE_PRODUCT_ID"] = "$productId";
    RevenueProperty["REVENUE_QUANTITY"] = "$quantity";
    RevenueProperty["REVENUE_PRICE"] = "$price";
    RevenueProperty["REVENUE_TYPE"] = "$revenueType";
    RevenueProperty["REVENUE"] = "$revenue";
})(RevenueProperty || (RevenueProperty = {}));
/**
 * Strings that have special meaning when used as an event's type
 * and have different specifications.
 */
export var SpecialEventType;
(function (SpecialEventType) {
    SpecialEventType["IDENTIFY"] = "$identify";
    SpecialEventType["GROUP_IDENTIFY"] = "$groupidentify";
    SpecialEventType["REVENUE"] = "revenue_amount";
})(SpecialEventType || (SpecialEventType = {}));
//# sourceMappingURL=event.js.map