export var returnWrapper = function (awaitable) { return ({
    promise: awaitable || Promise.resolve(),
}); };
//# sourceMappingURL=return-wrapper.js.map