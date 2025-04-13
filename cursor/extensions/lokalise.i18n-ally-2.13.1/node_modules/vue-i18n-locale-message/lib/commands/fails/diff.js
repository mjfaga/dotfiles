"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.fail = exports.DiffError = void 0;
const fail_1 = __importDefault(require("./fail"));
class DiffError extends Error {
}
exports.DiffError = DiffError;
exports.fail = fail_1.default(DiffError, 64 /* Difference */);
exports.default = {
    DiffError,
    fail: exports.fail
};
